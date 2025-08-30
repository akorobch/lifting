from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Note: The `__tablename__` is explicitly set to 'user' to avoid conflicts
# with the 'user' keyword in some databases.
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(25))
    email = db.Column(db.String(45))
    enabled = db.Column(db.SmallInteger, default=1)

    # Relationship to workouts. 'User' has many 'Workout's.
    workouts = db.relationship('Workout', backref='user', lazy=True)

class Exercise(db.Model):
    __tablename__ = 'exercise'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45))
    description = db.Column(db.String(225))
    date_started = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to sets. 'Exercise' has many 'Set's.
    sets = db.relationship('Set', backref='exercise', lazy=True)

class Workout(db.Model):
    __tablename__ = 'workout'
    id = db.Column(db.Integer, primary_key=True)
    workout_date = db.Column(db.DateTime, nullable=False)
    comment = db.Column(db.String(245))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationship to sets. 'Workout' has many 'Set's.
    sets = db.relationship('Set', backref='workout', lazy=True)

class Set(db.Model):
    __tablename__ = 'set'
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'))
    weight = db.Column(db.Float)
    reps = db.Column(db.Integer)
    comment = db.Column(db.String(245))
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'))