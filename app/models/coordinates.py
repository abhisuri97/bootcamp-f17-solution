from app import db


class Coordinate(db.Model):
    __tablename__ = 'coordinates'
    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Integer)
    y = db.Column(db.Integer)
    dir = db.Column(db.String(64))
    valid = db.Column(db.Boolean)

    def __init__(self, x, y, dir, valid):
        self.x = x
        self.y = y
        self.dir = dir
        self.valid = valid

    def __repr__(self):
        return '<Coordinate {},{},{},{}>'.format(self.x, self.y,
                                                 self.dir, self.valid)
