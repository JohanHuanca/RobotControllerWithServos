import sqlite3

class Database:
    def __init__(self, dbName="robot.db"):
        self.conn = sqlite3.connect(dbName)
        self.createTables()

    def createTables(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS movements (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name TEXT NOT NULL UNIQUE
                                )''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS positions (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    "order" INTEGER,
                                    time INTEGER,
                                    angles TEXT NOT NULL,
                                    movement_id INTEGER,
                                    FOREIGN KEY (movement_id) REFERENCES movements(id)
                                )''')
