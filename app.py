import json
import pickle
import os

# ---- Load Environment Variables ----
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, url_for, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import pandas as pd

app = Flask(__name__)

# ---- Core config ----
# IMPORTANT: set these as real environment variables in production.
# Never commit real secrets/passwords into source control.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "dev-only-change-this-before-deploying")

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,   # test the connection before using it; reconnect if it's dead
    'pool_recycle': 280,    # recycle connections every ~4.5 minutes, before the pooler drops them
}

db = SQLAlchemy(app)

# ---- Flask-Login setup ----
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'          # redirects here if @login_required fails
login_manager.login_message = "Please log in to continue."


# ---------------- Database Models ----------------

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class PredictionHistory(db.Model):
    __tablename__ = 'prediction_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # nullable=True keeps old rows valid

    crim = db.Column(db.Float)
    zn = db.Column(db.Float)
    indus = db.Column(db.Float)
    chas = db.Column(db.Float)
    nox = db.Column(db.Float)
    rm = db.Column(db.Float)
    age = db.Column(db.Float)
    dis = db.Column(db.Float)
    rad = db.Column(db.Float)
    tax = db.Column(db.Float)
    ptratio = db.Column(db.Float)
    b = db.Column(db.Float)
    lstat = db.Column(db.Float)
    predicted_price = db.Column(db.Float)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------- Load the trained model ----------------
regmodel = pickle.load(open('regmodel.pkl', 'rb'))
scaler = pickle.load(open('scaling.pkl', 'rb'))


# ---------------- Auth routes ----------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not password:
            return render_template('register.html', error="Username and password are required.")
        if password != confirm_password:
            return render_template('register.html', error="Passwords do not match.")
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="That username is already taken.")

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('home'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))

        return render_template('login.html', error="Invalid username or password.")

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ---------------- App routes ----------------

@app.route('/')
@login_required
def home():
    return render_template('home.html')


@app.route('/predict_api', methods=['POST'])
@login_required
def predict_api():
    data = request.json['data']
    new_data = scaler.transform(np.array(list(data.values())).reshape(1, -1))
    output = regmodel.predict(new_data)
    return jsonify(output[0])


@app.route('/predict', methods=['POST'])
@login_required
def predict():
    data = [float(x) for x in request.form.values()]
    final_input = scaler.transform(np.array(data).reshape(1, -1))
    output = regmodel.predict(final_input)[0]

    new_record = PredictionHistory(
        user_id=current_user.id,
        crim=data[0], zn=data[1], indus=data[2], chas=data[3],
        nox=data[4], rm=data[5], age=data[6], dis=data[7],
        rad=data[8], tax=data[9], ptratio=data[10], b=data[11],
        lstat=data[12], predicted_price=float(output)
    )
    db.session.add(new_record)
    db.session.commit()

    # Boston Housing MEDV is in $1000s -> multiply for a real dollar figure
    formatted_price = "${:,.0f}".format(float(output) * 1000)
    return render_template(
        "home.html",
        prediction_text="Estimated Home Value: {}".format(formatted_price)
    )


@app.route('/history')
@login_required
def history():
    records = (
        PredictionHistory.query
        .filter_by(user_id=current_user.id)
        .order_by(PredictionHistory.id.desc())
        .limit(15)
        .all()
    )
    return render_template('history.html', records=records)


if __name__ == "__main__":
    app.run(debug=True)