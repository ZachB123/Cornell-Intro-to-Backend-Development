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
    Database driver for the Venmo app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        self.conn = sqlite3.connect("venmo.db", check_same_thread=False)
        self.create_users_table()
    
    def create_users_table(self):
        try:
            self.conn.execute(
                """
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    username TEXT NOT NULL,
                    balance INTEGER
                );
                """
            )
            self.conn.commit()
        except Exception as e:
            print(e)

    def delete_users_table(self):
        self.conn.execute(
            """
            DROP TABLE IF EXISTS users;
            """
        )
        self.conn.commit()

    def get_all_users(self):
        cursor = self.conn.execute(
            """
            SELECT * FROM users;
            """
        )
        users = [{
            "id": row[0],
            "name": row[1],
            "username": row[2]
            }
            for row in cursor
        ]
        return users

    def create_user(self, name, username, balance):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (name, username, balance)
            VALUES (?, ?, ?);
            """,
            (name, username, balance)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_user_by_id(self, user_id):
        cursor = self.conn.execute(
            """
            SELECT * FROM users WHERE id=?;
            """,
            (user_id,)
        )
        for row in cursor:
            return {
                "id": row[0],
                "name": row[1],
                "username": row[2],
                "balance": row[3]
            }
        return None

    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        self.conn.execute(
            """
            DELETE FROM users 
            WHERE id=?;
            """,
            (user_id,)
        )
        self.conn.commit()
        return user

    def update_user_by_id(self, user_id, name, username, balance):
        self.conn.execute(
            """
            UPDATE users
            SET name=?, username=?, balance=?
            WHERE id=?;
            """,
            (name, username, balance, user_id)
        )
        self.conn.commit()


DatabaseDriver = singleton(DatabaseDriver)