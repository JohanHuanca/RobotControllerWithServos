from models import Movement

class MovementRepository:
    def __init__(self, db):
        self.db = db

    def save(self, name):
        cursor = self.db.conn.execute("INSERT INTO movements (name) VALUES (?)", (name,))
        self.db.conn.commit()
        return cursor.lastrowid

    def updateById(self, id, name):
        self.db.conn.execute("UPDATE movements SET name = ? WHERE id = ?", (name, id))
        self.db.conn.commit()

    def deleteById(self, id):
        self.db.conn.execute("DELETE FROM positions WHERE movement_id = ?", (id,))
        self.db.conn.execute("DELETE FROM movements WHERE id = ?", (id,))
        self.db.conn.commit()

    def findById(self, id):
        cursor = self.db.conn.execute("SELECT id, name FROM movements WHERE id = ?", (id,))
        row = cursor.fetchone()
        if row:
            return Movement(id=row[0], name=row[1])
        return None

    def findByName(self, name):
        cursor = self.db.conn.execute("SELECT id, name FROM movements WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            return Movement(id=row[0], name=row[1])
        return None

    def findAll(self):
        cursor = self.db.conn.execute("SELECT id, name FROM movements")
        rows = cursor.fetchall()
        return [Movement(id=row[0], name=row[1]) for row in rows]
