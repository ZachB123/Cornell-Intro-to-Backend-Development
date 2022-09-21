from datetime import datetime
import json


import db
from flask import Flask
from flask import request

DB = db.DatabaseDriver()

app = Flask(__name__)


def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code


def failure_response(data, code=404):
    return json.dumps({"success": False, "error": data}), code


def is_none(*args):
    for val in args:
        if val is None:
            return True
    return False


@app.route("/")
def hello_world():
    return "Hello world!"


@app.route("/api/users/")
def get_all_users():
    return success_response(DB.get_all_users())


@app.route("/api/users/", methods=["POST"])
def create_user():
    body = json.loads(request.data)
    name, username, balance = body.get("name"), body.get("username"), body.get("balance")
    if name is None or username is None:
        return failure_response("not enough information", 400)
    if balance is None:
        balance = 0
    user_id = DB.create_user(name, username, balance)
    return success_response(DB.get_user_by_id(user_id), 201)


@app.route("/api/users/<int:user_id>/")
def get_user_by_id(user_id):
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("user not found")
    return success_response(user)


@app.route("/api/users/<int:user_id>/", methods=["DELETE"])
def delete_user_by_id(user_id):
    user = DB.delete_user_by_id(user_id)
    if user is None:
        return failure_response("user not found")
    return success_response(user)

@app.route("/api/transactions/", methods=["POST"])
def create_transaction():
    body = json.loads(request.data)
    sender_id, receiver_id, amount, accepted = body.get("sender_id"), body.get("receiver_id"), body.get("amount"), body.get("accepted")
    if is_none(sender_id, receiver_id, amount):
        return failure_response("missing fields", 400)
    if accepted is False:
        return failure_response("invalid value for accepted", 400)
    if DB.get_user_by_id(sender_id) is None or DB.get_user_by_id(receiver_id) is None:
        return failure_response("user not found")
    if amount > DB.get_user_by_id(sender_id)["balance"]:
        return failure_response("sender does not have enough money", 403)
    transaction_id = DB.create_transaction(sender_id, receiver_id, amount, accepted)
    if accepted is None:
        return success_response(DB.get_transaction_by_id(transaction_id))
    transaction = DB.complete_transaction(transaction_id, accepted) #accepted must be true here
    return transaction

@app.route("/api/transactions/<int:transaction_id>/", methods=["POST"])
def process_transaction(transaction_id):
    body = json.loads(request.data)
    accepted = body.get("accepted")
    if accepted is None:
        return failure_response("missing field accepted", 400)
    transaction = DB.get_transaction_by_id(transaction_id)
    if transaction is None:
        return failure_response("transaction not found")
    if transaction["accepted"] is not None:
        return failure_response("transaction already has been completed", 403)
    sender_id, receiver_id, amount = transaction.get("sender_id"), transaction.get("receiver_id"), transaction.get("amount")
    if amount > DB.get_user_by_id(sender_id)["balance"]:
        return failure_response("sender does not have enough money", 403)
    return success_response(DB.complete_transaction(transaction_id, accepted))



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
