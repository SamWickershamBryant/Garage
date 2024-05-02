from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, url_for, abort
import stripe, os
from datetime import datetime
from forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
from models import Garages, ParkingSpace, Vehicles, Reservations, session
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
@login_required
def search():
    location = request.args.get('location')
    print("Location:", location)

    search_results = Garages.searchGaragesByLocation(location)
    return render_template('garages_list.html', search_results=search_results)
    

@app.route("/garage/<int:garage_id>")
@login_required
def garage_parking_spaces(garage_id):
    garage = Garages.getGarageById(garage_id)
    if garage is None:
        return "404", 404

    parking_spaces = Garages.getSpacesbyGarageID(garage_id)
    return render_template(
        "garage.html", garage=garage, parking_spaces=parking_spaces, user=getUser()
    )

@app.route("/reserve_spot/<int:garage_id>", methods=['GET','POST'])
@login_required
def reserve(garage_id):
    reservation_date = request.form.get("reservation_date")
    available_spot = Garages.getAvailableSpot(garage_id)

    reserved_spot = Garages.reserveSpot(available_spot, reservation_date)
    if reserved_spot:
        Users.userReserveSpot(current_user.id, reserved_spot.id)
    else:
        flash("Failed to reserve spot.", "error")
        
    return redirect(url_for("cart"))


current_time = datetime.now().hour
cutoff_hour = 17 

@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if request.method == 'GET':

        current_email = current_user.email
        current_username = current_user.username
        
        return render_template('update_profile.html', email=current_email, username=current_username)
    
    elif request.method == 'POST':
        user_id = current_user.id
        current_password = request.form.get('current_password')
        new_email = request.form.get('email')
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        new_hashedpass = generate_password_hash(new_password, method="pbkdf2:sha256")

        users = Users()

        if not users.verify_password(user_id, current_password):
            flash('Incorrect current password. Try again.', 'error')
            return redirect(url_for('update_profile'))

        if new_password != confirm_password:
            flash('Passwords do not match. Try again.', 'error')
            return redirect(url_for('update_profile'))

        users.updateUserDetails(user_id, new_email=new_email, new_username=new_username, new_password=new_hashedpass)
        flash('Profile updated successfully', 'success')

        return redirect(url_for('account'))


# Checkout

@app.route("/cart")
@login_required
def cart():
    vehicles = Vehicles.getAllVehicles(current_user.id)
    current_vehicle = Vehicles.getCurrentVehicleByUserId(current_user.id)
    # if user cart is empty
    spot = None
    garage = None
    reservation_id = current_user.reserved
    if reservation_id != -1:
        reserved_spot = Garages.getSpotById(reservation_id)
        if reserved_spot:
            spot = reserved_spot.__dict__
            garage = reserved_spot.garage


    return render_template("cart.html", spot=spot, user=getUser(), vehicles=vehicles, current_vehicle=current_vehicle, garage=garage)

@app.route('/empty_cart', methods=['POST'])
@login_required
def empty_cart():
    current_user.reserved = -1
    session.commit()
    return redirect(url_for("cart"))


@app.route('/create_checkout_session', methods=['POST'])
@login_required
def create_checkout_session():
    product_id = request.form.get('product_id')
    price_id = request.form.get('price_id')
    spot_id = request.form.get('spot_id')
    spot_num = request.form.get('spot_num')
    garage_name = request.form.get('garage_name')
    vehicle_id = request.form.get('vehicle')
    vehicle_model = request.form.get('vehicle_model')
    vehicle_plate = request.form.get('vehicle_plate')
    date_str = request.form.get('reservation_date')
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    purchase_date = datetime.now().date()
    quantity = 1

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
        cancel_url=url_for('thanks', _external=True),
    )
    try:
        reservation_created = Reservations.createReservation(current_user.id, garage_name, spot_id, spot_num, vehicle_id, vehicle_model, vehicle_plate, date, purchase_date)
        if reservation_created:
            flash("Reservation created", "success")
            session.commit()
        
    except Exception as e:
        flash("Reservation created", "success")

    return redirect(session.url, code=303)


@app.route('/thanks')
@login_required
def thanks():
    current_user.reserved = -1
    session.commit()

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
        print('INVALID PAYLOAD')
        return {}, 400
    except stripe.error.SignatureVerificationError as e:
        print('INVALID SIGNATURE')
        return {}, 400

    # if checkout completed
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(session)
        line_items = stripe.checkout.Session.list_line_items(session['id'], limit=1)
        print(line_items['data'][0]['description'])

    return {}

@app.route("/reservation_history")
@login_required
def reservation_history():
    reservations = Reservations.getReservationsById(current_user.id)

    return render_template("reservations.html", reservations=reservations)

# Vehicle

@app.route("/set_current_vehicle/<int:vehicle_id>", methods=['POST'])
@login_required
def set_current_vehicle(vehicle_id):
    vehicle = Vehicles.getVehicleById(vehicle_id)
    if vehicle:
        current_user.current_vehicle = vehicle_id
        for user_vehicle in current_user.vehicles:
            user_vehicle.current_vehicle = False

        vehicle.current_vehicle = True
        session.commit()
    else:
        flash("Vehicle not found.", "error")
    
    return redirect(url_for("vehicles"))

@app.route('/vehicles', methods=['GET', 'POST'])
@login_required
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
    vehicles = Vehicles.getAllVehicles(current_user.id)
    return render_template('view_vehicles.html', vehicles=vehicles)


@app.route('/vehicles/add', methods=['GET', 'POST'])
@login_required
def add_vehicle():

    return render_template('add_vehicle.html')


@app.route('/vehicles/default', methods=['GET'])
@login_required
def default_vehicle():
    current_vehicle = Vehicles.getCurrentVehicleByUserId(current_user.id)
    if current_vehicle:
        vehicle_model = current_vehicle.vehicle_model
        vehicle_plate = current_vehicle.license_plate
    else:
        current_vehicle = None
        default_vehicle = None
        vehicle_model = None
        vehicle_plate = None
    return render_template('default_vehicle.html', current_vehicle=current_vehicle, vehicle_model=vehicle_model, vehicle_plate=vehicle_plate)


@app.route("/allgarages")
@login_required
def allGarages():
    garages = Garages.getAllGarages()

    return render_template("all_garages.html", garages=garages, user=getUser())


if __name__ == "__main__":
    app.run(debug=True)