from flask import Flask, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

LOCALHOST = '0.0.0.0'
PORT = 4000

app = Flask(__name__)
api = Api(app)

client = MongoClient('mongodb://bank-mongodb-container:27017')
db = client['bank_db']
users_collection = db['Users']

bank_fee = 1


def check_user_exist(username):
    user_exists = users_collection.find_one({ "username": username })
    if user_exists:
        return True
    return False


def verifyPassword(username, password):
    user_exists = check_user_exist(username)
    if not user_exists:
        return False
    
    user = users_collection.find_one({ "username": username })
    hashed_user_password = user['password']
    
    verify_password = bcrypt.hashpw(password.encode('UTF8'), hashed_user_password) == hashed_user_password

    if verify_password:
        return True
    return False


def fetch_user_detail(username, field):
    username_credential = users_collection.find_one({ "username": username })[field]
    return username_credential


def generate_message(message, status):
    return { "message": message, "status": status }


def update_account(username, action, amount):
    user = users_collection.find_one({ "username": username })
    
    users_collection.update_one({ "username": username }, { "$set": { action: user[action] + amount } })


def verify_params(user_credentials, *params):
    is_valid = True

    for param in params:
        if param not in user_credentials:
            is_valid = False

    return is_valid


class CreateAccount(Resource):
    def post(self):
        user_credentials = request.get_json()
        
        if "username" not in user_credentials or "password" not in user_credentials:
            return { "message": "Missing Credentials" }, 400
        
        username = user_credentials['username']
        password = user_credentials['password']        
        
        user_exists = check_user_exist(username)
        if user_exists:
            return { "message": "User already exists" }, 401

        hash_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        users_collection.insert_one({
            "username": username,
            "password": hash_password,
            "own": 0,
            "debt": 0
        })

        messsage = { "message": f"{username} added as a new user" }
        return messsage, 200


class Add(Resource):
    def post(self):
        user_credentials = request.get_json()

        param_checker = verify_params(user_credentials, 'username', 'password', 'amount')
        if not param_checker:
            return { "message": "Missing Credentials" }, 400

        username = user_credentials['username']
        password = user_credentials['password']  
        amount = user_credentials['amount']

        correct_password = verifyPassword(username, password)
        if not correct_password:
            return generate_message('Invalid password', 302)

        if amount <= 0:
            return generate_message('Invalid amount', 400)

        update_account(username, 'own', amount - bank_fee)
        update_account('bank', 'own', bank_fee)

        return generate_message(f'{amount}$ added to your account', 200)
 

class Transfer(Resource):
    def post(self):
        user_credentials = request.get_json()

        param_checker = verify_params(user_credentials, 'username', 'password', 'to', 'amount')
        if not param_checker:
            return { "message": "Missing Credentials" }, 400

        username = user_credentials['username']
        password = user_credentials['password']
        to = user_credentials['to']
        amount = user_credentials['amount']
        
        correct_password = verifyPassword(username, password)
        if not correct_password:
            return generate_message('Invalid password', 302)
        
        user_cash = fetch_user_detail(username, 'own')

        if user_cash <= 0:
            return generate_message('Out of money', 304)
        
        recipient_exist = check_user_exist(to)
        if not recipient_exist:
            return generate_message('Recipient does not exists')

        update_account(username, 'own', -amount - bank_fee)
        update_account(to, 'own', amount)
        update_account('bank', 'own', bank_fee)

        return generate_message('Transfer completed', 200)
    

class Balance(Resource):
    def post(self):
        user_credentials = request.get_json()

        param_checker = verify_params(user_credentials, 'username')
        if not param_checker:
            return { "message": "Missing Credentials" }, 400
        
        username = user_credentials['username']
        
        user_exists = check_user_exist(username)
        if not user_exists:
            return generate_message('User does not exists', 401)
        
        user = users_collection.find_one({ 'username': username })

        return { "username": username,"own": user['own'], "debt": user['debt'] }, 200
        

class TakeLoan(Resource):
    def post(self):
        user_credentials = request.get_json()

        param_checker = verify_params(user_credentials, 'username', 'password', 'loan_amount')
        if not param_checker:
            return { "message": "Missing Credentials" }, 400

        username = user_credentials['username']
        password = user_credentials['password']
        loan_amount = user_credentials['loan_amount']

        correct_password = verifyPassword(username, password)
        if not correct_password:
            return generate_message('Invalid password', 302)
        
        update_account(username, 'own', loan_amount)
        update_account(username, 'debt', -loan_amount)

        return generate_message('Loan successfully transferd', 200)
    

class PayLoan(Resource):
    def post(self):
        user_credentials = request.get_json()

        param_checker = verify_params(user_credentials, 'username', 'password', 'loan_amount')
        if not param_checker:
            return { "message": "Missing Credentials" }, 400

        username = user_credentials['username']
        password = user_credentials['password']
        loan_amount = user_credentials['loan_amount']

        correct_password = verifyPassword(username, password)
        if not correct_password:
            return generate_message('Invalid password', 302)         

        update_account(username, 'debt', loan_amount)
        update_account(username, 'own', -loan_amount)

        return generate_message('Loan successfully returned', 200)   




api.add_resource(CreateAccount, "/create")
api.add_resource(Add, "/add")
api.add_resource(Transfer, "/transfer")
api.add_resource(Balance, "/balance")
api.add_resource(TakeLoan, "/take_loan")
api.add_resource(PayLoan, "/pay_loan")

if __name__ == '__main__':
    app.run(host=LOCALHOST, port=PORT)
