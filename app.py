from flask import Flask, render_template
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:2701/covid"
mongo = PyMongo(app)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/main")
def main():
    return render_template('main.html')

@app.route("/read")
def read():
    messages = "Hello Test"
    return render_template("read.html", messages=messages)

@app.route("/write")
def write():
    return render_template("write.html")

if __name__ == '__main__':
    app.run(debug=True)