from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

# Get MongoDB URI from environment or use default
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/inventory_system")
print(mongo_uri)

# Create a direct MongoClient connection instead of using Flask-PyMongo
# This gives more direct control over the connection
try:
    # Connect directly to MongoDB
    client = MongoClient(mongo_uri)
    
    # Access the database
    db = client.get_database('inventory_system')
    
    # Test connection
    client.admin.command('ping')
    print("MongoDB connection successful!")
    print(f"Available collections: {db.list_collection_names()}")
    
    # Create other database connections
    user_db = client["UserInfo"]
    projects_db = client["Projects"]
    
    user_collection = user_db["UserLogin"]
    projects_collection = projects_db["Project1"]
    
except Exception as e:
    print(f"MongoDB connection error: {e}")
    # Initialize variables to prevent None errors, app will still show errors but won't crash
    db = None
    user_db = None
    projects_db = None
    user_collection = None
    projects_collection = None

#password encryption stuff
passN = 2
passD = 1

# User Routes
@app.route('/signup', methods=['POST'])
def create_user():
    if user_collection is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400
        existing_user = user_collection.find_one({"Username": username})
        if existing_user:
            return jsonify({"error": "User already exists"}), 409
        
        encryptedpass = encrypt(password,passN,passD)
        
        doc = {
            "Username": username,
            "Password": encryptedpass,
            "UserId": user_collection.count_documents({}) + 1,
            "ProjectIds": []
        }
        user_collection.insert_one(doc)
        return jsonify({"message": "Successfully registered", "redirect": "/checkout"}), 201
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/login', methods=['POST'])
def login():
    if user_collection is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400
        user = user_collection.find_one({"Username": username})
        if user:

            decryptedpass=decrypt(user.get("Password"),passN,passD)

            if password == decryptedpass:
                return jsonify(doc_to_dict(user)), 200
            else:
                return jsonify({"error": "Incorrect password"}), 401
        else:
            return jsonify({"error": "User does not exist"}), 404
    except Exception as e:
        print("Database error:", e)
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def encrypt(inputText, n, d):
    if d!=1 and d!=-1:
        return inputText
    if n<1:
        return inputText
    flip = ""
    for c in inputText:
        flip = c + flip
    final = ""
    for c in flip:
        see = ord(c)+n*d
        if see>126 or see<34:
            temp = chr(((see-34)%93)+34)
        else:
            temp = chr(see)
        final += temp
    return final

def decrypt(inputText, n,d):
    if d!=1 and d!=-1:
        return inputText
    if n<1:
        return inputText
    flip = ""
    for c in inputText:
        flip = c + flip
    final = ""
    for c in flip:
        see = ord(c)+n*d*(-1)
        if see>126 or see<34:
            temp = chr(((see-34)%93)+34)
        else:
            temp = chr(see)
        final += temp
    return final


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


#Project+Inventory Routes
@app.route('/api/user/<userId>/projects/inventory', methods=["GET"])
def get_projects_inventory(userId):
    if db is None or user_db is None or projects_collection is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    user = user_db["UserLogin"].find_one({"UserId": int(userId)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    project_ids = user.get("ProjectIds", [])
    if not project_ids:
        return jsonify([])
    #list of projects where project_id is in project_ids
    projects = list(projects_collection.find({"project_id": {"$in":project_ids}}))
    projectItems=[]

    for project in projects:
        item_ids = project.get("items", [])
        itemsPerProj = db.inventory.find({"item_id":{"$in": item_ids}})
        itemsson = [doc_to_dict(item) for item in itemsPerProj]

        project_data ={
            "project_id": str(project["project_id"]),
            "project_name": project.get("project_name", "Unamed Project"),
            "items": itemsson
        }
        projectItems.append(project_data)
    return jsonify(projectItems), 200

#Inventory Routes
@app.route('/api/inventory', methods=['GET'])
def get_all_inventory():
    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        items = list(db.inventory.find())
        return jsonify([doc_to_dict(item) for item in items])
    except Exception as e:
        print(f"Error getting inventory: {e}")
        return jsonify({"error": f"Error retrieving inventory: {str(e)}"}), 500

@app.route('/api/inventory/<item_id>', methods=['GET'])
def get_inventory_item(item_id):
    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        item = db.inventory.find_one({'_id': ObjectId(item_id)})
        if item:
            return jsonify(doc_to_dict(item))
        return jsonify({"error": "Item not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/inventory', methods=['POST'])
def add_inventory_item():
    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
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
        
        result = db.inventory.insert_one(new_item)
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
    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        data = request.get_json()
        print(data)
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
        
        result = db.inventory.update_one(
            {'_id': ObjectId(item_id)},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "Item not found"}), 404
            
        return jsonify({"message": "Item updated successfully"})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400

@app.route('/api/inventory/<item_id>', methods=['DELETE'])
def delete_inventory_item(item_id):
    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        # Check if the item is currently checked out
        checkout = db.checkout.find_one({
            'item_id': ObjectId(item_id),
            'return_date': None
        })
        
        if checkout:
            return jsonify({"error": "Cannot delete item that is currently checked out"}), 400
            
        result = db.inventory.delete_one({'_id': ObjectId(item_id)})
        
        if result.deleted_count == 0:
            return jsonify({"error": "Item not found"}), 404
            
        # Also delete checkout history for this item
        db.checkout.delete_many({'item_id': ObjectId(item_id)})
        
        return jsonify({"message": "Item and its checkout history deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Checkout Routes
@app.route('/api/checkout', methods=['GET'])
def get_all_checkouts():
    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        checkouts = list(db.checkout.find())
        return jsonify([doc_to_dict(checkout) for checkout in checkouts])
    except Exception as e:
        print(f"Error getting checkouts: {e}")
        return jsonify({"error": f"Error retrieving checkouts: {str(e)}"}), 500

@app.route('/api/checkout/active', methods=['GET'])
def get_active_checkouts():
    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        active_checkouts = list(db.checkout.find({'return_date': None}))
        result = []
        
        for checkout in active_checkouts:
            checkout_dict = doc_to_dict(checkout)
            # Get item details
            item = db.inventory.find_one({'_id': ObjectId(checkout['item_id'])})
            if item:
                checkout_dict['item_details'] = doc_to_dict(item)
            result.append(checkout_dict)
        
        return jsonify(result)
    except Exception as e:
        print(f"Error getting active checkouts: {e}")
        return jsonify({"error": f"Error retrieving active checkouts: {str(e)}"}), 500

@app.route('/api/checkout/<item_id>', methods=['POST'])
def checkout_item(item_id):
    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        data = request.get_json()
        
        if not data.get('checked_out_by'):
            return jsonify({"error": "Missing required field: checked_out_by"}), 400
            
        # Check if item exists and has available quantity
        item = db.inventory.find_one({'_id': ObjectId(item_id)})
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
        
        result = db.checkout.insert_one(checkout_data)
        
        # Decrease inventory quantity
        db.inventory.update_one(
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
    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        data = request.get_json()
        
        # Find the checkout record
        checkout = db.checkout.find_one({'_id': ObjectId(checkout_id)})
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
            
        db.checkout.update_one(
            {'_id': ObjectId(checkout_id)},
            {'$set': update_data}
        )
        
        # Increase inventory quantity
        db.inventory.update_one(
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
    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        data = request.get_json()
        
        if 'condition' not in data:
            return jsonify({"error": "Missing required field: condition"}), 400
            
        valid_conditions = ['New', 'Good', 'Damaged', 'Lost']
        if data['condition'] not in valid_conditions:
            return jsonify({"error": f"Invalid condition. Must be one of: {', '.join(valid_conditions)}"}), 400
            
        result = db.checkout.update_one(
            {'_id': ObjectId(checkout_id)},
            {'$set': {'condition': data['condition']}}
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "Checkout record not found"}), 404
            
        # If condition is "Lost", don't increment inventory on return
        if data['condition'] == 'Lost':
            checkout = db.checkout.find_one({'_id': ObjectId(checkout_id)})
            
            # If the item is already returned, we need to decrement the inventory
            if checkout.get('return_date'):
                db.inventory.update_one(
                    {'_id': checkout['item_id']},
                    {'$inc': {'quantity': -1}}
                )
            
        return jsonify({"message": "Condition updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Stats and Reporting
@app.route('/api/stats/inventory', methods=['GET'])
def inventory_stats():
    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        total_items = db.inventory.count_documents({})
        out_of_stock = db.inventory.count_documents({'quantity': 0})
        
        # Get the most popular items (most checked out)
        pipeline = [
            {'$group': {'_id': '$item_id', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 5}
        ]
        popular_items = list(db.checkout.aggregate(pipeline))
        
        popular_details = []
        for item in popular_items:
            inventory_item = db.inventory.find_one({'_id': item['_id']})
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

# Project Management Routes
# Add these to your backend.py file

# Project Routes
@app.route('/api/projects', methods=['GET'])
def get_all_projects():
    if projects_db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        projects = list(projects_collection.find())
        return jsonify([doc_to_dict(project) for project in projects])
    except Exception as e:
        print(f"Error getting projects: {e}")
        return jsonify({"error": f"Error retrieving projects: {str(e)}"}), 500

@app.route('/api/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    if projects_db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        # Try to match by string ID first
        project = projects_collection.find_one({"project_id": project_id})
        
        # If not found, try to match by ObjectId if it's a valid ObjectId
        if not project and ObjectId.is_valid(project_id):
            project = projects_collection.find_one({"_id": ObjectId(project_id)})
            
        if project:
            return jsonify(doc_to_dict(project))
        return jsonify({"error": "Project not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/projects', methods=['POST'])
def create_project():
    if projects_db is None or user_db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        data = request.get_json()
        
        if not data.get('project_name'):
            return jsonify({"error": "Required field 'project_name' is missing"}), 400
            
        if not data.get('created_by'):
            return jsonify({"error": "Required field 'created_by' (user ID) is missing"}), 400
        
        # Check if user exists
        user_id = data.get('created_by')
        user = user_db["UserLogin"].find_one({"UserId": int(user_id)})
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Generate a new project ID
        new_project_id = f"p{projects_collection.count_documents({}) + 1:05d}"
        
        now = datetime.now()
        new_project = {
            'project_id': new_project_id,
            'project_name': data['project_name'],
            'description': data.get('description', ''),
            'created_by': user_id,
            'created_date': now,
            'last_updated': now,
            'users': [user_id],  # Initial user is the creator
            'items': []  # No items initially
        }
        
        result = projects_collection.insert_one(new_project)
        
        # Add project to user's projects
        user_db["UserLogin"].update_one(
            {"UserId": int(user_id)},
            {"$push": {"ProjectIds": new_project_id}}
        )
        
        # Return the new project
        new_project['_id'] = str(result.inserted_id)
        
        return jsonify({
            "message": "Project created successfully",
            "project": doc_to_dict(new_project)
        }), 201
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Error in create_project: {e}")
        print(f"Traceback: {traceback_str}")
        return jsonify({"error": str(e), "traceback": traceback_str}), 400

@app.route('/api/projects/<project_id>', methods=['PUT'])
def update_project(project_id):
    if projects_db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        data = request.get_json()
        
        # Find the project
        project = projects_collection.find_one({"project_id": project_id})
        if not project and ObjectId.is_valid(project_id):
            project = projects_collection.find_one({"_id": ObjectId(project_id)})
            
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Verify that the requesting user is part of the project or a creator
        if 'user_id' in data:
            user_id = int(data['user_id'])
            if user_id not in project.get('users', []) and user_id != project.get('created_by'):
                return jsonify({"error": "Unauthorized to update this project"}), 403
        
        update_data = {}
        
        # Only update fields that are provided
        if 'project_name' in data:
            update_data['project_name'] = data['project_name']
        if 'description' in data:
            update_data['description'] = data['description']
            
        # Always update the last_updated field
        update_data['last_updated'] = datetime.now()
        
        # Use project_id for the query if it exists, otherwise use _id
        if 'project_id' in project:
            result = projects_collection.update_one(
                {'project_id': project_id},
                {'$set': update_data}
            )
        else:
            result = projects_collection.update_one(
                {'_id': ObjectId(project_id)},
                {'$set': update_data}
            )
        
        if result.matched_count == 0:
            return jsonify({"error": "Project not found"}), 404
            
        return jsonify({"message": "Project updated successfully"})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400

@app.route('/api/projects/<project_id>/join', methods=['POST'])
def join_project(project_id):
    if projects_db is None or user_db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        data = request.get_json()
        
        if not data.get('user_id'):
            return jsonify({"error": "Required field 'user_id' is missing"}), 400
        
        user_id = int(data['user_id'])
        
        # Check if user exists
        user = user_db["UserLogin"].find_one({"UserId": user_id})
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check if project exists
        project = projects_collection.find_one({"project_id": project_id})
        if not project and ObjectId.is_valid(project_id):
            project = projects_collection.find_one({"_id": ObjectId(project_id)})
            
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Check if user is already in the project
        if 'project_id' in project:
            actual_project_id = project['project_id']
        else:
            actual_project_id = project_id
            
        if user_id in project.get('users', []):
            return jsonify({"message": "User is already a member of this project"}), 200
        
        # Add user to project
        result = projects_collection.update_one(
            {"project_id": actual_project_id} if 'project_id' in project else {"_id": ObjectId(project_id)},
            {"$push": {"users": user_id}}
        )
        
        # Add project to user's projects
        user_db["UserLogin"].update_one(
            {"UserId": user_id},
            {"$push": {"ProjectIds": actual_project_id}}
        )
        
        return jsonify({"message": "Successfully joined project"})
    except Exception as e:
        print(f"Error joining project: {e}")
        return jsonify({"error": str(e)}), 400

@app.route('/api/projects/<project_id>/leave', methods=['POST'])
def leave_project(project_id):
    if projects_db is None or user_db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        data = request.get_json()
        
        if not data.get('user_id'):
            return jsonify({"error": "Required field 'user_id' is missing"}), 400
        
        user_id = int(data['user_id'])
        
        # Check if user exists
        user = user_db["UserLogin"].find_one({"UserId": user_id})
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check if project exists
        project = projects_collection.find_one({"project_id": project_id})
        if not project and ObjectId.is_valid(project_id):
            project = projects_collection.find_one({"_id": ObjectId(project_id)})
            
        if not project:
            return jsonify({"error": "Project not found"}), 404
            
        # Get actual project ID
        if 'project_id' in project:
            actual_project_id = project['project_id']
        else:
            actual_project_id = project_id
        
        # Check if user is in the project
        if user_id not in project.get('users', []):
            return jsonify({"error": "User is not a member of this project"}), 400
        
        # Check if user is the creator - creator cannot leave
        if user_id == project.get('created_by'):
            return jsonify({"error": "Project creator cannot leave the project"}), 400
        
        # Remove user from project
        result = projects_collection.update_one(
            {"project_id": actual_project_id} if 'project_id' in project else {"_id": ObjectId(project_id)},
            {"$pull": {"users": user_id}}
        )
        
        # Remove project from user's projects
        user_db["UserLogin"].update_one(
            {"UserId": user_id},
            {"$pull": {"ProjectIds": actual_project_id}}
        )
        
        return jsonify({"message": "Successfully left project"})
    except Exception as e:
        print(f"Error leaving project: {e}")
        return jsonify({"error": str(e)}), 400

@app.route('/api/projects/<project_id>/items', methods=['GET'])
def get_project_items(project_id):
    if projects_db is None or db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        # Check if project exists
        project = projects_collection.find_one({"project_id": project_id})
        if not project and ObjectId.is_valid(project_id):
            project = projects_collection.find_one({"_id": ObjectId(project_id)})
            
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Get items from the project
        item_ids = project.get('items', [])
        if not item_ids:
            return jsonify([])
        
        # Convert string IDs to ObjectId if needed
        object_ids = []
        for item_id in item_ids:
            if ObjectId.is_valid(item_id):
                object_ids.append(ObjectId(item_id))
            else:
                object_ids.append(item_id)
        
        # Fetch items from inventory
        items = list(db.inventory.find({"_id": {"$in": object_ids}}))
        
        return jsonify([doc_to_dict(item) for item in items])
    except Exception as e:
        print(f"Error getting project items: {e}")
        return jsonify({"error": str(e)}), 400

@app.route('/api/projects/<project_id>/items', methods=['POST'])
def add_item_to_project(project_id):
    if projects_db is None or db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        data = request.get_json()
        
        if not data.get('item_id'):
            return jsonify({"error": "Required field 'item_id' is missing"}), 400
        
        item_id = data['item_id']
        
        # Check if item exists
        if ObjectId.is_valid(item_id):
            item = db.inventory.find_one({"_id": ObjectId(item_id)})
        else:
            item = db.inventory.find_one({"item_id": item_id})
            
        if not item:
            return jsonify({"error": "Item not found"}), 404
        
        # Check if project exists
        project = projects_collection.find_one({"project_id": project_id})
        if not project and ObjectId.is_valid(project_id):
            project = projects_collection.find_one({"_id": ObjectId(project_id)})
            
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Get actual project ID
        if 'project_id' in project:
            actual_project_id = project['project_id']
        else:
            actual_project_id = project_id
            
        # Check if user is authorized
        if 'user_id' in data:
            user_id = int(data['user_id'])
            if user_id not in project.get('users', []):
                return jsonify({"error": "User is not authorized to add items to this project"}), 403
        
        # Check if item is already in the project
        if item_id in project.get('items', []) or str(item.get('_id')) in project.get('items', []):
            return jsonify({"message": "Item is already in the project"}), 200
        
        # Add item to project
        result = projects_collection.update_one(
            {"project_id": actual_project_id} if 'project_id' in project else {"_id": ObjectId(project_id)},
            {"$push": {"items": str(item.get('_id'))}}
        )
        
        return jsonify({"message": "Item added to project successfully"})
    except Exception as e:
        print(f"Error adding item to project: {e}")
        return jsonify({"error": str(e)}), 400

@app.route('/api/projects/<project_id>/items/<item_id>', methods=['DELETE'])
def remove_item_from_project(project_id, item_id):
    if projects_db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        # Check if project exists
        project = projects_collection.find_one({"project_id": project_id})
        if not project and ObjectId.is_valid(project_id):
            project = projects_collection.find_one({"_id": ObjectId(project_id)})
            
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Get actual project ID
        if 'project_id' in project:
            actual_project_id = project['project_id']
        else:
            actual_project_id = project_id
            
        # Check if user is authorized - get user_id from query parameters
        user_id = request.args.get('user_id')
        if user_id:
            try:
                user_id = int(user_id)
                if user_id not in project.get('users', []):
                    return jsonify({"error": "User is not authorized to remove items from this project"}), 403
            except ValueError:
                return jsonify({"error": "Invalid user ID format"}), 400
        
        # Convert item_id to string to ensure matching
        item_id_str = str(item_id)
        
        # Remove item from project
        result = projects_collection.update_one(
            {"project_id": actual_project_id} if 'project_id' in project else {"_id": ObjectId(project_id)},
            {"$pull": {"items": item_id_str}}
        )
        
        if result.modified_count == 0:
            return jsonify({"error": "Item not found in project"}), 404
        
        return jsonify({"message": "Item removed from project successfully"})
    except Exception as e:
        print(f"Error removing item from project: {e}")
        return jsonify({"error": str(e)}), 400

@app.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    if projects_db is None or user_db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        # Get user_id from query parameters
        user_id = request.args.get('user_id')
        if user_id:
            try:
                user_id = int(user_id)
            except ValueError:
                return jsonify({"error": "Invalid user ID format"}), 400
        
        # Check if project exists
        project = projects_collection.find_one({"project_id": project_id})
        if not project and ObjectId.is_valid(project_id):
            project = projects_collection.find_one({"_id": ObjectId(project_id)})
            
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Check if user is authorized (only creator can delete)
        if user_id and user_id != project.get('created_by'):
            return jsonify({"error": "Only the project creator can delete the project"}), 403
        
        # Get actual project ID
        if 'project_id' in project:
            actual_project_id = project['project_id']
        else:
            actual_project_id = project_id
        
        # Get all users in the project
        users_in_project = project.get('users', [])
        
        # Remove project from all users' ProjectIds
        for user_id in users_in_project:
            user_db["UserLogin"].update_one(
                {"UserId": user_id},
                {"$pull": {"ProjectIds": actual_project_id}}
            )
        
        # Delete the project
        result = projects_collection.delete_one(
            {"project_id": actual_project_id} if 'project_id' in project else {"_id": ObjectId(project_id)}
        )
        
        if result.deleted_count == 0:
            return jsonify({"error": "Project not found"}), 404
            
        return jsonify({"message": "Project deleted successfully"})
    except Exception as e:
        print(f"Error deleting project: {e}")
        return jsonify({"error": str(e)}), 400

@app.route('/api/user/<user_id>/projects', methods=['GET'])
def get_user_projects(user_id):
    if user_db is None or projects_db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        # Convert user_id to int if it's a string
        try:
            user_id = int(user_id)
        except ValueError:
            pass
        
        # Check if user exists
        user = user_db["UserLogin"].find_one({"UserId": user_id})
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get projects from user's ProjectIds
        project_ids = user.get("ProjectIds", [])
        if not project_ids:
            return jsonify([])
        
        # Find all projects that match the user's project IDs
        projects = list(projects_collection.find({"project_id": {"$in": project_ids}}))
        
        return jsonify([doc_to_dict(project) for project in projects])
    except Exception as e:
        print(f"Error getting user projects: {e}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
    #comment to false later
