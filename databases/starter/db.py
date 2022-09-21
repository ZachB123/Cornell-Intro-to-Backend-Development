import os
import sqlite3

# From: https://goo.gl/YzypOI
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    """
    Database driver for the Task app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        self.conn = sqlite3.connect("todo.db", check_same_thread=False)
        self.create_task_table()

    def create_task_table(self):
        try:
            self.conn.execute(
                """
                CREATE TABLE task(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                done INTEGER NOT NULL
                );
                """
            )
            self.conn.commit()
        except Exception as e:
            print(e)

    def delete_task_table(self):
        self.conn.execute(
            """
            DROP TABLE IF EXISTS task;
            """
        )
        self.conn.commit()
        
    def get_all_tasks(self):
        #cursor is sqlite3 object
        cursor = self.conn.execute(
            """
            SELECT * FROM task;
            """
        )
        tasks = []
        for row in cursor:
            tasks.append(
                {
                    "id": row[0],
                    "description": row[1],
                    "done": bool(row[2])
                }
            )
        #no need to commit because have not changed anything
        return tasks

    def insert_task_table(self, description, done):
        #self.conn.execute() grabs the cursor first then runs execute on it
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO task (description, done)
            VALUES (?, ?);
            """,
            (description, done)
        )
        self.conn.commit()
        return cursor.lastrowid #this is why we used a cursor

    def get_task_by_id(self, id):
        cursor = self.conn.execute(
            """
            SELECT * FROM task WHERE id=?;
            """,
            (id,)
        )
        for row in cursor:
            return {
                "id": row[0],
                "description": row[1],
                "done": bool(row[2])
            }
        return None

    def update_task_by_id(self, id, description, done):
        self.conn.execute(
            """
            UPDATE Task
            SET description=?, done=?
            WHERE id=?;
            """,
            (description, done, id)
        )
        self.conn.commit()

    def delete_task_by_id(self, id):
        self.conn.execute(
            """
            DELETE FROM task
            WHERE id=?;
            """,
            (id,)
        )
        self.conn.commit()
        


# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)
