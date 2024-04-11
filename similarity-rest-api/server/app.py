from flask import Flask, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import spacy
import sys

LOCALHOST = '0.0.0.0'
PORT = 4000

app = Flask(__name__)
api = Api(app)
sys.stdout = sys.stderr = open('/dev/stdout', 'w')

client = MongoClient('mongodb://similarity-mongodb-container:27017/')
db = client['similarity_db']
users_collection = db['Users']
    

class Register(Resource):
    def post(self):
        user_credentials = request.get_json()
        
        if "username" not in user_credentials or "password" not in user_credentials:
            return { "message": "Missing Credentials" }, 400
        
        username = user_credentials['username']
        password = user_credentials['password']

        user_exists = users_collection.find_one({ "username": username })
        if user_exists:
            return { "message": "User already exists" }, 401

        hash_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        users_collection.insert_one({
            "username": username,
            "password": hash_password,
            "tokens": 6
        })

        messsage = { "message": f"{username} added as a new user" }
        return messsage, 200
    

class CompereDocs(Resource):
    def post(self):

        user_credentials = request.get_json()

        if "username" not in user_credentials or "password" not in user_credentials or "doc_1" not in user_credentials or "doc_2" not in user_credentials:
            return { "message": "Missing Credentials" }, 400

        username = user_credentials['username']
        password = user_credentials['password']
        doc_1 = user_credentials['doc_1']
        doc_2 = user_credentials['doc_2']

        user_exists = users_collection.find_one({ "username": username })

        if not user_exists:
            return { "message": "Please signup before using this service" }, 401
        
        user_password = user_exists['password']
        verify_password = bcrypt.hashpw(password.encode('UTF8'), user_password) == user_password
        if not verify_password:
            return { "message": "Incorrect password, please try again" }, 400
    
        user_tokens = user_exists['tokens']
        if user_tokens == 0:
            return { "message": "Out of tokens" }, 400
        
        nlp = spacy.load('en_core_web_sm')
        text1 = nlp(doc_1)
        text2 = nlp(doc_2)

        similarity_ratio = text1.similarity(text2)

        users_collection.update_one({ "username": username }, { "$set": { "tokens": user_exists['tokens'] - 1 } })

        return { "results": similarity_ratio }, 200        


class Refill(Resource):
    def post(self):
        user_credentials = request.get_json()
        
        if "username" not in user_credentials or "admin_password" not in user_credentials or "refill_amount" not in user_credentials:
            return { "message": "Missing Credentials" }, 400
        
        username = user_credentials['username']
        admin_password = user_credentials['admin_password']
        refill_amount = user_credentials['refill_amount']

        user_exists = users_collection.find_one({ "username": username })
        
        if not user_exists:
            return { "message": "User not found" }, 400


        correct_password = "123123"

        if admin_password != correct_password:
            return { "message": "Invalid admin password" }, 400
        
        users_collection.update_one({ "username": username }, { "$set": { "tokens": user_exists['tokens'] + refill_amount } })

        return { "message": "Refilled successfully" }, 200


api.add_resource(Register, "/register")
api.add_resource(CompereDocs, "/compere")
api.add_resource(Refill, "/refill")

if __name__ == '__main__':
    app.run(host=LOCALHOST, port=PORT)
