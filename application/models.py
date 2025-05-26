from datetime import datetime, timezone
from . import db

class StudyAbroad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    tuition = db.Column(db.Float)
    living_cost = db.Column(db.Float)
    total = db.Column(db.Float)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc) )

    def __repr__(self):
        return 'Task %r' % self.id
