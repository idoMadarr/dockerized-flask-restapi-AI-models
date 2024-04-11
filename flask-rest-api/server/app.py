from flask import Flask, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import sys

# Local device host
# LOCALHOST = '127.0.0.1'
# Dcoker host
LOCALHOST = '0.0.0.0'
PORT = 4000

app = Flask(__name__)
api = Api(app)

# Printing dev logs form the container
sys.stdout = sys.stderr = open('/dev/stdout', 'w')

client = MongoClient('mongodb://mongodb-container:27017/')
db = client['sentences_db']
sentences_collection = db['sentences']
users_collection = db['Users']

def valid_password(current_user, password):
    user_password = current_user['password']

    if bcrypt.hashpw(password.encode('UTF8'), user_password) == user_password:
        return True
    else:
        return False
    
def check_tokens(current_user):
    user_tokens = current_user['tokens']

    if user_tokens >= 1:
        return True
    else:
        return False
    

class Signup(Resource):
    def post(self):
        user_credentials = request.get_json()
        
        if "username" not in user_credentials or "password" not in user_credentials:
            return { "message": "Missing Credentials" }
        
        username = user_credentials['username']
        password = user_credentials['password']

        hash_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        users_collection.insert_one({
            "username": username,
            "password": hash_password,
            "sentence": "",
            "tokens": 6
        })

        messsage = { "message": f"{username} added as a new user" }
        return messsage, 200


class Store(Resource):
    def post(self):
        user_credentials = request.get_json()

        if "username" not in user_credentials or "password" not in user_credentials:
            return { "message": "Missing Credentials" }
        
        username = user_credentials['username']
        password = user_credentials['password']
        sentence = user_credentials['sentence']

        current_user = users_collection.find_one({ "username": username })

        if not current_user:
            return { "message": "Missing Credentials" }, 302

        isValid = valid_password(current_user, password)

        if not isValid:
            return { "message": "Password Error" }, 401
        
        token_exists = check_tokens(current_user)

        if token_exists:
            users_collection.update_one({ "username": username }, { "$set": { "tokens": current_user['tokens'] - 1, "sentence": sentence } })
            return { "message": f"Saving sentence to {username}" } ,200
        
        # Make the user pay 
  

class Users(Resource):
    def post(self):
        data = users_collection.find()
        
        res = []
        for value in list(data):
            res.append({ "username": value['username'], "tokens": value['tokens'], "sentence": value['sentence'] })

        return { "users": res }, 200 


api.add_resource(Users, "/users")
api.add_resource(Signup, "/signup")
api.add_resource(Store, "/store")

if __name__ == '__main__':
    app.run(host=LOCALHOST, port=PORT)

