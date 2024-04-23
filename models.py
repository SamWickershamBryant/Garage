from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    Date,
    select,
    update,
    delete,
    func,
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
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


class Garage(Base):
    __tablename__ = "garages"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    location = Column(String(100))
    phone_number = Column(String(10))
    hours = Column(Boolean, default=False)
    wheelchair_accessible = Column(Boolean, default=False)
    service_type = Column(String(20))

class ParkingSpace(Base):
    __tablename__ = "parking_spaces"
    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    price = Column(Integer)
    availability = Column(Boolean)
    garage_id = Column(Integer)
    reservation_date = Column(Date)

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True)
    vehicle_model = Column(String(20))
    license_plate = Column(String(100))
    user_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="vehicles")

class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True)


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
    
    def updateUserDetails(self, user_id, new_email=None, new_username=None, new_password=None):
        user = session.query(User).get(user_id)
        
        if new_email is not None:
            user.email = new_email
        
        if new_username is not None:
            user.username = new_username
        
        if new_password is not None:
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
        
    def getAllVehicles():
        vehicles = session.query(Vehicle).all()
        vehicles_as_dict = [vehicle.__dict__ for vehicle in vehicles]
        return vehicles_as_dict
