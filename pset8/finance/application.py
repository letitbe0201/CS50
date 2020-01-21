import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


# route for index
@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # get the buying record from the transaction database
    userOwn = db.execute("SELECT userId, symbol, sellbuy, SUM(shares) FROM trans WHERE userId=:userId AND sellbuy='B' GROUP BY symbol ORDER BY symbol;",
                         userId=session["user_id"])
    # get the selling record from the transaction database
    userSell = db.execute("SELECT userId, symbol, sellbuy, SUM(shares) FROM trans WHERE userId=:userId AND sellbuy='S' GROUP BY symbol;",
                          userId=session["user_id"])
    # get the user info
    user = db.execute("SELECT id, username, cash FROM users WHERE id=:userId;", userId=session["user_id"])
    # for initializing total money = cash + stock
    money = user[0]["cash"]
    # calculate the actual shares of the stock
    for rowO in userOwn:
        for rowS in userSell:
            if rowO["symbol"] == rowS["symbol"]:
                # total shares here
                rowO["SUM(shares)"] = rowO["SUM(shares)"] - rowS["SUM(shares)"]

    # find out the current and total price of certain stock of the user
    for rowO in userOwn:
        if rowO["SUM(shares)"] > 0:
            symbol = lookup(rowO["symbol"])
            # put the value of price and total into the list userOwn
            rowO["price"] = symbol["price"]
            rowO["total"] = symbol["price"] * rowO["SUM(shares)"]
            # put the value of name into the list userOwn
            rowO["companyName"] = symbol["name"]
            # for calculating total money = cash + stock
            money = money + rowO["total"]
            # transform the format of money
            rowO["price"] = usd(rowO["price"])
            rowO["total"] = usd(rowO["total"])
    # transform the format of money
    money = usd(money)
    user[0]["cash"] = usd(user[0]["cash"])

    return render_template("index.html", userOwn=userOwn, user=user, money=money)


# route for buying shares of stock
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == 'POST':
        # Ensure the symbol was submitted
        if not request.form.get("symbol"):
            return apology("Must provide symbol", 400)
        # get the info of stock
        symbolBought = lookup(request.form.get("symbol"))
        # make sure it's a valid symbol
        if symbolBought is None:
            return apology("Invalid symbol", 400)
        # make sure the input number of shares is a positive integer
        try:
            shares = int(request.form.get("shares"))
            if shares < 0:
                return apology("Shares must be a positive number!", 400)
        except ValueError:
            return apology("Invalid shares!", 400)
        except:
            return apology("Error", 403)

        # process the "buying"
        user = db.execute("SELECT * FROM users WHERE id = :userId", userId=session["user_id"])
        # if the user doesn't have enough money to buy the stock
        if user[0]["cash"] < (symbolBought["price"] * shares):
            return apology("Can't afford!", 400)
        # calculate the amount of cash left and update it to the database
        user[0]["cash"] = user[0]["cash"] - (symbolBought["price"] * shares)
        db.execute("UPDATE users SET cash = :cash WHERE id = :userId", cash=user[0]["cash"],
                   userId=session["user_id"])
        # Update the info of transaction to table "trans"
        db.execute("INSERT INTO trans (userId, symbol, price, shares, total, sellbuy) VALUES(:userId, :symbol, :price, :shares, :total, :sellbuy)",
                   userId=session["user_id"], symbol=symbolBought["symbol"], price=symbolBought["price"], shares=shares,
                   total=(symbolBought["price"] * shares), sellbuy='B')

        # flashing the message on route /
        flash('BOUGHT!')

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    username = request.args.get("username")
    # ensure the username length is at least one
    if not username:
        return jsonify(False)

    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
    # if the len(rows)!=0, which means the username has been registered, then return false
    if len(rows) != 0:
        return jsonify(False)
    else:
        return jsonify(True)


# route for transaction record
@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # get the history of the user
    records = db.execute("SELECT symbol, sellbuy, price, shares, total, TIME FROM trans WHERE userId=:userId ORDER BY TIME;",
                         userId=session["user_id"])
    # change the format of price and total
    for record in records:
        record["price"] = usd(record["price"])
        record["total"] = usd(record["total"])

    return render_template("history.html", records=records)


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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
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


# route for quote
@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        # Ensure the symbol was submitted
        if not request.form.get("symbol"):
            return apology("Missing Symbol!", 400)
        # implement the function lookup to search the info of that symbol
        symbolAsked = lookup(request.form.get("symbol"))
        # validate the symbol
        if symbolAsked is None:
            return apology("Invalid Symbol!", 400)
        # change the format of the price
        symbolAsked["price"] = usd(symbolAsked["price"])

        return render_template("quoted.html", symbolAsked=symbolAsked)
    else:
        return render_template("quote.html")


# route for registeration
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        # if not request.form.get("username"):################
            # return apology("Must provide username!", 403)
        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("Must provide password!", 400)
        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("Retype the password for confirmation!", 400)
        # Ensure the password matches the confirmation
        elif not (request.form.get("password") == request.form.get("confirmation")):
            return apology("Passwords don't match!", 400)

        # insert the info of user into the database
        db.execute("INSERT INTO users (username, hash, cash) VALUES(:username, :password, :cash)",
                   username=request.form.get("username"),
                   password=generate_password_hash(request.form.get("password")), cash=10000)

        # Query database for username again to remember
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # flashing the message on route /
        flash('REGISTERED!')

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


# route for selling shares of stock
@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == 'POST':

        # get the user info
        user = db.execute("SELECT id, username, cash FROM users WHERE id=:userId;", userId=session["user_id"])

        # get the info of stock the user has
        # get the buying record from the transaction database
        userOwn = db.execute("SELECT userId, symbol, sellbuy, SUM(shares) FROM trans WHERE userId=:userId AND sellbuy='B' GROUP BY symbol ORDER BY symbol;",
                             userId=session["user_id"])
        # get the selling record from the transaction database
        userSell = db.execute("SELECT userId, symbol, sellbuy, SUM(shares) FROM trans WHERE userId=:userId AND sellbuy='S' GROUP BY symbol;",
                              userId=session["user_id"])
        # calculate the actual shares of the stock
        for rowO in userOwn:
            for rowS in userSell:
                if rowO["symbol"] == rowS["symbol"]:
                    # total shares here
                    rowO["SUM(shares)"] = rowO["SUM(shares)"] - rowS["SUM(shares)"]

        # Error checking
        # Ensure the symbol was submitted
        if not request.form.get("symbol"):
            return apology("Must provide symbol", 400)
        # get the info of stock
        symbolSell = lookup(request.form.get("symbol"))
        # make sure it's a valid symbol
        if symbolSell is None:
            return apology("Invalid symbol", 400)
        # make sure the input number of shares is a positive integer
        try:
            shares = int(request.form.get("shares"))
            if shares < 0:
                return apology("Shares must be a positive number!", 400)
        except ValueError:
            return apology("Invalid shares!", 400)
        except:
            return apology("Error", 403)
        # make sure the user has enough shares of that stock to sell
        for rowO in userOwn:
            if rowO["symbol"] == request.form.get("symbol"):
                if rowO["SUM(shares)"] - shares < 0:
                    return apology("Not enough shares to sell", 400)

        # process the "selling"
        # calculate the amount of cash earn and update it to the database
        user[0]["cash"] = user[0]["cash"] + (symbolSell["price"] * shares)
        db.execute("UPDATE users SET cash = :cash WHERE id = :userId", cash=user[0]["cash"], userId=session["user_id"])
        # Update the info of transaction to table "trans"
        db.execute("INSERT INTO trans (userId, symbol, price, shares, total, sellbuy) VALUES(:userId, :symbol, :price, :shares, :total, :sellbuy)",
                   userId=session["user_id"], symbol=symbolSell["symbol"], price=symbolSell["price"], shares=shares,
                   total=(symbolSell["price"] * shares), sellbuy='S')

        # flashing the message on route /
        flash('SOLD!')

        # Redirect user to home page
        return redirect("/")

    else:

        # get the info of stock the user has
        # get the buying record from the transaction database
        userOwn = db.execute("SELECT userId, symbol, sellbuy, SUM(shares) FROM trans WHERE userId=:userId AND sellbuy='B' GROUP BY symbol ORDER BY symbol;",
                             userId=session["user_id"])
        # get the selling record from the transaction database
        userSell = db.execute("SELECT userId, symbol, sellbuy, SUM(shares) FROM trans WHERE userId=:userId AND sellbuy='S' GROUP BY symbol;",
                              userId=session["user_id"])
        # calculate the actual shares of the stock
        for rowO in userOwn:
            for rowS in userSell:
                if rowO["symbol"] == rowS["symbol"]:
                    # total shares here
                    rowO["SUM(shares)"] = rowO["SUM(shares)"] - rowS["SUM(shares)"]

        return render_template("sell.html", userOwn=userOwn)


# route for changing the passwords
@app.route("/changePassword", methods=["GET", "POST"])
@login_required
def changePassword():
    """Let the user changes passwords"""
    if request.method == 'POST':

        # Query database for username
        user = db.execute("SELECT * FROM users WHERE id = :userId", userId=session["user_id"])
        # ensure the old passwords are correctly submitted
        if not request.form.get("oldPassword") or not check_password_hash(user[0]["hash"], request.form.get("oldPassword")):
            return apology("Wrong passwords!", 400)
        elif not request.form.get("newPassword"):
            return apology("Invalid new passwords!", 400)
        elif request.form.get("newPassword") != request.form.get("confirmation"):
            return apology("New passwords don\'t match!", 400)

        # replace the old with new passwords
        db.execute("UPDATE users SET hash = :newHash WHERE id = :userId",
                   newHash=generate_password_hash(request.form.get("newPassword")), userId=session["user_id"])

        # flashing the message on route /
        flash('Password changed!')

        return redirect("/")

    else:
        return render_template("changePassword.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
