from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#courses users assignments
#users can be students and instructors
#courses and students many to many
#courses and instructors many to many
#courses and assignments one to many
#users and assignements are serialized without course field


courses_users_association = db.Table(
    "courses_users_association",
    db.Column("course_id", db.Integer, db.ForeignKey("course.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"))
)

#courses
class Course(db.Model):
    __tablename__ = "course"
    id = db.Column(db.Integer, primary_key=True)
    #code is the number of the class like CS 1998
    code = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    assignments = db.relationship("Assignment", cascade="delete")
    students = db.relationship("User", secondary=courses_users_association, back_populates="courses")

    def __init__(self, **kwargs):
        self.code = kwargs.get("code")
        self.name = kwargs.get("name")
        
    def serialize(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "assignments": [a.serialize() for a in self.assignments],
            "students": [s.serialize_no_courses() for s in self.students]
        }

    def serialize_for_user(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
        }


class Assignment(db.Model):
    __tablename__ = "assignment"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    #due_date is in seconds since epoch
    due_date = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"))

    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.due_date = kwargs.get("due_date")
        self.course_id = kwargs.get("course_id")

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "due_date": self.due_date,
            "course_id": self.course_id
        }


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    netid = db.Column(db.String, nullable=False)
    courses = db.relationship("Course", secondary=courses_users_association)

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.netid = kwargs.get("netid")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid,
            "courses": [c.serialize_for_user() for c in self.courses]
        }

    def serialize_no_courses(self):
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid,
        }
