from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import validators
import string
import random

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "data.sqlite")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your-secret-key"

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Url(db.Model):
    __tablename__ = "url_table"
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(10), unique=True, nullable=False)

    def __init__(self, original_url, short_url):
        self.original_url = original_url
        self.short_url = short_url

    def __repr__(self):
        return f"<Url {self.original_url}>"


def generate_short_url():
    characters = string.ascii_letters + string.digits
    while True:
        short_url = "".join(random.choice(characters) for i in range(3))
        if not Url.query.filter_by(short_url=short_url).first():
            return short_url


@app.route("/")
def home_page():
    return render_template("Home.html")


@app.route("/", methods=["POST"])
def shorten_url():
    original_url = request.form.get("user_url")
    if not validators.url(original_url):
        return render_template("Home.html", error="Invalid URL")
    url = Url.query.filter_by(original_url=original_url).first()
    if not url:
        short_url = generate_short_url()
        url = Url(original_url=original_url, short_url=short_url)
        db.session.add(url)
        db.session.commit()
    return render_template("Home.html", short_url=url.short_url)


@app.route('/<short_url>')
def redirect_to_original_url(short_url):
    url = Url.query.filter_by(short_url=short_url).first()

    if url:
        return redirect(url.original_url)
    
    return os.abort(404)


@app.route("/history")
def history_page():
    urls = Url.query.all()
    return render_template("History.html", urls=urls)


if __name__ == "__main__":
    app.run(debug=True)
