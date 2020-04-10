from flask import Flask, render_template
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'sanctWorld'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/sanctEventdb'

mongo = PyMongo(app)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/main")
def main():
    return render_template('main.html')

@app.route("/support")
def support():
    return render_template('support.html')

@app.route("/read")
def read():
    messages = "Hello Test"
    return render_template("read.html", messages=messages)

@app.route("/write")
def write():
    return render_template("write.html")

if __name__ == '__main__':
    app.run(debug=True)