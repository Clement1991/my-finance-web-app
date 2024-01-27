import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

import datetime

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    user_id = session["user_id"]

    # Get the user's stock and shares
    stocks = db.execute(
        "SELECT symbol, SUM(shares) AS total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING total_shares > 0",
        user_id,
    )

    # Get user's cash balance
    cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    cash = cash_db[0]["cash"]

    # Initialize variables for total values
    total_value = cash

    # Iterate over stocks and add price and total value
    for stock in stocks:
        quote = lookup(stock["symbol"])
        stock["name"] = quote["name"]
        stock["price"] = quote["price"]
        stock["value"] = stock["price"] * stock["total_shares"]
        total_value += stock["value"]

    return render_template(
        "index.html",
        stocks=stocks,
        cash=cash,
        total_value=total_value,
    )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    user_id = session["user_id"]

    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")

        if not symbol:
            return apology("Must provide symbol")

        elif not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("Must provide a positive integer number of shares")

        quote = lookup(symbol)

        if quote == None:
            return apology("Symbol does not exist")

        price = quote["price"]
        total_cost = int(shares) * price

        cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        cash = cash_db[0]["cash"]

        if cash < total_cost:
            return apology("Not enough money in account")

        updated_cash = cash - total_cost

        # Update the users table
        db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_cash, user_id)

        # Update the purchase to the history table
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price, type) VALUES(?, ?, ?, ?, ?)",
            user_id,
            symbol,
            shares,
            price,
            "Bought"
        )

        flash(f"Bought {shares} shares of {symbol} for {usd(total_cost)}!")
        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    user_id = session["user_id"]

    # Query database for user's transactions, ordered by most recent first
    transactions = db.execute(
        "SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC", user_id
    )

    # Rend history page with transactions
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":
        symbol = request.form.get("symbol")
        quote = lookup(symbol.upper())

        if not quote:
            return apology("Invalid symbol", 400)

        return render_template("quoted.html", quote=quote)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # If user reached route via POST
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username is submitted
        if not username:
            flash("Please enter username")

        # Ensure password is submitted
        elif not password:
            return apology("must provide password", 400)

        # Ensure password confirmation is submitted
        elif not confirmation:
            return apology("must provide confirmation", 400)

        # Ensure password and confirmation match
        elif password != confirmation:
            return apology("Passwords do not match", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username does not already exit
        if len(rows) != 0:
            return apology("Username already exists", 400)

        # Convert entered password into hashses
        hash = generate_password_hash(password)

        # Insert new user into database
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        # Query database for newly inserted user
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Redirect user to homepage
        return redirect("/")

    # If user reached route via GET
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of quote"""

    user_id = session["user_id"]

    # Get user's stocks
    stocks = db.execute(
        "SELECT symbol, SUM(shares) AS total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING total_shares > 0",
        user_id,
    )

    # If user submits the form
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        if not symbol:
            return apology("Must Give Symbol")

        if not shares or shares < 1:
            return apology("Invalid shares")

        for stock in stocks:
            if stock["symbol"] == symbol:
                if stock["total_shares"] < shares:
                    return apology("Not enough shares")
                else:
                    # Get quote
                    quote = lookup(symbol.upper())
                    if quote == None:
                        return apology("Symbol not found")
                    price = quote["price"]
                    total_sale = shares * price

                    # Update users table
                    cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
                    cash = cash_db[0]["cash"]
                    db.execute(
                        "UPDATE users SET cash = ? WHERE id = ?",
                        (cash + total_sale),
                        user_id,
                    )


                    # Add the sale to the history table
                    db.execute(
                        "INSERT INTO transactions (user_id, symbol, shares, price, type) VALUES(?, ?, ?, ?, ?)",
                        user_id,
                        symbol,
                        ((-1) * shares),
                        price,
                        "Sold",
                    )

                    flash(f"Sold {shares} shares of {symbol} for {usd(total_sale)}!")
                    return redirect("/")

        return apology("Symbol not found")

    else:
        return render_template("sell.html", stocks=stocks)
