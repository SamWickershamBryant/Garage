from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    select,
    update,
    delete,
    func,
)

# from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from flask_login import UserMixin

engine = create_engine("sqlite:///data.db")
Base = declarative_base()


class User(Base, UserMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(50), unique=True)
    username = Column(String(20), unique=True)
    password = Column(String(256), unique=True)
    reserved = Column(Integer, default=-1)


class Garage(Base):
    __tablename__ = "garages"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    location = Column(String(100))

    # Relationship with ParkingSpace
    spaces = relationship("ParkingSpace", back_populates="garage")


class ParkingSpace(Base):
    __tablename__ = "parking_spaces"
    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    price = Column(Integer)
    availability = Column(Integer)
    garage_id = Column(Integer, ForeignKey("garages.id"))

    # Relationship with Garage
    garage = relationship("Garage", back_populates="spaces")

    def __init__(self, number, price, availability):
        self.number = number
        self.price = price
        self.availability = availability


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
    def userReserveSpot(uid,sid):
        usr = session.query(User).get(uid)
        usr.reserved = sid
        session.commit()
    def getAllUsers():
        users = session.query(User).all()
        users_as_dict = [user.__dict__ for user in users]
        return users_as_dict

class Garage():
    def getSpotById(id):
        spot = session.query(Spot).get(id)
        return spot
    def reserveSpot(id):
        spot = session.query(Spot).get(id)
        spot.reserved = True
        session.commit()
    def getAllSpots():
        spots = session.query(Spot).all()
        spots_as_dict = [spot.__dict__ for spot in spots]
        return spots_as_dict
    def createSpot(spotdict):
        spot = Spot(**spotdict)
        session.add(spot)
        session.commit()