import json

from db import db
from db import Course, Assignment, User
from flask import Flask
from flask import request

app = Flask(__name__)
db_filename = "cms.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code

def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code


@app.route("/api/courses/")
def get_all_courses():
    return success_response([c.serialize() for c in Course.query.all()])

@app.route("/api/courses/", methods=["POST"])
def create_course():
    body = json.loads(request.data)
    code, name = body.get("code"), body.get("name")
    if code is None or name is None:
        return failure_response("missing fields", 400)
    course = Course(code=code, name=name)
    db.session.add(course)
    db.session.commit()
    return success_response(course.serialize(), 201)

@app.route("/api/courses/<int:course_id>/")
def get_course_by_id(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("course not found")
    return success_response(course.serialize())

@app.route("/api/courses/<int:course_id>/", methods=["DELETE"])
def delete_course_by_id(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("course not found")
    db.session.delete(course)
    db.session.commit()
    return success_response(course.serialize())

@app.route("/api/users/", methods=["POST"])
def create_user():
    body = json.loads(request.data)
    name, netid = body.get("name"), body.get("netid")
    if name is None or netid is None:
        return failure_response("missing fields", 400)
    user = User(name=name, netid=netid)
    db.session.add(user)
    db.session.commit()
    return success_response(user.serialize())

@app.route("/api/users/<int:user_id>/")
def get_user_by_id(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("user not found")
    return success_response(user.serialize())

@app.route("/api/courses/<int:course_id>/add/", methods=["POST"])
def add_user_to_course(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("course not found")
    body = json.loads(request.data)
    user_id = body.get("user_id")
    if user_id is None:
        return failure_response("missing field", 400)
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("user not found")
    course.students.append(user)
    db.session.commit()
    return success_response(Course.query.filter_by(id=course_id).first().serialize())

@app.route("/api/courses/<int:course_id>/assignment/", methods=["POST"])
def create_assignement(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("course not found")
    body = json.loads(request.data)
    title, due_date = body.get("title"), body.get("due_date")
    if title is None or due_date is None:
        return failure_response("missing fields")
    assignment = Assignment(title=title, due_date=due_date, course_id=course_id)
    db.session.add(assignment)
    db.session.commit()
    return success_response(assignment.serialize())
    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
