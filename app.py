from flask import Flask, render_template, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField, BooleanField
from wtforms.validators import URL, InputRequired
from datetime import datetime
import psycopg2
import os

# Environment Variables
DATABASE_URI = os.environ['DATABASE_URI']
SECRET_KEY = os.environ['SECRET_KEY']
PASSKEYS = [generate_password_hash(passkey.strip()) for passkey in os.environ['PASSKEYS'].split(',')]
# Initialize Flask App
app = Flask(__name__)
app.secret_key = SECRET_KEY

# Initialize Database
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
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
    seats = StringField(label='Seats', validators=[InputRequired()])
    has_toilet = BooleanField(label='Has Toilet')
    has_sockets = BooleanField(label='Has Sockets')
    has_wifi = BooleanField(label='Has WiFi')
    can_take_calls = BooleanField(label='Can Take Calls')
    coffee_price = StringField(label='Coffee Price', validators=[InputRequired()])
    submit = SubmitField(label='Submit')


# Confirm Delete Form
class ConfirmDeleteForm(FlaskForm):
    passkey = StringField(label='Passkey')
    submit = SubmitField(label='Confirm Deletion')
    close = SubmitField(label='Close')


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
    form = CafeAddForm()
    all_cafes = list(db.session.execute(db.select(Cafe)).scalars())
    return render_template('index.html', cafes=all_cafes, form=form)


@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    form = CafeAddForm()
    if form.validate_on_submit():
        cafe = {key: value for key, value in form.data.items() if key != 'csrf_token' and key != 'submit'}
        new_cafe = Cafe(**cafe)
        db.session.add(new_cafe)
        db.session.commit()
        flash(f'New Cafe {new_cafe.name} added successfully!', category='success')
        return redirect(url_for('home'))


@app.route('/delete/<int:cafe_id>', methods=['GET', 'POST'])
def delete_cafe(cafe_id: int):
    form = ConfirmDeleteForm()
    cafe_to_delete = db.get_or_404(Cafe, cafe_id)
    if form.validate_on_submit():
        print("validated")
        passkey_match = [check_password_hash(passkey_hash, form.passkey.data) for passkey_hash in PASSKEYS]
        print(passkey_match)
        if cafe_id > 21 or any(passkey_match):
            db.session.delete(cafe_to_delete)
            db.session.commit()
            flash(f'Cafe {cafe_to_delete.name} deleted successfully!', category='success')
            return redirect(url_for('home'))
        else:
            flash('Incorrect Passkey!', category='danger')
            return redirect(url_for('home'))

    return render_template('confirm-del.html', form=form, cafe=cafe_to_delete)

@app.context_processor
def inject_templates():
    year_today = datetime.now().year
    return dict(year=year_today)


if __name__ == '__main__':
    app.run()
