from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='./build', static_url_path='/')
CORS(app, origins=["https://team2-swe-project-9d360b48d501.herokuapp.com/"])

@app.route('/')
def index():
    return app.send_static_file('index.html')

# Get MongoDB URI from environment or use default
mongo_uri = os.getenv("MONGO_URI", "mongodb+srv://swelabteam:swelabteam@inventorydata.i4qua.mongodb.net/?retryWrites=true&w=majority&appName=InventoryData")
print(mongo_uri)

app.config["MONGO_URI"] = mongo_uri
try:
    mongo = PyMongo(app)
    client = mongo.cx
    # Test connection
    db = client['inventory_system'] #db is the inventory_system database, just deal with it I don't want to change working code
    db.command('ping')
    print("MongoDB connection successful!")
    print(f"Available collections: {db.list_collection_names()}")
except Exception as e:
    print(f"MongoDB connection error: {e}")
    # Continue running even with error to see additional debug info

user_db = client["UserInfo"]
projects_db = client["Projects"]

user_collection = user_db["UserLogin"]
projects_collection = projects_db["Project1"]

#password encryption stuff
passN = 2
passD = 1

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

            decryptedpass=decrypt(user.get("Password"),passN,passD)

            if password == decryptedpass:
                return jsonify(user), 200
            else:
                return jsonify({"error": "Incorrect password"}), 401
        else:
            return jsonify({"error": "User does not exist"}), 404
    except Exception as e:
        print("Database error:", e)
        return jsonify({"error": "Server error"}), 500

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
    user = user_db["UserLogin"].find_one({"UserId": int(userId)})
    if not user:
        return jsonify({"error: User not found"}), 404
    
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
            "project_description": project.get("description"),
            "items": itemsson
        }
        projectItems.append(project_data)
    return jsonify(projectItems), 200

#Inventory Routes
@app.route('/api/inventory', methods=['GET'])
def get_all_inventory():
    items = list(db.inventory.find())
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
    
#Projects Calls
@app.route('/api/projects', methods=['GET'])
def get_all_projects():
    try:
        # Get all projects from the Projects.Project1 collection
        projects = list(projects_collection.find())
        result = []

        for project in projects:
            user_ids = project.get("users", [])
            usernames = []
            # Look up each user document by ID and build a list of usernames.
            for uid in user_ids:
                user_doc = user_db["UserLogin"].find_one({"UserId": int(uid)})
                if user_doc:
                    usernames.append(user_doc.get("Username", "Unknown"))
                else:
                    usernames.append("Unknown")

            project_data = {
            "project_name": project.get("project_name", "Unnamed Project"),
            "project_id": project.get("project_id", ""),
            "description": project.get("description", ""),
            "users": usernames, 
            "items": []
            }
            item_ids = project.get("items", [])
            if item_ids:
                items = db.inventory.find({"item_id": {"$in": item_ids}})
                for item in items:
                    item_dict = doc_to_dict(item)
                    project_data["items"].append({
                        "item_name": item_dict.get("item_name", "Unknown Item"),
                        "quantity": item_dict.get("quantity", 0)
                    })

            result.append(project_data)
        return jsonify(result), 200
    except Exception as e:
        print(f"Error fetching projects: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/user/<userId>/myprojects', methods=["GET"])
def get_myprojects(userId):
    user = user_db["UserLogin"].find_one({"UserId": int(userId)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    project_ids = user.get("ProjectIds", [])
    return jsonify(project_ids), 200

@app.route('/api/createprojects', methods=['POST'])
def create_project():
    try:
        data = request.get_json()

        project_name = data.get('project_name')
        project_id = data.get('project_id')
        description = data.get('description', "")
        users = data.get('users', [])
        items = ["T0000", "T0001"]

        if not project_name or not project_id:
            return jsonify({"error": "Missing required fields: project_name or project_id"}), 400

        # Check for duplicate project_id
        existing_project = projects_collection.find_one({'project_id': project_id})
        if existing_project:
            return jsonify({"error": f"Project with ID '{project_id}' already exists."}), 400

        # Build new project document
        new_project = {
            'project_name': project_name,
            'project_id': project_id,
            'description': description,
            'users': users,
            'items': items
        }
        # Insert into database
        result = projects_collection.insert_one(new_project)

        return jsonify({"message": "Project created successfully", "project_id": str(result.inserted_id)}), 201

    except Exception as e:
        print(f"Error creating project: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/user/joinProject', methods=["POST"])
def join_project():
    data = request.get_json()
    userId = data.get('userId')
    projectId = data.get('projectId')
    
    if not userId or not projectId:
        return jsonify({"error": "Missing required fields: userId and projectId"}), 400

    # Find the user document by converting userId to an integer if needed.
    user = user_db["UserLogin"].find_one({"UserId": int(userId)})
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Use $addToSet to add the projectId to the ProjectIds array only if it doesn't exist already.
    user_update = user_db["UserLogin"].update_one(
        {"UserId": int(userId)},
        {"$addToSet": {"ProjectIds": projectId}}
    )
    project_update = projects_collection.update_one(
        {"project_id": projectId},
        {"$addToSet": {"users": int(userId)}}
    )
    
    if user_update.modified_count or project_update.modified_count:
        return jsonify({"message": "Project joined successfully", "projectId": projectId}), 200
    else:
        # If no changes were made, then the project was likely already joined.
        return jsonify({"message": "Project already joined", "projectId": projectId}), 200


@app.route('/api/user/leaveProject', methods=["POST"])
def leave_project():
    data = request.get_json()
    userId = data.get('userId')
    projectId = data.get('projectId')
    
    if not userId or not projectId:
        return jsonify({"error": "Missing required fields: userId and projectId"}), 400

    # Find the user document
    user = user_db["UserLogin"].find_one({"UserId": int(userId)})
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Use $pull to remove the projectId from the ProjectIds array.
    user_update = user_db["UserLogin"].update_one(
        {"UserId": int(userId)},
        {"$pull": {"ProjectIds": projectId}}
    )
    
    # Update the project document by removing the userId from the users array.
    project_update = projects_collection.update_one(
        {"project_id": projectId},
        {"$pull": {"users": int(userId)}}
    )
    
    if user_update.modified_count or project_update.modified_count:
        return jsonify({"message": "Project left successfully", "projectId": projectId}), 200
    else:
        # This might mean the project id wasn't in the user's project list.
        return jsonify({"message": "Project was not joined", "projectId": projectId}), 200

@app.errorhandler(404)
def not_found(e):
    return app.send_static_file('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, port=os.environ.get('PORT', 80))