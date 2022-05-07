from sqlalchemy import ForeignKey
from app import db
from sqlalchemy.schema import FetchedValue

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50), unique=True)
    type = db.Column(db.String(20))
    source = db.Column(db.String(250))
    title = db.Column(db.String(100))
    author = db.Column(db.String(50))
    answer = db.relationship("Answer")

class Http_request(db.Model):
    request_id = db.Column(db.String(50), primary_key=True, unique=True)
    image_id = db.Column(db.Integer)
    timestamp = db.Column(db.String(100), server_default=FetchedValue())
    attributes = db.Column(db.ARRAY(db.String))

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    attributes = db.Column(db.ARRAY(db.String))
    ip = db.Column(db.String(45))
    timestamp = db.Column(db.String(100), server_default=FetchedValue())

class Answer2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    attributes_true = db.Column(db.ARRAY(db.String))
    attributes_false = db.Column(db.ARRAY(db.String))
    ip = db.Column(db.String(45))
    timestamp = db.Column(db.String(100), server_default=FetchedValue())

class Attribute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    type = db.Column(db.String(50))