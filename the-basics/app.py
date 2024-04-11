from flask import Flask, request, jsonify

LOCALHOST = '127.0.0.1'
PORT = 4000
app = Flask(__name__)

@app.route('/add', methods=['POST'])
def add_nums():
    user_numbers = fetch_numbers()

    if user_numbers == False:
        return { "message": "Missing parameter" }, 301

    result = user_numbers['num1'] + user_numbers['num2']

    return jsonify(result), 200

@app.route('/subtract', methods=['POST'])
def subtract_nums():
    user_numbers = fetch_numbers()

    if user_numbers == False:
        return { "message": "Missing parameter" }, 301
    
    result = user_numbers['num1'] - user_numbers['num2']

    return jsonify(result), 200

@app.route('/divide', methods=['POST'])
def divide_nums():
    user_numbers = fetch_numbers()

    if user_numbers == False:
        return { "message": "Missing parameter" }, 301

    result = user_numbers['num1'] / user_numbers['num2']

    return jsonify(result), 200

@app.route('/multiply', methods=['POST'])
def multiply_nums():
    user_numbers = fetch_numbers()
    
    if user_numbers == False:
        return { "message": "Missing parameter" }, 301

    result = user_numbers['num1'] * user_numbers['num2']
    
    return jsonify(result), 200

def fetch_numbers():
    data = request.get_json()

    if "num1" not in data or "num2" not in data:
        return False

    num1 = data["num1"]
    num2 = data["num2"]

    return { "num1": num1, "num2": num2 }

if __name__ == '__main__':
    app.run(host=LOCALHOST, port=PORT)