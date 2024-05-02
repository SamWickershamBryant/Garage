from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    ForeignKeyConstraint,
    Boolean,
    Date,
    select,
    update,
    delete,
    func,
    Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, joinedload
from flask_login import UserMixin
from datetime import datetime



engine = create_engine("sqlite:///data.db")
Base = declarative_base()


class User(Base, UserMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(50), unique=True)
    username = Column(String(20), unique=True)
    password = Column(String(256), unique=True)
    reserved = Column(Integer, default=-1)

    vehicles = relationship("Vehicle", back_populates="owner")
    reservations = relationship("Reservation", back_populates="user")


class Garage(Base):
    __tablename__ = "garages"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    location = Column(String(100))
    phone_number = Column(String(10))
    hours = Column(Boolean, default=False)
    wheelchair_accessible = Column(Boolean, default=False)
    service_type = Column(String(20))

    parking_spaces = relationship("ParkingSpace", back_populates="garage")
    reservations = relationship("Reservation", back_populates="garage")

class ParkingSpace(Base):
    __tablename__ = "parking_spaces"
    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    price = Column(Integer)
    availability = Column(Boolean)
    garage_id = Column(Integer, ForeignKey('garages.id'))
    reservation_date = Column(Date)

    garage = relationship("Garage", back_populates="parking_spaces")
    reservations = relationship("Reservation", back_populates="spot", foreign_keys="[Reservation.spot_id]")

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True)
    vehicle_model = Column(String(20))
    license_plate = Column(String(10))
    user_id = Column(Integer, ForeignKey('users.id'))
    current_vehicle = Column(Boolean, default=False)

    owner = relationship("User", back_populates="vehicles")
    reservations = relationship("Reservation", back_populates="vehicle")


class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    garage_name = Column(String, ForeignKey('garages.name'))
    spot_id = Column(Integer, ForeignKey('parking_spaces.id'))
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
    reservation_date = Column(Date)
    purchase_date = Column(Date)

    vehicle_model = Column(String(20))
    vehicle_plate = Column(String(10))
    spot_num = Column(Integer)

    user = relationship("User", back_populates="reservations")
    garage = relationship("Garage", back_populates="reservations")
    vehicle = relationship("Vehicle", back_populates="reservations")
    spot = relationship("ParkingSpace", back_populates="reservations")

    


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

session = Session()  # use to modify database


class Users:
    def getUserById(id):
        usr = session.query(User).get(id)
        return usr

    def getUserByName(name):
        user = session.query(User).filter_by(username=name).first()
        return user

    def createUser(username, email, pswd):
        try:
            usr = User(username=username, email=email, password=pswd)
            session.add(usr)
            session.commit()
            return True
        except:
            session.rollback()
            return False

    def userReserveSpot(uid, sid):
        user = session.query(User).get(uid)
        if user:
            user.reserved = sid
            try:
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                print(f"Error occured: {e}")
                return False
        else:
            return False

    def getAllUsers():
        users = session.query(User).all()
        users_as_dict = [user.__dict__ for user in users]
        return users_as_dict
    
    def updateUserDetails(self, user_id, new_email, new_username, new_password):
        user = session.query(User).get(user_id)
        
        if new_email:
            user.email = new_email
        
        if new_username:
            user.username = new_username
        
        if new_password:
            user.password = new_password

        session.commit()

    def changePassword(self, user_id, new_password):
        user = session.query(User).get(user_id)
        user.password = new_password
        session.commit()
    
    def verify_password(self, user_id, password):
        user = session.query(User).get(user_id)
        if user:
            return user.password == password
        return False



class Garages:
    def getSpotById(id):
        spot = session.query(ParkingSpace).get(id)
        return spot

    def getGarageById(id):
        garage_id = session.query(Garage).get(id)
        return garage_id

    def getAvailableSpot(garage_id):
        available_spot = session.query(ParkingSpace).filter_by(garage_id=garage_id, availability=True, reservation_date=None).first()
        if available_spot:
            return available_spot.id
        else:
            return None

    def reserveSpot(available_spot_id, reservation_date_str):
        if not reservation_date_str:
            print("Reservation date is empty")
            return None
        try:
            reservation_date = datetime.strptime(reservation_date_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format")
            return None

        available_spot = session.query(ParkingSpace).get(available_spot_id)
        if available_spot:
            available_spot.reservation_date = reservation_date
            available_spot.availability = False
            try:
                session.commit()
                return available_spot
            except Exception as e:
                session.rollback()
                print(f"Error occurred: {e}")
                return None
        else:
            print("Spot not found")
            return None

    def getAllSpots():
        spots = session.query(ParkingSpace).all()
        spots_as_dict = [spot.__dict__ for spot in spots]
        return spots_as_dict

    def createSpot(spotdict):
        spot = ParkingSpace(**spotdict)
        session.add(spot)
        session.commit()

    def createGarage(garagedict):
        garage = Garage(**garagedict)
        session.add(garage)
        session.commit()

    def getAllGarages():
        garages = session.query(Garage).all()
        garages_as_dict = [user.__dict__ for user in garages]
        return garages_as_dict

    def getSpacesbyGarageID(garage_id):
        spaces = session.query(ParkingSpace).filter_by(garage_id=garage_id).all()
        return spaces
    
    def searchGaragesByLocation(location):
        return session.query(Garage).filter(Garage.location.ilike(f"%{location}%")).all()


class Vehicles:
    def getVehicleById(id):
        vehicle_id = session.query(Vehicle).get(id)
        return vehicle_id
    
    def getCurrentVehicleByUserId(user_id):
        current_vehicle = session.query(Vehicle)\
            .filter(Vehicle.user_id == user_id, Vehicle.current_vehicle == True)\
            .options(joinedload(Vehicle.owner))\
            .first()
        return current_vehicle
    
    def createVehicle(vehicle_model, license_plate, user_id):
        try:
            vehicle = Vehicle(vehicle_model=vehicle_model, license_plate=license_plate, user_id=user_id)
            session.add(vehicle)
            session.commit()
            return True
        except:
            session.rollback()
            return False
        
    def deleteVehicle(id):
        vehicle = session.query(Vehicle).get(id)
        if vehicle:
            session.delete(vehicle)
            session.commit()
            return True
        else:
            session.close()
            return False
        
    def getAllVehicles(user_id):
        vehicles = session.query(Vehicle).filter(Vehicle.user_id == user_id).all()
        vehicles_as_dict = [vehicle.__dict__ for vehicle in vehicles]
        return vehicles_as_dict
    


class Reservations:        
    def createReservation(user_id, garage_name, spot_id, spot_num, vehicle_id, vehicle_model, vehicle_plate, date, purchase_date):
        try:
            res = Reservation(user_id=user_id, garage_name=garage_name, spot_id=spot_id, spot_num=spot_num, vehicle_id=vehicle_id, vehicle_model=vehicle_model, vehicle_plate=vehicle_plate, reservation_date=date, purchase_date=purchase_date)
            session.add(res)
            session.commit()
            return True
        except Exception as e:
            return False


    def getReservationsById(user_id):
        reservations = session.query(Reservation) \
                          .options(joinedload(Reservation.vehicle), joinedload(Reservation.spot)) \
                          .filter_by(user_id=user_id) \
                          .all()
        return reservations

