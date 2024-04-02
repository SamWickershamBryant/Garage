from models import Garage
import random

def populateSpots():
    GARAGE_SIZE = 100
    BASE_PRICE = 10

    for i in range(50):
        distance_from_top = i  # Distance from the top of the garage
        distance_from_bottom = GARAGE_SIZE - i - 1 # Distance from bottom
        price_multiplier = 1 + (
            distance_from_top / GARAGE_SIZE + distance_from_bottom / GARAGE_SIZE
        )
        spot = {'id':i,'price':round(BASE_PRICE * price_multiplier, 2),'reserved':random.choice([True, False])}
        Garage.createSpot(spot)

populateSpots()