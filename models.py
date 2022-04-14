from app import db
from sqlalchemy.schema import FetchedValue

class Object(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50), unique=True)
    type = db.Column(db.String(20))
    source = db.Column(db.String(250))
    title = db.Column(db.String(100))
    author = db.Column(db.String(50))

class http_request(db.Model):
    request_id = db.Column(db.String(50), primary_key=True, unique=True)
    image_id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(100), server_default=FetchedValue())