from flask import Flask, render_template, request, redirect, url_for, flash, session
from forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import Users
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'CHANGE_THIS_TO_ENV_VAR'

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.getUserById(user_id)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = request.form.get("username")
        password = request.form.get("password")
        user = Users.getUserByName(username)
        if user and not check_password_hash(user.password,password):
            user = None
        if user: #AUTHENTICATED
            login_user(user)
            #TODO: get last session instead
            return redirect('/')
    return render_template('login.html', form=form)

@app.route('/signout')
def signout():
    if current_user.is_authenticated:
        logout_user()
    return redirect('/')   

@app.route('/signup', methods=['GET','POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        username = request.form.get("username")
        password = request.form.get("password")
        hashedpass = generate_password_hash(password, method="pbkdf2:sha256")
        email = request.form.get('email')
        if not Users.createUser(username,email,hashedpass):
            print("user not made")
            return render_template('signup.html', form=form)
        user = Users.getUserByName(username)
        login_user(user)
        #TODO: get last session
        return redirect('/')
    return render_template('signup.html', form=form)

@app.route("/")
def index():
    # Define garage size and base price
    GARAGE_SIZE = 100
    BASE_PRICE = 10

    # Initialize parking spots with random availability for demonstration
    parking_spots = [
        {"id": i, "available": random.choice([True, False])} for i in range(GARAGE_SIZE)
    ]

    # Calculate dynamic pricing based on the position of the spot in the garage
    for spot in parking_spots:
        distance_from_top = spot["id"]  # Distance from the top of the garage
        price_multiplier = 1 + (
            distance_from_top / GARAGE_SIZE
        )  # Higher distance -> higher price
        spot["price"] = round(BASE_PRICE * price_multiplier, 2)

    user = current_user.username if current_user.is_authenticated else None #TODO change this to their actual name


    return render_template("index.html", parking_spots=parking_spots, user=user)


if __name__ == "__main__":
    app.run(debug=True)
