from flask import Flask, render_template, request, redirect, url_for, flash, session
from forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
from models import Garage, ParkingSpace, session
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from models import Users
import random

app = Flask(__name__)
app.config["SECRET_KEY"] = "CHANGE_THIS_TO_ENV_VAR"

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "signup"

@login_manager.user_loader
def load_user(user_id):
    return Users.getUserById(user_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = request.form.get("username")
        password = request.form.get("password")
        user = Users.getUserByName(username)
        if user and not check_password_hash(user.password, password):
            user = None
        if user:  # AUTHENTICATED
            login_user(user)
            # TODO: get last session instead
            return redirect("/")
    return render_template("login.html", form=form)


@app.route("/signout")
def signout():
    if current_user.is_authenticated:
        logout_user()
    return redirect("/")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        username = request.form.get("username")
        password = request.form.get("password")
        hashedpass = generate_password_hash(password, method="pbkdf2:sha256")
        email = request.form.get("email")
        if not Users.createUser(username, email, hashedpass):
            print("user not made")
            return render_template("signup.html", form=form)
        user = Users.getUserByName(username)
        login_user(user)
        # TODO: get last session
        return redirect("/")
    return render_template("signup.html", form=form)


@app.route("/")
def index():
    parking_spots = Garage.getAllSpots()

    user = current_user.username if current_user.is_authenticated else None #TODO change this to their actual name

        user = (
            request.args.get("user") if request.args.get("user") else None
        )  # Get user name from query parameters

        return render_template("index.html", parking_spots=parking_spots, user=user)

@app.route('/reserve/<i>')
@login_required
def reserve(i):
    Users.userReserveSpot(current_user.id,i)
    Garage.reserveSpot(i)
    return redirect(url_for("cart"))

@app.route('/cart')
@login_required
def cart():
    spot = None
    if current_user.reserved != -1:
        spot = Garage.getSpotById(current_user.reserved).__dict__
    return render_template('cart.html', spot=spot)


@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    # Implement logic to process the checkout
    # For example, handle payment, update database, etc.
    return "Checkout successful! Thank you for shopping with us."

if __name__ == "__main__":
    app.run(debug=True)
