from flask import Flask
app = Flask(__name__)

@app.route("/")
@app.route("/home")
def hello():
    return "Hello World"

@app.route("/read")
    return "Read"

@app.route("/write")
def write():
    return "Write"

if __name__ == '__main__':
    app.run(debug=True)