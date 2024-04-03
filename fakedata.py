from models import Garages
import random
from faker import Faker
fake = Faker()

def populateSpots():
    GARAGE_SIZE = 100
    BASE_PRICE = 10

    for i in range(10):
        garage = {'name':fake.name() + ' Garage', 'location':fake.address().replace('\n',' ')}
        Garages.createGarage(garage)
        for j in range(50):
            distance_from_top = j  # Distance from the top of the garage
            distance_from_bottom = GARAGE_SIZE - j - 1 # Distance from bottom
            price_multiplier = 1 + (
                distance_from_top / GARAGE_SIZE + distance_from_bottom / GARAGE_SIZE
            )
            spot = {'number':i,'price':round(BASE_PRICE * price_multiplier, 2),'availability':random.choice([True, False]), 'garage_id':i}
            Garages.createSpot(spot)

populateSpots()