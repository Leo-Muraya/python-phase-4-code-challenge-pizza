#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from models import db, Restaurant, Pizza, RestaurantPizza

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)

# Routes
@app.route("/")
def index():
    return "<h1>Code Challenge</h1>"

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([
        {"id": r.id, "name": r.name, "address": r.address}
        for r in restaurants
    ])

@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    restaurant_pizzas = RestaurantPizza.query.filter_by(restaurant_id=id).all()
    pizzas = []
    for rp in restaurant_pizzas:
        pizza = Pizza.query.get(rp.pizza_id)
        if pizza:  
            pizzas.append({
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients,
            })

    return jsonify({
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "pizzas": pizzas
    })


@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    # Delete all restaurant_pizzas manually if cascade is not working
    RestaurantPizza.query.filter_by(restaurant_id=id).delete()

    db.session.delete(restaurant)
    db.session.commit()
    return '', 204


@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([
        {"id": p.id, "name": p.name, "ingredients": p.ingredients}
        for p in pizzas
    ])

@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")
    price = data.get("price")

    # Validation: Check if the price is between 1 and 30
    if not (1 <= price <= 30):
        return jsonify({"errors": ["validation errors"]}), 400
    
    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)

    if not pizza:
        return jsonify({"errors": ["Pizza not found"]}), 404
    if not restaurant:
        return jsonify({"errors": ["Restaurant not found"]}), 404

    # Create a new RestaurantPizza 
    restaurant_pizza = RestaurantPizza(
        pizza_id=pizza_id,
        restaurant_id=restaurant_id,
        price=price
    )

    db.session.add(restaurant_pizza)
    db.session.commit()

    return jsonify(restaurant_pizza.to_dict()), 201

if __name__ == "__main__":
    app.run(port=5555, debug=True)
