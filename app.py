from flask import Flask,render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func, select
from os import path

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    create_database(app)
    return app

def create_database(app):
    if not path.exists(DB_NAME):
        db.create_all(app=app)
        print('Created Database!')


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

