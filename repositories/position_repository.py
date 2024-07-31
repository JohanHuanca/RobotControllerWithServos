import json
from models import Position

class PositionRepository:
    def __init__(self, db):
        self.db = db

    def save(self, order, time, angles, movement_id):
        angles_json = json.dumps(angles)
        cursor = self.db.conn.execute(
            'INSERT INTO positions ("order", time, angles, movement_id) VALUES (?, ?, ?, ?)',
            (order, time, angles_json, movement_id)
        )
        self.db.conn.commit()
        return cursor.lastrowid

    def updateById(self, id, time, angles):
        angles_json = json.dumps(angles)
        self.db.conn.execute(
            'UPDATE positions SET time = ?, angles = ? WHERE id = ?',
            (time, angles_json, id)
        )
        self.db.conn.commit()

    def deleteById(self, id):
        self.db.conn.execute('DELETE FROM positions WHERE id = ?', (id,))
        self.db.conn.commit()

    def decrementOrder(self, order, movement_id):
        self.db.conn.execute(
            'UPDATE positions SET "order" = "order" - 1 WHERE "order" > ? AND movement_id = ?',
            (order, movement_id)
        )
        self.db.conn.commit()

    def swapPositions(self, id1, order1, id2, order2):
        self.db.conn.execute(
            'UPDATE positions SET "order" = ? WHERE id = ?',
            (order2, id1)
        )
        self.db.conn.execute(
            'UPDATE positions SET "order" = ? WHERE id = ?',
            (order1, id2)
        )
        self.db.conn.commit()

    def swapWithPrevious(self, id, order, movement_id):
        cursor = self.db.conn.execute(
            'SELECT id, "order" FROM positions WHERE "order" = ? AND movement_id = ?',
            (order - 1, movement_id)
        )
        previous_position = cursor.fetchone()
        if previous_position:
            previous_id, previous_order = previous_position
            self.swapPositions(id, order, previous_id, previous_order)

    def swapWithNext(self, id, order, movement_id):
        cursor = self.db.conn.execute(
            'SELECT id, "order" FROM positions WHERE "order" = ? AND movement_id = ?',
            (order + 1, movement_id)
        )
        next_position = cursor.fetchone()
        if next_position:
            next_id, next_order = next_position
            self.swapPositions(id, order, next_id, next_order)
    
    def findMaxOrder(self, movement_id):
        cursor = self.db.conn.execute(
            'SELECT MAX("order") FROM positions WHERE movement_id = ?',
            (movement_id,)
        )
        max_order = cursor.fetchone()[0]
        return max_order

    def findById(self, id):
        cursor = self.db.conn.execute('SELECT id, "order", time, angles, movement_id FROM positions WHERE id = ?', (id,))
        row = cursor.fetchone()
        if row:
            return Position(id=row[0], order=row[1], time=row[2], angles=json.loads(row[3]), movement_id=row[4])
        return None

    def findAll(self):
        cursor = self.db.conn.execute('SELECT id, "order", time, angles, movement_id FROM positions')
        rows = cursor.fetchall()
        return [Position(id=row[0], order=row[1], time=row[2], angles=json.loads(row[3]), movement_id=row[4]) for row in rows]

    def findAllByMovementId(self, movement_id):
        cursor = self.db.conn.execute('SELECT id, "order", time, angles, movement_id FROM positions WHERE movement_id = ? ORDER BY "order"', (movement_id,))
        rows = cursor.fetchall()
        return [Position(id=row[0], order=row[1], time=row[2], angles=json.loads(row[3]), movement_id=row[4]) for row in rows]
