from flask import Flask,render_template, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import false, null
from sqlalchemy.sql.expression import func, select
from apscheduler.schedulers.background import BackgroundScheduler
import os, re, uuid, threading, time, random

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
from models import Image, Http_request, Answer, Answer2, Attribute
if __name__ == "__main__":
    app.run(debug=True)

# Funkce na automatické mazání starých http_request
def delete_requests():
    with app.app_context():
        db.session.execute("delete from http_request where timestamp < now() - interval '30 minutes'")
        db.session.commit()
        print("Deleting old requests")
scheduler = BackgroundScheduler()
job = scheduler.add_job(delete_requests, 'interval', minutes=15)
scheduler.start()

# Fuknce k prvnímu formuláři
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

def validate_form(data):
    if data['action'] == '' or data['imageID'] == '' or data['requestID'] == '' :
        return False
    if data['atribut-1'].strip() or data['atribut-2'].strip() or data['atribut-3'].strip() or data['atribut-4'].strip() or data['atribut-5'].strip() or data['atribut-6'].strip() :
        return True
    return False

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

# Funkce k druhému formuláři
def validate_request_id_2(data):
    sem.acquire()
    current_request = Http_request.query.filter_by(request_id=data['requestID']).first()
    if current_request == None or str(current_request.image_id) != data['imageID']:
        sem.release()
        return False
    else :
        attributes = current_request.attributes
        Http_request.query.filter_by(request_id=data['requestID']).delete()
        db.session.commit()
        sem.release()
        return attributes

def validate_form_2(data):
    if len(data) != 12:
        return False
    for x in data[0:10]:
        if x != 'false' and x != 'true':
            return False
    return True

def get_image_2():
    id_list = []
    images = Image.query.order_by(func.random())
    for image in images:
        id_list.append(image.id)
    id_dict = dict.fromkeys(id_list,0)

    answers = Answer2.query.all()
    for answer in answers:
        id_dict[answer.image_id] += 1
    id_list_sorted= sorted(id_dict.items(), key=lambda item: item[1])
    id_list_filtered = filter(lambda item: item[1] == id_list_sorted[0][1], id_list_sorted)
    return Image.query.filter_by(id=random.choice(list(id_list_filtered))[0]).first()

def get_attributes_2(id):
    attribute_list = []
    attributes = Attribute.query.order_by(func.random())
    for attribute in attributes:
        attribute_list.append(attribute.name)
    attribute_dict = dict.fromkeys(attribute_list,0)

    answers = Answer2.query.filter_by(image_id=id)
    for answer in answers:
        for attributeT in answer.attributes_true:
            attribute_dict[attributeT] += 1
        for attributeF in answer.attributes_false:
            attribute_dict[attributeF] += 1

    attribute_list_sorted= sorted(attribute_dict.items(), key=lambda item: item[1])
    attribute_list_final = [attribute[0] for attribute in attribute_list_sorted[:10]]

    return attribute_list_final

def new_request_2(new_image):
    request_id=uuid.uuid4()
    attributes=get_attributes_2(new_image)
    new_http_request = Http_request(request_id=request_id, image_id=new_image, attributes=attributes)
    db.session.add(new_http_request)
    db.session.commit()
    return request_id, attributes

def save_answer_2(attributes, values, id):
    false_list = []
    true_list = []
    for attribute, value in zip(attributes, values):
        if value == 'false':
            false_list.append(attribute)
        elif value == 'true':
            true_list.append(attribute)
    answer = Answer2(image_id=id, attributes_true=true_list, attributes_false=false_list, ip=request.access_route[0])
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
    return render_template('form.html', current_image=new_image.filename, image_ID=new_image.id, request_ID=request_id, author=new_image.author, title=new_image.title, link=new_image.source)

@app.route("/form2", methods=['GET', 'POST'])
def form2():
    if request.method == 'POST':
        data = request.form.to_dict()
        attribute_list = validate_request_id_2(data)
        if attribute_list == False :
            flash("Neplatné odeslání formuláře", category='error')
        elif validate_form_2(list(data.values())) == False :
            flash("Špatně vyplněný formulář", category='error')
        else:
            save_answer_2(attribute_list, list(data.values())[0:10], data['imageID'])

    new_image = get_image_2()
    new_request, attributes=new_request_2(new_image.id)
    return render_template('form2.html', current_image=new_image.filename, image_ID=new_image.id, request_ID=new_request, author=new_image.author, title=new_image.title, attributes=attributes)


