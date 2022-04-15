from flask import Flask,render_template, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import null
from sqlalchemy.sql.expression import func, select
from apscheduler.schedulers.background import BackgroundScheduler
import os, re, uuid, threading, time

db = SQLAlchemy()
sem = threading.Semaphore()
#   RUN ON LOCAL:
#       $env:DATABASE_URL=$(heroku config:get DATABASE_URL -a obrazkovy-dataset)

def create_app():
    app = Flask(__name__)
    DB_URL = os.environ['DATABASE_URL']
    if DB_URL.startswith("postgres://"):
        DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    app.secret_key = '6e2db44e-2b19-4909-93b4-65ca2e10a135'
    db.init_app(app)
    return app

app = create_app()
from models import Image, Http_request, Answer
if __name__ == "__main__":
    app.run(debug=True)

def delete_requests():
    with app.app_context():
        db.session.execute("delete from http_request where timestamp < now() - interval '30 minutes'")
        db.session.commit()
        print("Deleting old requests")
# Automatické mazání starých requests
scheduler = BackgroundScheduler()
job = scheduler.add_job(delete_requests, 'interval', minutes=15)
scheduler.start()

def validate_form(data):
    if data['action'] == '' or data['imageID'] == '' or data['requestID'] == '' :
        return False
    if data['atribut-1'].strip() or data['atribut-2'].strip() or data['atribut-3'].strip() or data['atribut-4'].strip() or data['atribut-5'].strip() or data['atribut-6'].strip() :
        return True
    return False

def validate_request_id(data):
    sem.acquire()
    current_request = Http_request.query.filter_by(request_id=data['requestID']).first()
    if current_request == None or str(current_request.image_id) != data['imageID']:
        sem.release()
        return False
    else :
        Http_request.query.filter_by(request_id=data['requestID']).delete()
        db.session.commit()
        sem.release()
        return True

def new_request(new_image):
    request_id=uuid.uuid4()
    new_http_request = Http_request(request_id=request_id, image_id=new_image)
    db.session.add(new_http_request)
    db.session.commit()
    return request_id

def save_answer(data):
    data_attributes = list(data.items())[:6]
    attributes = []
    for value in data_attributes:
        if len(value[1].strip()) != 0 :
            attributes.append(value[1].strip())
    answer = Answer(image_id=data['imageID'], attributes=attributes, ip=request.access_route[0])
    db.session.add(answer)
    db.session.commit()


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/form", methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        data = request.form.to_dict()
        if validate_request_id(data) == False :
            flash("Neplatné odeslání formuláře", category='error')
        elif validate_form(data) == False :
            flash("Špatně vyplněný formulář", category='error')
        else :
            save_answer(data)
            flash("Atributy uloženy", category='success')

        if data['action'] == 'next' :
            new_image = Image.query.order_by(func.random()).first()
        else:
            new_image = Image.query.filter_by(id=data['imageID']).first()

    if request.method == 'GET':
        new_image = Image.query.order_by(func.random()).first()

    request_id=new_request(new_image.id)
    return render_template('form.html', current_image=new_image.filename, image_ID=new_image.id, request_ID=request_id)

