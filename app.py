from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, url_for, abort
import stripe, os
from datetime import datetime
from forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
from models import Garages, ParkingSpace, Vehicles, session
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from models import Users
from flask import Flask

app = Flask(__name__, static_url_path="", static_folder="templates")
app = Flask(__name__, static_url_path='/static')
app.config["SECRET_KEY"] = "CHANGE_THIS_TO_ENV_VAR"
app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51P0z0dCLh6RFSyLp0AONn5FZKjTzYGQj2hnuQTVrY8DYm7fH1sDjl21nX9yK4r2wltposTYnijV0sC86GhQa90xP00ZvcfWQgo'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51P0z0dCLh6RFSyLpgMa9qsm0QjzUybS1Yo7Bf3nDR8ZJ1EE0xa0T4FH8eGOLdZPQ1TEmQfXN23wCXG5xkr5DHPsc00ytAKga1q'
stripe.api_key = app.config['STRIPE_SECRET_KEY']

YOUR_DOMAIN = 'http://127.0.0.1:5000'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "signup"

def getUser():
    return current_user.username if current_user.is_authenticated else None
    
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

@app.route('/protected')
def protected():
    if not current_user.is_authenticated:
        session['next'] = request.url
        return redirect(url_for('login'))
    return render_template('/')

@login_manager.user_loader
def load_user(user_id):
    return Users.getUserById(user_id)

@app.route("/", methods=['GET', 'POST'])
def index():
    garages = Garages.getAllGarages()

    return render_template("index.html", garages=garages, user=getUser())

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():

        username = request.form.get("username")
        password = request.form.get("password")
        user = Users.getUserByName(username)
        if user and not check_password_hash(user.password, password):
            user = None
            flash('Incorrect username/password.', 'error')
        if user:  # AUTHENTICATED
            login_user(user, remember=True)
            return redirect("/")
    return render_template("login.html", form=form, user=current_user)


@app.route("/logout")
@login_required
def signout():
    if current_user.is_authenticated:
        logout_user()
    return redirect("/login")


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
        login_user(user, remember=True)
        # TODO: get last session
        return redirect("/")
    return render_template("signup.html", form=form)


@app.route('/search', methods=['GET'])
def search():
    location = request.args.get('location')
    print("Location:", location)

    search_results = Garages.searchGaragesByLocation(location)
    return render_template('garages_list.html', search_results=search_results)
    


@app.route("/garages_list")
@login_required
def garage_list():
    garages = Garages.getAllGarages()

    return render_template("garages_list.html", garages=garages)


@app.route("/garage/<int:garage_id>")
@login_required
def garage_parking_spaces(garage_id):
    garage = Garages.getGarageById(garage_id)
    if garage is None:
        # Handle garage not found
        return "404", 404

    parking_spaces = Garages.getSpacesbyGarageID(garage_id)
    return render_template(
        "garage.html", garage=garage, parking_spaces=parking_spaces, user=getUser()
    )


@app.route("/parking_space/<int:parking_space_id>")
@login_required
def parking_space_detail(parking_space_id):
    parking_space = Garages.getSpotById(parking_space_id)
    
    if parking_space is None:
        # Handle parking space not found
        return "404", 404
    
    garage = Garages.getGarageById(parking_space.garage_id)

    return render_template("parkingspace.html", parking_space=parking_space, garage=garage, user=getUser())


@app.route("/reserve_spot/<int:garage_id>", methods=['GET','POST'])
@login_required
def reserve(garage_id):
    reservation_date = request.form.get("reservation_date")
    all_spots = Garages.getAllSpots()
    print("spots: ", all_spots)
    available_spot = Garages.getAvailableSpot(garage_id)
    #space = Garages.getSpotById(available_spot)

    print("Current User:", current_user)  # Print current_user object
    print("Reservation Date:", reservation_date)
    print("Reserved Spot:", available_spot)

    reserved_spot = Garages.reserveSpot(available_spot, reservation_date)
    print("Reserved Spot:", reserved_spot)
    if reserved_spot:
        Users.userReserveSpot(current_user.id, reserved_spot.id)
        print("Reserved Spot:", reserved_spot)
    else:
        flash("Failed to reserve spot.", "error")

    return redirect(url_for("cart"))


@app.route("/cart")
@login_required
def cart():
    spot = None
    reservation_id = current_user.reserved
    if reservation_id != -1:
        reserved_spot = Garages.getSpotById(reservation_id)
        if reserved_spot:
            spot = reserved_spot.__dict__
            # session['spot.number'] = space
            # session['spot.price'] = price
            # session['reservation_date'] = price


    return render_template("cart.html", spot=spot, user=getUser())

current_time = datetime.now().hour
cutoff_hour = 17 

# @app.route('/update_profile', methods=['POST'])
# @login_required
# def update_profile():
#     user_id = current_user.id
#     current_password = request.form.get('current_password')
#     new_email = request.form.get('email')
#     new_username = request.form.get('username')
#     new_password = request.form.get('password')
#     confirm_password = request.form.get('confirm_password')

#     users = Users()

#     if not users.verify_password(user_id, current_password):
#         if new_password != confirm_password:
#             flash('Passwords do not match. Try again.', 'error')
#             return redirect('/update_profile')
#         users.updateUserDetails(user_id, new_email=new_email, new_username=new_username, new_password=new_password)
#         flash('Profile updated successfully', 'success')
#     else:
#         flash('Incorrect current password. Try again.', 'error')
#     # Redirect or render a response
#     return render_template('account.html')

# @app.route('/update_profile', methods=['GET','POST'])
# @login_required
# def update_profile():
#     user_id = current_user.id
#     current_password = request.form.get('current_password')
#     new_email = request.form.get('email')
#     new_username = request.form.get('username')
#     new_password = request.form.get('password')
#     confirm_password = request.form.get('confirm_password')

#     users = Users()

#     if not users.verify_password(user_id, current_password):
#         flash('Incorrect current password. Try again.', 'error')
#         return redirect(url_for('update_profile'))

#     if new_password != confirm_password:
#         flash('Passwords do not match. Try again.', 'error')
#         return redirect(url_for('update_profile'))

#     users.updateUserDetails(user_id, new_email=new_email, new_username=new_username, new_password=new_password)
#     flash('Profile updated successfully', 'success')

#     # Redirect to the account page or any other appropriate page
#     return redirect(url_for('account'))

@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if request.method == 'GET':
        # Fetch current user's details
        current_email = current_user.email
        current_username = current_user.username
        
        # Render the form with pre-filled values
        return render_template('update_profile.html', email=current_email, username=current_username)
    
    elif request.method == 'POST':
        user_id = current_user.id
        current_password = request.form.get('current_password')
        new_email = request.form.get('email')
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        users = Users()

        if not users.verify_password(user_id, current_password):
            flash('Incorrect current password. Try again.', 'error')
            return redirect(url_for('update_profile'))

        if new_password != confirm_password:
            flash('Passwords do not match. Try again.', 'error')
            return redirect(url_for('update_profile'))

        users.updateUserDetails(user_id, new_email=new_email, new_username=new_username, new_password=new_password)
        flash('Profile updated successfully', 'success')

        # Redirect to the account page or any other appropriate page
        return redirect(url_for('account'))


#Payment routes

@app.route('/pricing', methods=['GET', 'POST'])
def pricing():    
    return render_template('pricing.html')

@app.route('/create_checkout_session', methods=['POST'])
@login_required
def create_checkout_session():
    product_id = request.form.get('product_id')
    price_id = request.form.get('price_id')

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price': price_id,
                'quantity': 1,
            }
        ],
        mode='payment',
        success_url=url_for('thanks', _external=True),
        cancel_url=url_for('index', _external=True),
    )
    
    return redirect(session.url, code=303)


@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

@app.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    print('WEBHOOK CALLED')

    if request.content_length > 1024 * 1024:
        print('REQUEST TOO BIG')
        abort(400)
    payload = request.get_data()
    sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = 'whsec_d3290e17f2cade77c240e17dc6ea076f243d88753f470e59a1e63d8e4a6d2ec0'
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print('INVALID PAYLOAD')
        return {}, 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print('INVALID SIGNATURE')
        return {}, 400

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(session)
        line_items = stripe.checkout.Session.list_line_items(session['id'], limit=1)
        print(line_items['data'][0]['description'])

    return {}

# Vehicle

# @app.route('/vehicles', methods=['GET', 'POST'])
# def vehicles():
#     vehicles_manager = Vehicles()


#     if request.method == 'POST':
#         # Add a new vehicle
#         vehicle_model = request.form['vehicle_model']
#         license_plate = request.form['license_plate']
#         user_id = current_user.id 
#         new_vehicle = Vehicles.createVehicle(vehicle_model, license_plate, user_id)
#         if new_vehicle:
#             return redirect(url_for('vehicles'))
#         else:
#             return "Failed to add vehicle"  

#     if request.method == 'GET':
#         if 'delete_vehicle_id' in request.args:
#             # Delete a vehicle
#             vehicle_id = int(request.args['delete_vehicle_id'])
#             if vehicles_manager.deleteVehicle(vehicle_id):
#                 return redirect(url_for('vehicles'))
#             else:
#                 return "Vehicle not found"  

#     # Get all vehicles
#     vehicles = vehicles_manager.getAllVehicles()
#     return render_template('view_vehicles.html', vehicles=vehicles)

@app.route('/vehicles', methods=['GET', 'POST'])
def vehicles():
    if request.method == 'POST':
        # Add a new vehicle
        vehicle_model = request.form['vehicle_model']
        license_plate = request.form['license_plate']
        user_id = current_user.id 
        new_vehicle = Vehicles.createVehicle(vehicle_model, license_plate, user_id)
        if new_vehicle:
            return redirect(url_for('vehicles'))
        else:
            return "Failed to add vehicle"  

    if request.method == 'GET':
        if 'delete_vehicle_id' in request.args:
            # Delete a vehicle
            vehicle_id = int(request.args['delete_vehicle_id'])
            if Vehicles.deleteVehicle(vehicle_id):
                return redirect(url_for('vehicles'))
            else:
                return "Vehicle not found"  

    # Get all vehicles
    vehicles = Vehicles.getAllVehicles()
    return render_template('view_vehicles.html', vehicles=vehicles)


@app.route("/allgarages")
def allGarages():
    garages = Garages.getAllGarages()

    return render_template("all_garages.html", garages=garages, user=getUser())


if __name__ == "__main__":
    app.run(debug=True)