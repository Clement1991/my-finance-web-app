-- Drop tables
DROP TABLE IF EXISTS "users";
DROP TABLE IF EXISTS "transactions";

-- Drop Index
DROP INDEX IF EXISTS "username";

-- Create Tables
CREATE TABLE "users" (
    "id" INTEGER,
    "username" TEXT NOT NULL,
    "hash" TEXT NOT NULL,
    "cash" NUMERIC NOT NULL DEFAULT 10000.00,
    PRIMARY KEY("id")
);


CREATE TABLE "transactions" (
    "id" INTEGER,
    "user_id" INTEGER,
    "symbol" TEXT NOT NULL,
    "shares" INT NOT NULL,
    "price" FLOAT NOT NULL,
    "type" NOT NULL,
    "date" NUMERIC NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY("id")
);

CREATE UNIQUE INDEX "username" ON "users" ("username");
