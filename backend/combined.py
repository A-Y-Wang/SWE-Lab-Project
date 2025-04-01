from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

# MongoDB Configuration
inventory_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/inventory_system")
user_uri = "mongodb+srv://swelabteam:0njGARlJosA7m0B4@userstuff.vmqiy.mongodb.net/?retryWrites=true&w=majority&appName=UserStuff"

# Connect to Inventory Database
app.config["MONGO_URI"] = inventory_uri
inventory_mongo = PyMongo(app)
inventory_db = inventory_mongo.cx['inventory_system']

# Connect to User Database
user_client = MongoClient(user_uri, server_api=ServerApi('1'))
user_db = user_client["UserStuff"]
user_collection = user_db["UserLogin"]

try:
    inventory_db.command('ping')
    print("Connected to Inventory MongoDB!")
    print(f"Available collections: {inventory_db.list_collection_names()}")
except Exception as e:
    print(f"Inventory MongoDB connection error: {e}")

try:
    user_client.admin.command('ping')
    print("Connected to User MongoDB!")
except Exception as e:
    print(e)

# Helper function to serialize MongoDB documents
def doc_to_dict(doc):
    if doc is None:
        return None
    doc_dict = dict(doc)
    for key, value in doc_dict.items():
        if isinstance(value, ObjectId):
            doc_dict[key] = str(value)
        elif isinstance(value, datetime):
            doc_dict[key] = value.isoformat()
    return doc_dict

# User Routes
@app.route('/signup', methods=['POST'])
def create_user():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400
        existing_user = user_collection.find_one({"Username": username})
        if existing_user:
            return jsonify({"error": "User already exists"}), 409
        doc = {
            "Username": username,
            "Password": password,
            "UserId": user_collection.count_documents({}) + 1,
            "ProjectIds": []
        }
        user_collection.insert_one(doc)
        return jsonify({"message": "Successfully registered", "redirect": "/checkout"}), 201
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Server error"}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400
        user = user_collection.find_one({"Username": username})
        if user:
            if password == user.get("Password"):
                return jsonify({"message": "Login success", "redirect": "/checkout"}), 200
            else:
                return jsonify({"error": "Incorrect password"}), 401
        else:
            return jsonify({"error": "User does not exist"}), 404
    except Exception as e:
        print("Database error:", e)
        return jsonify({"error": "Server error"}), 500

# Inventory Routes
@app.route('/api/inventory', methods=['GET'])
def get_all_inventory():
    items = list(inventory_db.inventory.find())
    return jsonify([doc_to_dict(item) for item in items])

@app.route('/api/inventory/<item_id>', methods=['GET'])
def get_inventory_item(item_id):
    try:
        item = inventory_db.inventory.find_one({'_id': ObjectId(item_id)})
        if item:
            return jsonify(doc_to_dict(item))
        return jsonify({"error": "Item not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/inventory', methods=['POST'])
def add_inventory_item():
    try:
        data = request.get_json()
        if not data.get('item_name') or 'quantity' not in data:
            return jsonify({"error": "Missing required fields"}), 400
        if not isinstance(data.get('quantity'), int):
            return jsonify({"error": "Quantity must be an integer"}), 400
        now = datetime.now()
        new_item = {
            'item_name': data['item_name'],
            'description': data.get('description', ''),
            'quantity': data['quantity'],
            'added_date': now,
            'last_updated': now
        }
        result = inventory_db.inventory.insert_one(new_item)
        new_item['_id'] = str(result.inserted_id)
        return jsonify({"message": "Item added successfully", "item": new_item}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/inventory/<item_id>', methods=['DELETE'])
def delete_inventory_item(item_id):
    try:
        checkout = inventory_db.checkout.find_one({
            'item_id': ObjectId(item_id),
            'return_date': None
        })
        if checkout:
            return jsonify({"error": "Cannot delete item that is currently checked out"}), 400
        result = inventory_db.inventory.delete_one({'_id': ObjectId(item_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Item not found"}), 404
        inventory_db.checkout.delete_many({'item_id': ObjectId(item_id)})
        return jsonify({"message": "Item and its checkout history deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        user_client.close()
