# FINANCE WEB APPLICATION

By Clement Gyasi Siaw

Video overview: <>

## Scope

This project is a finance web app via which users can manage portfolios of stocks. They can check real stocks’ actual prices and portfolios’ values and can also “buy” and "sell" stocks by querying for stocks’ prices.

## Running

In vs-code navigate to the root directory and create a virtual environment (venv) and activate the venv depending on the operating system. In the same root directory run `sqlite3 finance.db` to open finance.db with sqlite3. When you run `.schema ` in the SQLite prompt, finance.db comes with `users` and `transactions` tables. From the `users` table, by default, new users will receive $10,000 in cash. After running `flask run` in the terminal, open the link given in a browser to access the web application.

## Understanding

### app.py

Atop `app.py` are a bunch of imports, among them is Havard's CS50’s SQL module and a few helper functions. Other imports include `generate_password_hash` from `werkzeug.security` used for generating hashed passwords of users.
After configuring Flask, this file disables caching of responses, else the browser will not notice any changes made to the file. It then further configures Flask to store sessions on the local filesystem (i.e., disk) as opposed to storing them inside of (digitally signed) cookies, which is Flask’s default. The file then configures CS50’s SQL module to use finance.db which is a SQlite database. After that, there are a number of routes which will be discussed later in detail.

### helpers.py

Next, lets take a look at `helpers.py`. There’s the implementation of `apology` which is used to deny the user access to other routes when certain conditions in the current route are not met. It takes two arguments: `message`, which is passed to render_template as the value of bottom, and, optionally, `code`, which is passed to render_template as the value of top. 
This file also contains the `login_required` function. The function is used to automatically direct users to the login route if the user has not logged in or after a user logs out of the app. 
Thereafter is `lookup`, a function that, given a symbol (e.g., NFLX for Netflix, AAPL for Apple etc.), returns a stock quote for a company in the form of a dict with three keys: `name`, whose value is a str, the name of the company; `price`, whose value is a float; and `symbol`, whose value is a str, a canonicalized (uppercase) version of a stock’s symbol, irrespective of how that symbol was capitalized when passed into `lookup`.


### requirements.txt

That file simply prescribes the packages on which this app depends.

### static/

Contains `style.css` where some initial CSS lives.

### templates/

The templates folder contains all templates used to build the web app, stylized with Bootstrap. `layout.html` is the base template to which all other templates are linked. It defines a block, `main`, inside of which all templates shall go. It also includes support for Flask’s message flashing so that messages can be relayed from one route to another for the user to see. The other templates will be discussed in great detail later in this report.

### schema.sql

This files contains the schema and all other entities of the database. You can reset the database by running `.read schema.sql` in sqlite3.

### finance.db

This is the databse which contains all the relevant tables which will be used to manage all the data of the web application.

## Specification

### register.py and register.html

The `/register` route in `app.py` allows a user to register for an account via `register.html`. The user is required to complete all fields. An `apology` is rendered if the user’s input is blank, invalid or if the username already exists. Users' account information is stored on the `users` table in the database.

### login.py and login.html

The `/login` route is used to log users into their account via `login.html`. Validation is done to ensure that, the username and password provided by the user exists in the database. If a user's record exists, the user is successfully logged into their account and directed to the root directory `index.html`, which at this stage, will contain a table with no data until a user buys or sells shares. The user's `id` from the database is then stored in Flask's `session` for identification.

### /quote and quote.html

The `/quote` route via `quote.html` allows a user to look up a stock’s current price using the `lookup` function. The user submits a stock’s symbol and the result is displayed in `quoted.html`. The result includes the name, stock symbol and stock price of the company. If the stock symbol does not exist, `apology` is rendered.

### /buy and buy.html

A user is required to input a stock `symbol` and the number of shares they want to buy. Apology is rendered if the symbol field is blank or if the stock symbol does not exist. If the `shares` field is blank or not a positive integer, apology is also rendered. If the user cannot afford the number of shares at the current price, that is, if total stock value exceeds the amount of `cash` in the user's account, apology is rendered. After a succesful `buy`, this transaction information is stored in the `transactions` table in the database. 


### /index and index.html

`/index` displays an html table via `index.html`. This table summarises which stocks the user owns, the numbers of shares owned, the current price of each stock, and the total value of each holding (i.e., shares times price). It also displays the user’s current cash balance along with a grand total (i.e., stocks’ total value plus cash).

### /sell and sell.html

A user can only sell shares of a stock that he or she owns. The user chooses the stock symbol and inputs the number of shares they want to sell and submits via POST to `/sell`. If no symbol is chosen or the number of shares is not a positive integer, `apolopy` is rendered. Apology is also rendered if the user attempts to sell more shares of a stock than he or she owns. The sell transation is also recorded in the `transactions` table

### /history and history.html

The `/history` route through `history.html` displays an HTML table summarizing all of a user’s transactions ever, listing row by row, every buy and every sell. Each row includes the type of transaction (whether a stock was bought or sold), the stock’s symbol, the (purchase or sale) price, the number of shares bought or sold, and the date and time at which the transaction occurred.


### /logout

This route logs out users from their account by clearing Flask's `session`. They are then redirected back to the login page.