import sqlite3
from datetime import datetime


def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


def parse_row(row, columns):
    parsed_row = {}
    for i in range(len(columns)):
        parsed_row[columns[i]] = row[i]
    return parsed_row


def parse_cursor(cursor, columns):
    return [parse_row(row, columns) for row in cursor]


class DatabaseDriver(object):
    """
    Database driver for the Venmo (Full) app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        self.conn = sqlite3.connect("venmo.db", check_same_thread=False)
        self.create_user_table()
        self.create_txn_table()

    def create_user_table(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                username TEXT NOT NULL,
                balance INTEGER NOT NULL
            );
            """
        )
        self.conn.commit()

    def create_txn_table(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS txn (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                sender_id INTEGER SECONDARY KEY NOT NULL,
                receiver_id SECONDARY KEY INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                accepted BOOLEAN
            );
            """
        )
        self.conn.commit()
    
    def get_all_users(self):
        cursor = self.conn.execute(
            """
            SELECT * FROM users;
            """
        )
        return parse_cursor(cursor, ["id", "name", "username"])

    def create_user(self, name, username, balance):
        cursor = self.conn.execute(
            """
            INSERT INTO users (name, username, balance)
            VALUES (?,?,?);
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
            user = parse_row(row, ["id", "name", "username", "balance"])
            user["transactions"] = self.get_all_transactions_of_user(user_id)
            return user
        return None

    def delete_user_by_id(self, user_id):
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

    def get_all_transactions(self):
        cursor = self.conn.execute(
            """
            SELECT * FROM txn;
            """
        )
        return [{
                "id": row[0],
                "timestamp": row[1],
                "sender_id": row[2],
                "receiver_id": row[3],
                "amount": row[4],
                "accepted": row[5]
            } for row in cursor]

    def get_all_transactions_of_user(self, user_id):
        cursor = self.conn.execute(
            """
            SELECT * FROM txn
            WHERE sender_id=? OR receiver_id=?;
            """,
            (user_id, user_id)
        )
        return [{
                "id": row[0],
                "timestamp": row[1],
                "sender_id": row[2],
                "receiver_id": row[3],
                "amount": row[4],
                "accepted": row[5]
            } for row in cursor]

    def get_transaction_by_id(self, transaction_id):
        cursor = self.conn.execute(
            """
            SELECT * FROM txn
            WHERE id=?;
            """,
            (transaction_id,)
        )
        for row in cursor:
            return parse_row(row, ["id", "timestamp", "sender_id", "receiver_id", "amount", "accepted"])
        return None

    def create_transaction(self, sender_id, receiver_id, amount, accepted):
        cursor = self.conn.execute(
            """
            INSERT INTO txn (sender_id, receiver_id, amount, accepted)
            VALUES (?,?,?,?);
            """,
            (sender_id, receiver_id, amount, accepted)
        )
        self.conn.commit()
        return cursor.lastrowid

    def delete_transaction(self, transaction_id):
        transaction = self.get_transaction_by_id(transaction_id)
        self.conn.execute(
            """
            DELETE FROM txn
            WHERE id=?;
            """,
            (transaction_id,)
        )
        self.conn.commit()
        return transaction

    def complete_transaction(self, transaction_id, accepted):
        transaction = self.get_transaction_by_id(transaction_id)
        if accepted is False:
            self.conn.execute(
                """
                UPDATE txn
                SET timestamp=?, accepted=?
                WHERE id=?;
                """,
                (str(datetime.now()), accepted, transaction_id)
            )
            self.conn.commit()
            return self.get_transaction_by_id(transaction_id)
        amount = transaction["amount"]
        sender_balance = self.get_user_by_id(transaction["sender_id"])["balance"] - amount
        receiver_balance = self.get_user_by_id(transaction["receiver_id"])["balance"] + amount
        timestamp = str(datetime.now())
        self.conn.execute(
            """
            UPDATE txn
            SET timestamp=?,accepted=?
            WHERE id=?;
            """,
            (timestamp, accepted, transaction_id)
        )
        self.conn.commit()
        self.conn.execute(
            """
            UPDATE users
            SET balance=?
            WHERE id=?;
            """,
            (sender_balance, transaction["sender_id"])
        )
        self.conn.commit()
        self.conn.execute(
            """
            UPDATE users
            SET balance=?
            WHERE id=?;
            """,
            (receiver_balance, transaction["receiver_id"])
        )
        self.conn.commit()
        return self.get_transaction_by_id(transaction_id)
        
        

DatabaseDriver = singleton(DatabaseDriver)