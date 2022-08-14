from flask import Flask, render_template, request, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import false, null
from sqlalchemy.sql.expression import func, select
from apscheduler.schedulers.background import BackgroundScheduler
from zipfile import ZipFile
import os, re, uuid, threading, time, random, json, unidecode, copy, csv, shutil

db = SQLAlchemy()
sem = threading.Semaphore()
#   RUN ON LOCAL:
#       venv/scripts/activate
#       $env:DATABASE_URL=$(heroku config:get DATABASE_URL -a obrazkovy-dataset)
#       flask run


def create_app():
    app = Flask(__name__)
    DB_URL = os.environ["DATABASE_URL"]
    if DB_URL.startswith("postgres://"):
        DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = "6e2db44e-2b19-4909-93b4-65ca2e10a135"
    db.init_app(app)
    return app


app = create_app()
from models import Image, Http_request, Answer, Answer2, Attribute

if __name__ == "__main__":
    app.run(debug=True)
# Funkce na automatické mazání prošlých http_request
def delete_requests():
    with app.app_context():
        db.session.execute(
            "delete from http_request where timestamp < now() - interval '30 minutes'"
        )
        db.session.commit()
        print("Deleting old requests")


scheduler = BackgroundScheduler()
job = scheduler.add_job(delete_requests, "interval", minutes=30)
scheduler.start()

# Fuknce k prvnímu formuláři
def validate_request_id(data):
    sem.acquire()
    current_request = Http_request.query.filter_by(request_id=data["requestID"]).first()
    if current_request == None or str(current_request.image_id) != data["imageID"]:
        sem.release()
        return False
    else:
        Http_request.query.filter_by(request_id=data["requestID"]).delete()
        db.session.commit()
        sem.release()
        return True


def validate_form(data):
    if data["action"] == "" or data["imageID"] == "" or data["requestID"] == "":
        return False
    if (
        data["atribut-1"].strip()
        or data["atribut-2"].strip()
        or data["atribut-3"].strip()
        or data["atribut-4"].strip()
        or data["atribut-5"].strip()
        or data["atribut-6"].strip()
    ):
        return True
    return False


def new_request(new_image):
    request_id = uuid.uuid4()
    new_http_request = Http_request(request_id=request_id, image_id=new_image)
    db.session.add(new_http_request)
    db.session.commit()
    return request_id


def get_image():
    id_list = []
    images = Image.query.order_by(func.random())
    for image in images:
        id_list.append(image.id)
    id_dict = dict.fromkeys(id_list, 0)

    answers = Answer.query.all()
    for answer in answers:
        id_dict[answer.image_id] += 1
    id_list_sorted = sorted(id_dict.items(), key=lambda item: item[1])
    id_list_filtered = filter(
        lambda item: item[1] == id_list_sorted[0][1], id_list_sorted
    )
    return Image.query.filter_by(id=random.choice(list(id_list_filtered))[0]).first()


def save_answer(data):
    data_attributes = list(data.items())[:6]
    attributes = []
    for value in data_attributes:
        if len(value[1].strip()) != 0:
            attributes.append(value[1].strip())
    answer = Answer(image_id=data["imageID"], attributes=attributes)
    db.session.add(answer)
    db.session.commit()


# Funkce k druhému formuláři
def validate_request_id_2(data):
    sem.acquire()
    current_request = Http_request.query.filter_by(request_id=data["requestID"]).first()
    if current_request == None or str(current_request.image_id) != data["imageID"]:
        sem.release()
        return False
    else:
        attributes = current_request.attributes
        Http_request.query.filter_by(request_id=data["requestID"]).delete()
        db.session.commit()
        sem.release()
        return attributes


def validate_form_2(data):
    if len(data) != 14:
        return False
    for x in data[0:12]:
        if x != "false" and x != "true":
            return False
    return True


def get_image_2():
    id_list = []
    images = Image.query.order_by(func.random())
    for image in images:
        id_list.append(image.id)
    id_dict = dict.fromkeys(id_list, 0)

    answers = Answer2.query.all()
    for answer in answers:
        id_dict[answer.image_id] += 1
    id_list_sorted = sorted(id_dict.items(), key=lambda item: item[1])
    id_list_filtered = filter(
        lambda item: item[1] == id_list_sorted[0][1], id_list_sorted
    )
    return Image.query.filter_by(id=random.choice(list(id_list_filtered))[0]).first()


def get_attributes_2(id):
    attribute_list = []
    attributes = Attribute.query.order_by(func.random())
    for attribute in attributes:
        attribute_list.append(attribute.name)
    attribute_dict = dict.fromkeys(attribute_list, 0)

    answers = Answer2.query.filter_by(image_id=id)
    for answer in answers:
        for attributeT in answer.attributes_true:
            attribute_dict[attributeT] += 1
        for attributeF in answer.attributes_false:
            attribute_dict[attributeF] += 1
    attribute_list_sorted = sorted(attribute_dict.items(), key=lambda item: item[1])
    attribute_list_final = [attribute[0] for attribute in attribute_list_sorted[:12]]

    return attribute_list_final


def new_request_2(new_image):
    request_id = uuid.uuid4()
    attributes = get_attributes_2(new_image)
    new_http_request = Http_request(
        request_id=request_id, image_id=new_image, attributes=attributes
    )
    db.session.add(new_http_request)
    db.session.commit()
    return request_id, attributes


def save_answer_2(attributes, values, id):
    false_list = []
    true_list = []
    for attribute, value in zip(attributes, values):
        if value == "false":
            false_list.append(attribute)
        elif value == "true":
            true_list.append(attribute)
    answer = Answer2(
        image_id=id, attributes_true=true_list, attributes_false=false_list
    )
    db.session.add(answer)
    db.session.commit()


# JSON / CSV / ZIP
def generate_objects_list():
    attributes_list = []
    attributes = Attribute.query.all()
    for attribute in attributes:
        attributes_list.append(attribute.name)
    attributes_dict = {
        new_dict: {"Value": "", True: 0, False: 0} for new_dict in attributes_list
    }

    objects_list = []
    images = Image.query.all()
    for image in images:
        img_dict = image.__dict__
        img_dict.pop("_sa_instance_state")
        img_dict["filename"] = img_dict["link"].split("/")[3]
        img_dict["link"] = img_dict["link"].replace(
            "..", "https://obrazkovy-dataset.herokuapp.com"
        )
        # img_dict['link'] = img_dict['link'].replace("..", request.url_root) DYNAMIC URL
        img_dict["link"] = img_dict["link"].replace(" ", "%20")
        img_dict["attributes"] = copy.deepcopy(attributes_dict)
        objects_list.append(img_dict)
    answers = Answer2.query.all()

    for answer in answers:
        true_answers = answer.attributes_true
        false_answers = answer.attributes_false

        for true_answer in true_answers:
            updated_object = next(
                item for item in objects_list if item["id"] == answer.image_id
            )
            try:
                updated_object["attributes"][true_answer][True] += 1
                updated_object["attributes"][true_answer]["Value"] = round(
                    updated_object["attributes"][true_answer][True]
                    / (
                        updated_object["attributes"][true_answer][True]
                        + updated_object["attributes"][true_answer][False]
                    ),
                    2,
                )
            except Exception:
                pass
        for false_answer in false_answers:
            updated_object = next(
                item for item in objects_list if item["id"] == answer.image_id
            )
            try:
                updated_object["attributes"][false_answer][False] += 1
                updated_object["attributes"][false_answer]["Value"] = round(
                    updated_object["attributes"][false_answer][True]
                    / (
                        updated_object["attributes"][false_answer][True]
                        + updated_object["attributes"][false_answer][False]
                    ),
                    2,
                )
            except Exception:
                pass
    objects_list = sorted(objects_list, key=lambda d: d["id"])

    return objects_list


def generate_objects_min_list():
    objects_list = generate_objects_list()
    objects_min_list = []
    for object in objects_list:
        new_min_object = {}
        new_min_object["id"] = object["id"]
        new_min_object["filename"] = object["filename"]
        new_min_object["link"] = object["link"]
        for key in object["attributes"]:
            new_min_object[key] = object["attributes"][key]["Value"]
        objects_min_list.append(new_min_object)
    return objects_min_list


def generate_json():
    objects_list = generate_objects_list()
    with open("download/dataset.json", "w", encoding="utf8") as outfile:
        json.dump(objects_list, outfile, ensure_ascii=False, indent=4)
    objects_min_list = generate_objects_min_list()
    with open("download/dataset-minimal.json", "w", encoding="utf8") as outfile:
        json.dump(objects_min_list, outfile, ensure_ascii=False, indent=4)
    zipObj = ZipFile("download/dataset-json.zip", "w")
    zipObj.write("download/readme.txt", "readme.txt")
    zipObj.write("download/dataset-minimal.json", "dataset-minimal.json")
    zipObj.write("download/dataset.json", "dataset.json")
    zipObj.close()
    return "dataset.json"


def generate_csv():
    min_csv_list = generate_objects_min_list()
    keys = min_csv_list[0].keys()
    with open("download/dataset.csv", "w", newline="", encoding="utf8") as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(min_csv_list)
    zipObj = ZipFile("download/dataset-csv.zip", "w")
    zipObj.write("download/readme.txt", "readme.txt")
    zipObj.write("download/dataset.csv", "dataset.csv")
    zipObj.close()
    return "dataset.csv"


def generate_picture_zip():
    shutil.make_archive("download/img", "zip", "static/", "img")
    return "img.zip"


def generate_zip():
    with app.app_context():
        generate_json()
        # generate_min_json()
        generate_csv()
        generate_picture_zip()
        zipObj = ZipFile("download/dataset.zip", "w")
        zipObj.write("download/dataset.csv", "dataset.csv")
        zipObj.write("download/dataset.json", "dataset.json")
        zipObj.write("download/img.zip", "img.zip")
        zipObj.write("download/readme.txt", "readme.txt")
        zipObj.close()
        print("All data generated")
        return "dataset.zip"


job = scheduler.add_job(generate_zip, "interval", minutes=30)


# DOWNLOAD PAGES
@app.route("/download_full")
def download_full():
    return send_from_directory("download/", "dataset.zip", as_attachment=True)


@app.route("/download_pictures")
def download_pictures():
    return send_from_directory("download/", "img.zip", as_attachment=True)


@app.route("/download_json")
def download_json():
    return send_from_directory("download/", "dataset-json.zip", as_attachment=True)


@app.route("/download_csv")
def download_csv():
    return send_from_directory("download/", "dataset-csv.zip", as_attachment=True)


# MAIN PAGES
@app.route("/")
def index():
    generate_zip()
    return render_template("index.html")


@app.route("/data")
def data():
    return render_template("data.html")


@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        data = request.form.to_dict()
        if validate_request_id(data) == False:
            flash("Neplatné odeslání formuláře", category="error")
        elif validate_form(data) == False:
            flash("Špatně vyplněný formulář", category="error")
        else:
            save_answer(data)
            flash("Atributy uloženy", category="success")
        if data["action"] == "next":
            new_image = get_image()
        else:
            new_image = Image.query.filter_by(id=data["imageID"]).first()
    if request.method == "GET":
        new_image = get_image()
    request_id = new_request(new_image.id)
    return render_template(
        "form.html",
        current_image=new_image.link,
        image_ID=new_image.id,
        request_ID=request_id,
        author=new_image.author,
        title=new_image.title,
        link=new_image.source,
    )


@app.route("/form2/guide")
def form2_guide():
    return render_template("form2_guide.html")


@app.route("/form2", methods=["GET", "POST"])
def form2():
    if request.method == "POST":
        data = request.form.to_dict()
        attribute_list = validate_request_id_2(data)
        if attribute_list == False:
            flash("Neplatné odeslání formuláře", category="error")
        elif validate_form_2(list(data.values())) == False:
            flash("Špatně vyplněný formulář", category="error")
        else:
            save_answer_2(attribute_list, list(data.values())[0:12], data["imageID"])
    new_image = get_image_2()
    new_request, attributes = new_request_2(new_image.id)
    return render_template(
        "form2.html",
        current_image=new_image.link,
        image_ID=new_image.id,
        request_ID=new_request,
        author=new_image.author,
        title=new_image.title,
        attributes=attributes,
    )