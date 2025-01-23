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
    pizzas = [
        {
            "id": rp.pizza_id,
            "name": Pizza.query.get(rp.pizza_id).name,
            "ingredients": Pizza.query.get(rp.pizza_id).ingredients,
        }
        for rp in restaurant_pizzas
    ]
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
    price = data.get("price")
    restaurant_id = data.get("restaurant_id")
    pizza_id = data.get("pizza_id")

    # Validate price
    if not (1 <= price <= 30):
        return jsonify({"errors": ["Price must be between 1 and 30"]}), 400

    # Check if restaurant and pizza exist
    if not Restaurant.query.get(restaurant_id):
        return jsonify({"errors": ["Restaurant not found"]}), 404
    if not Pizza.query.get(pizza_id):
        return jsonify({"errors": ["Pizza not found"]}), 404

    # Create and save restaurant-pizza relationship
    restaurant_pizza = RestaurantPizza(
        price=price,
        restaurant_id=restaurant_id,
        pizza_id=pizza_id
    )
    db.session.add(restaurant_pizza)
    db.session.commit()

    return jsonify({
        "id": restaurant_pizza.id,
        "price": restaurant_pizza.price,
        "restaurant_id": restaurant_pizza.restaurant_id,
        "pizza_id": restaurant_pizza.pizza_id,
    }), 201

if __name__ == "__main__":
    app.run(port=5555, debug=True)
