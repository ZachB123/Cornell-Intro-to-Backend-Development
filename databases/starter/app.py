import json
from turtle import done
from flask import Flask, request
import db

DB = db.DatabaseDriver()

app = Flask(__name__)


def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code


def failure_response(data, code=404):
    return json.dumps({"success": False, "error": data}), code


@app.route("/")
@app.route("/tasks/")
def get_tasks():
    return success_response(DB.get_all_tasks())


@app.route("/tasks/", methods=["POST"])
def create_task():
    body = json.loads(request.data)
    description = body.get("description")
    if description is not None:
        task_id = DB.insert_task_table(description, False)
        return success_response(DB.get_task_by_id(task_id), 201)
    return failure_response("no description", 400)


@app.route("/tasks/<int:task_id>/")
def get_task(task_id):
    task = DB.get_task_by_id(task_id)
    if task is not None:
        return success_response(task)
    return failure_response("task not found")


@app.route("/tasks/<int:task_id>/", methods=["POST"])
def update_task(task_id):
    body = json.loads(request.data)
    description, done = body.get("description"), body.get("done")
    task = DB.get_task_by_id(task_id)
    if task is None:
        return failure_response("task not found")
    if description is None and done is None:
        return failure_response("Not enough information", 400)
    elif description is None:
        DB.update_task_by_id(task_id, task["description"], done)
    elif done is None:
        DB.update_task_by_id(task_id, description, task["done"])
    else:
        DB.update_task_by_id(task_id, description, done)
    return success_response(DB.get_task_by_id(task_id))



@app.route("/tasks/<int:task_id>/", methods=["DELETE"])
def delete_task(task_id):
    task = DB.get_task_by_id(task_id)
    if task is None:
        return failure_response("task not found")
    DB.delete_task_by_id(task_id)
    return success_response(task)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
