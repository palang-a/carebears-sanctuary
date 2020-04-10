from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/main")
def main():
    return render_template('main.html')

@app.route("/read")
def read():
    return render_template("read.html", messages="WIP TEXT")

@app.route("/write")
def write():
    return render_template("write.html")

if __name__ == '__main__':
    app.run(debug=True)