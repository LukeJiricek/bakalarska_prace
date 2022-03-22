from flask import Flask,render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func, select
import os


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://tncbhgirdjkurb:5a1c4af375a64ceacbc518fe411d29c244605d1dd6aff78d80489ffd9ce51b4d@ec2-54-208-96-16.compute-1.amazonaws.com:5432/d8lnl8quucc1j8'
    #print(os.environ['DATABASE_URL'])
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

