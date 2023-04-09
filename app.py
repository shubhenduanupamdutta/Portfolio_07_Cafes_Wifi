from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField, SelectField, TextAreaField
from wtforms.validators import URL, InputRequired
from datetime import datetime

# Initialize Flask App
app = Flask(__name__)
app.secret_key = 'cc01ff520e914e64639c81957e91aa88b17076f648f4e0560011e3bb3cd88cf8'

# Initialize Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)

# Initialize Bootstrap
bootstrap = Bootstrap5()
bootstrap.init_app(app)


# Initialize Cafe Add form
class CafeAddForm(FlaskForm):
    name = StringField(label='Cafe Name', validators=[InputRequired()])
    map_url = URLField(label='Map URL', validators=[InputRequired(), URL()])
    img_url = URLField(label='Image URL', validators=[InputRequired(), URL()])
    location = StringField(label='Location', validators=[InputRequired()])
    seats = SelectField(label='Seats', choices=['Yes', 'No'], validators=[InputRequired()])
    has_toilet = SelectField(label='Has Toilet', choices=['Yes', 'No'], validators=[InputRequired()])
    has_sockets = SelectField(label='Has Sockets', choices=['Yes', 'No'], validators=[InputRequired()])
    has_wifi = SelectField(label='Has WiFi', choices=['Yes', 'No'], validators=[InputRequired()])
    can_take_calls = SelectField(label='Can Take Calls', choices=['Yes', 'No'], validators=[InputRequired()])
    coffee_price = StringField(label='Coffee Price', validators=[InputRequired()])
    submit = SubmitField(label='Submit')


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Returns the table as a dictionary
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# creating the table
with app.app_context():
    db.create_all()


@app.route('/')
def home():  # put application's code here
    all_cafes = list(db.session.execute(db.select(Cafe)).scalars())
    return render_template('index.html', cafes=all_cafes)


@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    pass


@app.context_processor
def inject_templates():
    year_today = datetime.now().year
    return dict(year=year_today)


if __name__ == '__main__':
    app.run()
