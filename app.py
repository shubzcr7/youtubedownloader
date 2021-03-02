from flask import Flask, render_template, request, flash, redirect, send_from_directory, abort, url_for
from pytube import YouTube
import pytube
import os
import os.path
import time
from flask_sqlalchemy import SQLAlchemy
import requests
from flask_heroku import Heroku


app = Flask(__name__)

heroku = Heroku(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    Subject = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(600), nullable=False)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.message}')"


class Sub(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}'"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/download", methods=['GET', 'POST'])
def download():
    if request.method == "POST":
        url = request.form.get("ur")
        quality = request.form.get("quality")
        try:
            yt = YouTube(url)
            print(yt.title)
            if "audio" in quality:
                a, b = quality.split("/")
                c = a.strip()
                d = b.strip()
                q = d.strip()
            else:
                a, b = quality.split(",")
                c = a.strip()
                d = b.strip()
                e = c.split("/")
                q = e[1]
            x = yt.streams
            z = ""
            t = time.strftime('%d-%m-%Y_%H_%M_%S_%Z')
            a = t[:19]
            t = a.replace(" ", "_")
            for i in x:
                if c in str(i) and d in str(i) and "vcodec" in str(i) and "acodec" in str(i):
                    i.download(filename=t)
                    break
                elif c in str(i) and "acodec" in str(i):
                    i.download(filename=t)
                    break
            else:
                flash("The vedio is not available in this format", "danger")
                return redirect(url_for("index"))
            fname = os.path.basename(t)
            mod = fname+"."+q
            address = "http://youtmate.herokuapp.com/download-file/" + mod
            return redirect(address, code=302)
        except pytube.exceptions.RegexMatchError:
            flash("Not valid URL", "danger")
            return redirect(url_for("index"))


app.config["CLIENT_TEXTFILES"] = os.getcwd()


@app.route("/download-file/<fname>")
def download_zapfile(fname):
    w = fname
    try:
        return send_from_directory(app.config["CLIENT_TEXTFILES"], filename=w, as_attachment=True)
    except FileNotFoundError:
        abort(404)


@app.route("/feed", methods=['GET', 'POST'])
def feed():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")
        con = Contact(name=name, email=email, Subject=subject, message=message)
        db.session.add(con)
        db.session.commit()
        flash("Your message has been sent successfully", "success")
    return redirect(url_for("index"))


@app.route("/subscribe", methods=['GET', 'POST'])
def subscribe():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        user = Sub.query.filter_by(email=email).first()
        if user == None:
            con = Sub(name=name, email=email)
            db.session.add(con)
            db.session.commit()
            flash("You are subscribed to the Youtmate", "success")
        else:
            flash("Already a member", 'danger')
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
