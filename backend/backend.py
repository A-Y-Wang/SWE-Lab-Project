from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get MongoDB URI from environment or use default
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/inventory_system")
print(mongo_uri)

app.config["MONGO_URI"] = mongo_uri
try:
    mongo = PyMongo(app)
    # Test connection
    mongo.db.command('ping')
    print("MongoDB connection successful!")
    print(f"Available collections: {mongo.db.list_collection_names()}")
except Exception as e:
    print(f"MongoDB connection error: {e}")
    # Continue running even with error to see additional debug info

# Helper function to serialize ObjectId
def serialize_objectid(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError("Type not serializable")

# Convert MongoDB document to JSON-serializable dict
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

# Inventory Routes
@app.route('/api/inventory', methods=['GET'])
def get_all_inventory():
    items = list(mongo.db.inventory.find())
    return jsonify([doc_to_dict(item) for item in items])

@app.route('/api/inventory/<item_id>', methods=['GET'])
def get_inventory_item(item_id):
    try:
        item = mongo.db.inventory.find_one({'_id': ObjectId(item_id)})
        if item:
            return jsonify(doc_to_dict(item))
        return jsonify({"error": "Item not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/inventory', methods=['POST'])
def add_inventory_item():
    try:
        # Print request data for debugging
        print(f"Request content type: {request.content_type}")
        print(f"Request data: {request.data}")
        
        data = request.get_json()
        print(f"Parsed JSON data: {data}")
        
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
            
        if not data.get('item_name'):
            return jsonify({"error": "Required field 'item_name' is missing"}), 400
            
        if 'quantity' not in data:
            return jsonify({"error": "Required field 'quantity' is missing"}), 400
            
        if not isinstance(data.get('quantity'), int):
            return jsonify({"error": "Field 'quantity' must be an integer"}), 400
        
        now = datetime.now()
        new_item = {
            'item_name': data['item_name'],
            'description': data.get('description', ''),
            'quantity': data['quantity'],
            'added_date': now,
            'last_updated': now
        }
        
        result = mongo.db.inventory.insert_one(new_item)
        new_item['_id'] = str(result.inserted_id)
        
        return jsonify({"message": "Item added successfully", "item": new_item}), 201
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Error in add_inventory_item: {e}")
        print(f"Traceback: {traceback_str}")
        return jsonify({"error": str(e), "traceback": traceback_str}), 400

@app.route('/api/inventory/<item_id>', methods=['PUT'])
def update_inventory_item(item_id):
    try:
        data = request.get_json()
        update_data = {}
        
        # Only update fields that are provided
        if 'item_name' in data:
            update_data['item_name'] = data['item_name']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'quantity' in data:
            update_data['quantity'] = data['quantity']
            
        # Always update the last_updated field
        update_data['last_updated'] = datetime.now()
        
        result = mongo.db.inventory.update_one(
            {'_id': ObjectId(item_id)},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "Item not found"}), 404
            
        return jsonify({"message": "Item updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/inventory/<item_id>', methods=['DELETE'])
def delete_inventory_item(item_id):
    try:
        # Check if the item is currently checked out
        checkout = mongo.db.checkout.find_one({
            'item_id': ObjectId(item_id),
            'return_date': None
        })
        
        if checkout:
            return jsonify({"error": "Cannot delete item that is currently checked out"}), 400
            
        result = mongo.db.inventory.delete_one({'_id': ObjectId(item_id)})
        
        if result.deleted_count == 0:
            return jsonify({"error": "Item not found"}), 404
            
        # Also delete checkout history for this item
        mongo.db.checkout.delete_many({'item_id': ObjectId(item_id)})
        
        return jsonify({"message": "Item and its checkout history deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Checkout Routes
@app.route('/api/checkout', methods=['GET'])
def get_all_checkouts():
    checkouts = list(mongo.db.checkout.find())
    return jsonify([doc_to_dict(checkout) for checkout in checkouts])

@app.route('/api/checkout/active', methods=['GET'])
def get_active_checkouts():
    active_checkouts = list(mongo.db.checkout.find({'return_date': None}))
    result = []
    
    for checkout in active_checkouts:
        checkout_dict = doc_to_dict(checkout)
        # Get item details
        item = mongo.db.inventory.find_one({'_id': ObjectId(checkout['item_id'])})
        if item:
            checkout_dict['item_details'] = doc_to_dict(item)
        result.append(checkout_dict)
    
    return jsonify(result)

@app.route('/api/checkout/<item_id>', methods=['POST'])
def checkout_item(item_id):
    try:
        data = request.get_json()
        
        if not data.get('checked_out_by'):
            return jsonify({"error": "Missing required field: checked_out_by"}), 400
            
        # Check if item exists and has available quantity
        item = mongo.db.inventory.find_one({'_id': ObjectId(item_id)})
        if not item:
            return jsonify({"error": "Item not found"}), 404
            
        if item['quantity'] <= 0:
            return jsonify({"error": "Item is out of stock"}), 400
            
        # Create checkout record
        checkout_data = {
            'item_id': ObjectId(item_id),
            'checked_out_date': datetime.now(),
            'checked_out_by': data['checked_out_by'],
            'condition': data.get('condition', 'Good'),
            'return_date': None
        }
        
        result = mongo.db.checkout.insert_one(checkout_data)
        
        # Decrease inventory quantity
        mongo.db.inventory.update_one(
            {'_id': ObjectId(item_id)},
            {
                '$inc': {'quantity': -1},
                '$set': {'last_updated': datetime.now()}
            }
        )
        
        checkout_data['_id'] = str(result.inserted_id)
        checkout_data['item_id'] = item_id  # Convert ObjectId to string for JSON
        
        return jsonify({
            "message": "Item checked out successfully",
            "checkout": doc_to_dict(checkout_data)
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/checkout/<checkout_id>/return', methods=['PUT'])
def return_item(checkout_id):
    try:
        data = request.get_json()
        
        # Find the checkout record
        checkout = mongo.db.checkout.find_one({'_id': ObjectId(checkout_id)})
        if not checkout:
            return jsonify({"error": "Checkout record not found"}), 404
            
        if checkout.get('return_date'):
            return jsonify({"error": "Item already returned"}), 400
            
        # Update checkout record with return date and condition
        update_data = {
            'return_date': datetime.now(),
        }
        
        if 'condition' in data:
            update_data['condition'] = data['condition']
            
        mongo.db.checkout.update_one(
            {'_id': ObjectId(checkout_id)},
            {'$set': update_data}
        )
        
        # Increase inventory quantity
        mongo.db.inventory.update_one(
            {'_id': checkout['item_id']},
            {
                '$inc': {'quantity': 1},
                '$set': {'last_updated': datetime.now()}
            }
        )
        
        return jsonify({"message": "Item returned successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/checkout/<checkout_id>/update-condition', methods=['PUT'])
def update_checkout_condition(checkout_id):
    try:
        data = request.get_json()
        
        if 'condition' not in data:
            return jsonify({"error": "Missing required field: condition"}), 400
            
        valid_conditions = ['New', 'Good', 'Damaged', 'Lost']
        if data['condition'] not in valid_conditions:
            return jsonify({"error": f"Invalid condition. Must be one of: {', '.join(valid_conditions)}"}), 400
            
        result = mongo.db.checkout.update_one(
            {'_id': ObjectId(checkout_id)},
            {'$set': {'condition': data['condition']}}
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "Checkout record not found"}), 404
            
        # If condition is "Lost", don't increment inventory on return
        if data['condition'] == 'Lost':
            checkout = mongo.db.checkout.find_one({'_id': ObjectId(checkout_id)})
            
            # If the item is already returned, we need to decrement the inventory
            if checkout.get('return_date'):
                mongo.db.inventory.update_one(
                    {'_id': checkout['item_id']},
                    {'$inc': {'quantity': -1}}
                )
            
        return jsonify({"message": "Condition updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Stats and Reporting
@app.route('/api/stats/inventory', methods=['GET'])
def inventory_stats():
    try:
        total_items = mongo.db.inventory.count_documents({})
        out_of_stock = mongo.db.inventory.count_documents({'quantity': 0})
        
        # Get the most popular items (most checked out)
        pipeline = [
            {'$group': {'_id': '$item_id', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 5}
        ]
        popular_items = list(mongo.db.checkout.aggregate(pipeline))
        
        popular_details = []
        for item in popular_items:
            inventory_item = mongo.db.inventory.find_one({'_id': item['_id']})
            if inventory_item:
                popular_details.append({
                    'item': doc_to_dict(inventory_item),
                    'checkout_count': item['count']
                })
        
        return jsonify({
            'total_unique_items': total_items,
            'out_of_stock_items': out_of_stock,
            'popular_items': popular_details
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)