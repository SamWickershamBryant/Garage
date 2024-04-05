from flask import Flask, render_template, request, redirect, url_for, flash, session
import stripe
from datetime import datetime
from forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
from models import Garages, ParkingSpace, session
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from models import Users

app = Flask(__name__, static_url_path="", static_folder="templates")
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
    garages = Garages.getAllGarages()

    user = (
        current_user.username if current_user.is_authenticated else None
    )  # TODO change this to their actual name

    return render_template("index.html", garages=garages, user=user)


@app.route("/garage/<int:garage_id>")
#@login_required
def garage_parking_spaces(garage_id):
    garage = Garages.getGarageById(garage_id)
    if garage is None:
        # Handle garage not found
        return "404", 404

    parking_spaces = Garages.getSpacesbyGarageID(garage_id)
    return render_template(
        "garage.html", garage=garage, parking_spaces=parking_spaces
    )


@app.route("/parking_space/<int:parking_space_id>")
#@login_required
def parking_space_detail(parking_space_id):
    parking_space = Garages.getSpotById(parking_space_id)
    
    if parking_space is None:
        # Handle parking space not found
        return "404", 404
    
    garage = Garages.getGarageById(parking_space.garage_id)

    return render_template("parkingspace.html", parking_space=parking_space, garage=garage)


@app.route("/reserve/<i>")
#@login_required
def reserve(i):
    Users.userReserveSpot(current_user.id, i)
    Garages.reserveSpot(i)
    return redirect(url_for("cart"))


@app.route("/cart")
#@login_required
def cart():
    spot = None
    if current_user.reserved != -1:
        spot = Garages.getSpotById(current_user.reserved).__dict__
    return render_template("cart.html", spot=spot)


stripe.api_key = "sk_test_51P0z0dCLh6RFSyLpgMa9qsm0QjzUybS1Yo7Bf3nDR8ZJ1EE0xa0T4FH8eGOLdZPQ1TEmQfXN23wCXG5xkr5DHPsc00ytAKga1q"

current_time = datetime.now().hour
cutoff_hour = 17 

@app.route('/create-checkout-session',methods=["GET", 'POST'])
def create_checkout_session():
    YOUR_DOMAIN = request.host_url[:-1]
    try:
        if current_time >= cutoff_hour:
            checkout_session = stripe.checkout.Session.create(
                line_items = [
                    {
                        'price': 'price_1P1xTpCLh6RFSyLpWGjh88ZC',
                        'quantity': 1
                    }
                ],
                mode="payment",
                success_url=YOUR_DOMAIN + "/success.html",
                cancel_url=YOUR_DOMAIN + "/cancel.html"
            )
        else:
            checkout_session = stripe.checkout.Session.create(
                line_items = [
                    {
                        'price': 'price_1P1zcMCLh6RFSyLpk0kapij1',
                        'quantity': 1
                    }
                ],
                mode="payment",
                success_url=YOUR_DOMAIN + "/success.html",
                cancel_url=YOUR_DOMAIN + "/cancel.html"
            )

    except Exception as e:
        return str(e)
    
    return redirect(checkout_session.url, code=303)


if __name__ == "__main__":
    app.run(debug=True)
