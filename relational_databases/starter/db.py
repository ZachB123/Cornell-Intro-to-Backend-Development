import sqlite3


def parse_row(row, columns):
    parsed_row = {}
    for i in range(len(columns)):
        parsed_row[columns[i]] = row[i]
    return parsed_row


def parse_cursor(cursor, columns):
    return [parse_row(row, columns) for row in cursor]


class DatabaseDriver(object):
    """
    Database driver for the Task app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        """
        Secures a connection with the database and stores it into the
        instance variable `conn`
        """
        self.conn = sqlite3.connect("todo.db", check_same_thread=False)
        self.create_task_table()
        self.create_subtask_table()

    # -- TASKS -----------------------------------------------------------

    def create_task_table(self):
        """
        Using SQL, creates a task table
        """
        try:
            self.conn.execute(
                """
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    done INTEGER NOT NULL
                );
            """
            )
        except Exception as e:
            print(e)

    def delete_task_table(self):
        """
        Using SQL, deletes a task table
        """
        self.conn.execute("DROP TABLE IF EXISTS tasks;")

    def get_all_tasks(self):
        """
        Using SQL, gets all tasks in the task table
        """
        cursor = self.conn.execute("SELECT * FROM tasks;")
        return parse_cursor(cursor, ["id", "description", "done"])


    def insert_task_table(self, description, done):
        """
        Using SQL, adds a new task in the task table
        """
        cursor = self.conn.execute("INSERT INTO tasks (description, done) VALUES (?, ?);", (description, done))
        self.conn.commit()
        return cursor.lastrowid

    def get_task_by_id(self, id):
        """
        Using SQL, gets a task by id
        """
        cursor = self.conn.execute("SELECT * FROM tasks WHERE id = ?;", (id,))
        for row in cursor:
            return parse_row(row, ["id", "description", "done"])
        return None

    def update_task_by_id(self, id, description, done):
        """
        Using SQL, updates a task by id
        """
        self.conn.execute(
            """
            UPDATE tasks
            SET description = ?, done = ?
            WHERE id = ?;
        """,
            (description, done, id),
        )
        self.conn.commit()

    def delete_task_by_id(self, id):
        """
        Using SQL, deletes a task by id
        """
        self.conn.execute(
            """
            DELETE FROM tasks
            WHERE id = ?;
        """,
            (id,),
        )
        self.conn.commit()

#-- SUBTASKS --------------------------------------------------------

    def create_subtask_table(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS subtask (
            id INTEGER PRIMARY KEY,
            description TEXT NOT NULL,
            done BOOLEAN NOT NULL,
            task_id INTEGER NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
            );
            """
        )
        self.conn.commit()

    def get_all_subtasks(self):
        cursor = self.conn.execute(
            """
            SELECT * FROM subtask;
            """
        )
        subtasks = parse_cursor(cursor, ["id", "description", "done", "task_id"])
        return subtasks

    def insert_subtask(self, description, done, task_id):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO subtask (description, done, task_id)
            VALUES (?,?,?);
            """,
            (description, done, task_id)
        )
        self.conn.commit();
        return cursor.lastrowid

    def get_subtask_by_id(self, subtask_id):
        cursor = self.conn.execute(
            """
            SELECT * FROM subtask WHERE id=?;
            """,
            (subtask_id,)
        )
        for row in cursor:
            return parse_row(row, ["id", "description", "done", "task_id"])
        return None

    def get_subtasks_of_task(self, task_id):
        cursor = self.conn.execute(
            """
            SELECT * FROM subtask WHERE task_id=?;
            """,
            (task_id,)
        )
        subtasks = parse_cursor(cursor, ["id", "description", "done", "task_id"])
        return subtasks


    