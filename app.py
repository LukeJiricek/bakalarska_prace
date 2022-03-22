from flask import Flask,render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func, select
import os
import re


db = SQLAlchemy()

# $env:DATABASE_URL=$(heroku config:get DATABASE_URL -a obrazkovy-dataset)

def create_app():
    app = Flask(__name__)
    DB_URL = os.environ['DATABASE_URL']
    if DB_URL.startswith("postgres://"):
        DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    db.init_app(app)
    return app



app = create_app()
from models import Object
if __name__ == "__main__":
    app.run(debug=True)




@app.route("/")
def index():
    return render_template('index.html')

@app.route("/form", methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        if request.form['action'] == 'reset' :
            data = request.form
            print(data)
        elif request.form['action'] == 'next' :
            data = request.form
            print(data)

    current_image = Object.query.order_by(func.random()).first()

    image_ID=current_image.id
    return render_template('form.html', current_image=current_image.filename, image_ID=image_ID)

