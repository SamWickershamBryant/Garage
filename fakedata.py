from models import Garages
import random, datetime
from faker import Faker
fake = Faker()

def populateSpots():
    GARAGE_SIZE = 100
    BASE_PRICE_WEEKDAY = 30
    BASE_PRICE_WEEKEND = 50
    TIME_PERIOD_ADDITIONAL_COST = (5, 8)  # Time period: 5am to 8am
    ADDITIONAL_COST = 10


    for i in range(10):
        phone_number = fake.phone_number()
        hours = fake.boolean(chance_of_getting_true=50)
        wheelchair_accessible = fake.boolean(chance_of_getting_true=75) 
        service_type = random.choice(['self-service', 'valet'])  


        garage = {
            'name': fake.name() + ' Garage',
            'location': fake.address().replace('\n', ' '),
            'phone_number': phone_number,
            'hours': hours,
            'wheelchair_accessible': wheelchair_accessible,
            'service_type': service_type
        }
        Garages.createGarage(garage) 
        
        for j in range(50):
            # Calculate the base price based on the day of the week
            current_time = datetime.datetime.now()
            if current_time.weekday() < 4:  # Monday to Thursday
                base_price = BASE_PRICE_WEEKDAY
            else:  # Friday to Sunday
                base_price = BASE_PRICE_WEEKEND
            # Add additional cost if the current time is between 5am to 8am
            if TIME_PERIOD_ADDITIONAL_COST[0] <= current_time.hour < TIME_PERIOD_ADDITIONAL_COST[1]:
                price = base_price + ADDITIONAL_COST
            else:
                price = base_price
            spot = {'number': j, 'price': price, 'availability': random.choice([True, False]), 'garage_id': i}
            Garages.createSpot(spot)

populateSpots()