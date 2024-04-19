# InceptionV3 is a model that use for image recogniztion

from flask import Flask, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import numpy as np
import requests
import tensorflow as tf
from keras.applications import InceptionV3, imagenet_utils
from keras.applications.inception_v3 import preprocess_input
from keras.preprocessing.image import img_to_array
from PIL import Image
from io import BytesIO

LOCALHOST = '0.0.0.0'
PORT = 4000

app = Flask(__name__)
api = Api(app)

# Loading our pre-trained model
pretrained_model = InceptionV3(weights='imagenet')

client = MongoClient('mongodb://image-recognition-mongodb-container:27017')
db = client['image-recognition_db']
users_collection = db['Users']

class Signup(Resource):
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
            "tokens": 5
        })

        messsage = { "message": f"{username} added as a new user" }
        return messsage, 200


class ImageClassification(Resource):
    def post(self):
        user_credentials = request.get_json()
        
        if "username" not in user_credentials or "password" not in user_credentials or "url" not in user_credentials:
            return { "message": "Missing Credentials" }, 400
        
        username = user_credentials['username']
        password = user_credentials['password']     
        url = user_credentials['url']   

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
         
        # Load image from url
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))

        # Pre process the image
        img = img.resize((299, 299))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        # Make prediction
        prediction = pretrained_model.predict(img_array)
        actual_prediction = imagenet_utils.decode_predictions(prediction, top=5)

        res = {}
        for pred in actual_prediction[0]:
            res[pred[1]] = float(pred[2]*100)
        
        users_collection.update_one({ "username": username }, { "$set": { "tokens": user_exists['tokens'] - 1 } })

        return res, 200


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


api.add_resource(Signup, "/signup")
api.add_resource(ImageClassification, "/classification")
api.add_resource(Refill, "/refill")

if __name__ == '__main__':
    app.run(host=LOCALHOST, port=PORT)
