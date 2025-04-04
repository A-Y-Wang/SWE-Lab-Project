from flask import Flask, request, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

uri = "mongodb+srv://swelabteam:0njGARlJosA7m0B4@userstuff.vmqiy.mongodb.net/?retryWrites=true&w=majority&appName=UserStuff"

client = MongoClient(uri,server_api=ServerApi('1'))
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    database = client["UserStuff"]
    collection = database["UserLogin"]

except Exception as e:
    print(e)

@app.route('/signup',methods=['POST'])
def createCollection():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')   
        if not username or not password:
            return jsonify({"error": "missing user or password"}), 400 
        existing_user = collection.find_one({"Username":username})
        if existing_user:
            return jsonify({"error":"user already exists"}),409
        doc = {
            "Username":username,
            "Password":password,
            "UserId": collection.count_documents({}) + 1,
            "ProjectIds":[]
        }
        collection.insert_one(doc)
        return jsonify({"message":"successfully registered", "redirect":"/checkout"}),201

    except Exception as e:
        print("error:",e)
        return jsonify({"error": "server error"}), 500

def get_database():
    client = MongoClient(uri,server_api=ServerApi('1'))
    return client["UserStuff"], client

@app.route('/login', methods=['POST'])
def login():
    
    # database, client = get_database()
    # collection = database["UserLogin"]
    
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({"error": "Missing user or pass"}), 400
        user = collection.find_one({"Username": username})
        if user:
            if password == user.get("Password"):
                return jsonify({"message":"Login success","redirect":"/checkout"}),200
            else:
                return jsonify({"error":"Incorrect password"}),401
        else:
            return jsonify({"error":"User DNE"}),404

    except Exception as e:
        print("database error:",e)
        return jsonify({"error":"server error"}),500
    
if __name__ == "__main__":
    try:
        app.run(debug=True)
    finally:
        client.close()

# createCollection()
