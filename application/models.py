from . import db

class StudyAbroad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    tuition = db.Column(db.Float)
    living_cost = db.Column(db.Float)
    total = db.Column(db.Float)
