from pydoc import describe
from unicodedata import category
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# implement database model classes
association_table = db.Table(
    "association", #name of join table
    db.Column("task_id", db.Integer, db.ForeignKey("task.id")), #column of task id
    db.Column("category_id", db.Integer, db.ForeignKey("category.id")) # column of category id
)

# model for main information
# db.Table for like joins
class Task(db.Model): #classes are used for tables
    __tablename__ = "task"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False)
    done = db.Column(db.Boolean, nullable=False)
    # makes the Task table have a relationship with the subtask table and when a task is deleted it cascades to the subtask
    # also creates field to get subtasks from a task object
    subtasks = db.relationship("Subtask", cascade="delete") #name of class very weird
    categories = db.relationship("Category", secondary=association_table, back_populates="task")

    def init(self, **kwargs):
        #kwargs is dictionary
        self.description = kwargs.get("description")
        self.done = kwargs.get("done")

    def serialize(self):
        #converts to dictionary
        return {
            "id": self.id,
            "description": self.description,
            "done": self.done,
            "subtasks": [s.serialize() for s in self.subtasks],
            "categories": [c.serialize() for c in self.categories]
            }


class Subtask(db.Model):
    __tablename__ = "subtask"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Boolean, nullable=False)
    done = db.Column(db.Boolean, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"))

    def __init__(self, **kwargs):
        self.description = kwargs.get("description")
        self.done = kwargs.get("done")
        self.task_id = kwargs.get("task_id")

    def serialize(self):
        return {
            "id": self.id,
            "description": self.description,
            "done": self.done,
        }

class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False)
    color = db.Column(db.String, nullable=False)
    tasks = db.relationship("Task", secondary=association_table, back_populates="categories")

    def __init__(self, **kwargs):
        self.description = kwargs.get("description")
        self.color = kwargs.get("color")

    def serialize(self):
        return {
            "id": self.id,
            "description": self.description,
            "color": self.color
        }
