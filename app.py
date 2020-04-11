from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_pymongo import PyMongo
from random import seed, randint
import uuid

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'sanctWorld'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/sanctEventdb'

mongo = PyMongo(app)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route('/setcookie', methods = ['POST', 'GET'])
def setcookie():
    if (request.cookies.get('c_id')) is None:
        cookie = str(uuid.uuid1())
        resp = redirect(url_for('main'))
        resp.set_cookie('c_id', cookie)
        return resp
    else:
        return redirect(url_for('main'))

@app.route("/main")
def main():
    cookie = request.cookies.get('c_id')
    return render_template('main.html', cookie=cookie)

@app.route("/support")
def support():
    return render_template('support.html')

@app.route("/read", methods=['GET'])
def read():
    
    list_events = mongo.db.sanctDb
    output = []
    other_feeling = []
    for s in list_events.find():
        output.append({'event_id' : s['event_id'], 'event_data' : s['event_data'], 'c_id' : s['c_id']})
    for e in output:
        if e['c_id'] != request.cookies.get('c_id'):
            other_feeling.append(e)
    if (len(other_feeling)) == 0:
        messages = ""
        event_id = ""
    else:
        random_int = randint(0, (len(other_feeling)-1))
        messages = other_feeling[random_int]['event_data']
        event_id=other_feeling[random_int]['event_id']
    return render_template("read.html", messages=messages, event_id=event_id)

@app.route("/write", methods=['GET'])
def write():
    list_events = mongo.db.sanctDb
    output = []
    my_feeling = []
    for s in list_events.find():
        output.append({'event_id': s['event_id'], 'event_data': s['event_data'], 'c_id': s['c_id'], 'postcard_love' : s['postcard_love'], 'postcard_support' : s['postcard_support'], 'postcard_comfort': s['postcard_comfort'], 'postcard_reply' : s['postcard_reply']})
    other_response = output
    for e in output:
        if e['c_id'] == request.cookies.get('c_id'):
            my_feeling.append(e)
    other_response = my_feeling
    return render_template("write.html", other_response=other_response)

@app.route("/submit")
def submit():
    return render_template("submit.html")


# Database Interaction Methods

@app.route('/events', methods=['GET'])
def get_all_events():
    list_events = mongo.db.sanctDb
    output = []
    for s in list_events.find():
        output.append({'c_id' : s['c_id'],'event_id' : s['event_id'], 'event_data_type' : s['event_data_type'], 'event_data' : s['event_data']})
    return jsonify({'result' : output})

@app.route('/events/<event_id>', methods=['GET'])
def get_one_event(event_id):
    #print (event_id)
    a_event = mongo.db.sanctDb
    ev = a_event.find_one({'event_id' : str(event_id)})
    print(ev)
    if ev:
        output = {'event_id' : ev['event_id'], 'event_data' : ev['event_data']}
    else:
        output = "No such event_id"
    return jsonify({'result' : output})

@app.route('/postcard', methods=['POST'])
def add_postcard_event():
    eventDb = mongo.db.sanctDb
    event_id = str(uuid.uuid1()) # generate uuid on server side for event // request.json['name'] 
    c_id = request.cookies.get('c_id')
    event_data = request.form['feeling']

    postcard_love = 0
    postcard_support = 0
    postcard_comfort = 0

    postcard_reply = ""
    
    event_id = str(uuid.uuid1()) # generate uuid on server side for event // request.json['name'] 

    event_data = request.form['feeling']

    ev_ins_id = eventDb.insert({'event_id': event_id, 'event_data': event_data, 'c_id': c_id, 'postcard_love' : postcard_love, 'postcard_support' : postcard_support, 'postcard_comfort': postcard_comfort, 'postcard_reply' : postcard_reply})
    new_ev = eventDb.find_one({'_id': ev_ins_id })
    output = {'event_id' : new_ev['event_id'],'event_data' : new_ev['event_data']}
    print(jsonify({'result' : output}))

    return redirect(url_for("submit"))


@app.route('/postcard_text', methods=['POST'])
def add_postcard_text():
    eventDb = mongo.db.sanctDb
    
    event_id = str(uuid.uuid1()) # generate uuid on server side for event // request.json['name'] 
    c_id = request.cookies.get('c_id')
    event_data = request.form['feeling']
    ev_ins_id = eventDb.insert({'event_id': event_id, 'event_data': event_data, 'c_id': c_id})
    new_ev = eventDb.find_one({'_id': ev_ins_id })
    output = {'event_id' : new_ev['event_id'], 'event_data' : new_ev['event_data']}
    print(jsonify({'result' : output}))

    return redirect(url_for("submit"))

@app.route('/postcard/reply/<event_id>', methods=['POST'])
def postcard_reply(event_id):
    #print (event_id)
    a_event = mongo.db.sanctDb
    ev = a_event.find_one({'event_id' : str(event_id)})
    print(ev)

    postcard_reply = request.form['postcard_reply']

    if ev:
        # add postcard love if exists in post
        if  request.form.get('postcard_love'):
            postcard_love = int(ev['postcard_love'])
            postcard_love = postcard_love + 1
        else:
            postcard_love = int(ev['postcard_love'])

        # add postcard support if exists in post
        if  request.form.get('postcard_support'):
            postcard_support = int(ev['postcard_support'])
            postcard_support = postcard_support + 1
        else:
                postcard_support = int(ev['postcard_support'])

        # add postcard if comfort exists in post
        if  request.form.get('postcard_comfort'):
            postcard_comfort = int(ev['postcard_comfort'])
            postcard_comfort = postcard_comfort + 1
        else:
            postcard_comfort = int(ev['postcard_comfort'])

        if postcard_reply:
            # future code for maintaining message threads and conversations

            # add in future ai call out and interventions from medical professionals

            postcard_reply = str(postcard_reply)
        else:
            #maintain previous message if no new message has been included
            postcard_reply = ev['postcard_reply']

    # update the postcard

        result = a_event.update_one(
            {"event_id" : event_id},
            {"$set": {"postcard_reply" : postcard_reply, "postcard_comfort" : postcard_comfort, "postcard_support": postcard_support, "postcard_love": postcard_love}},
            upsert=False
        )

        if result:
            output = "Successfully updated"
        else:
            output = "Failed to update"

    else:
        output = "No such event_id"
        print (jsonify({'result' : output}))
    return redirect(url_for("submit"))

if __name__ == '__main__':
    app.run(debug=True)

