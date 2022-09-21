import json
from flask import Flask, request
import db

DB = db.DatabaseDriver()

app = Flask(__name__)


def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code


def failure_response(data, code=404):
    return json.dumps({"success": False, "error": data}), code


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
        return failure_response("missing field(s)", 400)
    if balance is None:
        balance = 0
    row_id = DB.create_user(name, username, balance)
    return success_response(DB.get_user_by_id(row_id), 201)


@app.route("/api/user/<int:user_id>")
def get_user(user_id):
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("user does not exist")
    return success_response(user)


@app.route("/api/user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("user not found")
    DB.delete_user(user_id)
    return success_response(user)


@app.route("/api/send/", methods=["POST"])
def send_money():
    body = json.loads(request.data)
    sender_id, receiver_id, amount = body.get("sender_id"), body.get("reciever_id"), body.get("amount")
    if sender_id is None or receiver_id is None or amount is None:
        return failure_response("missing field(s)", 400)
    sender = DB.get_user_by_id(sender_id)
    if sender is None:
        return failure_response("could not find sender")
    receiver = DB.get_user_by_id(receiver_id)
    if receiver is None:
        return failure_response("could not find receiver")
    sender_balance = sender["balance"]
    if amount > sender_balance:
        return failure_response("cannot overdraw balance", 400)
    DB.update_user_by_id(sender_id, sender["name"], sender["username"], sender["balance"] - amount)
    DB.update_user_by_id(receiver_id, receiver["name"], receiver["username"], receiver["balance"] + amount)
    return success_response({
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "amount": amount
    })


@app.route("/api/user/<int:user_id>", methods=["POST"])
def update_user(user_id):
    body = json.loads(request.data)
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("user not found")
    name, username, balance = body.get("name"), body.get("username"), body.get("balance")
    if name is None and username is None and balance is None:
        return failure_response("not enough information", 400)
    if name is None:
        name = user["name"]
    if username is None:
        username = user["username"]
    if balance is None:
        balance = user["balance"]
    DB.update_user_by_id(user_id, name, username, balance)
    return success_response(DB.get_user_by_id(user_id))


@app.route("/api/delete/", methods=["DELETE"])
def reset_database():
    DB.delete_users_table()
    DB.create_users_table()
    return success_response([])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
