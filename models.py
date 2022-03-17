from app import db

class Object(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50), unique=True)
    type = db.Column(db.String(20))
    source = db.Column(db.String(250))
    title = db.Column(db.String(100))
    author = db.Column(db.String(50))