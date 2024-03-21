from flask import Flask, render_template
import random

app = Flask(__name__)


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

    return render_template("index.html", parking_spots=parking_spots)


if __name__ == "__main__":
    app.run(debug=True)
