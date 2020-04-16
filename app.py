from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_pymongo import PyMongo
from random import seed, randint
from random_word import RandomWords

import datetime
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
        expire_date = datetime.datetime.now()
        expire_date = expire_date + datetime.timedelta(days=90)
        resp = redirect(url_for('main'))
        resp.set_cookie('c_id', cookie, expires=expire_date)
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

    postcard_reply = []
    
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
    #print(ev)

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
            greet_title = ["A kindred spirit", "A kind passerby", "A polite person", "A secret admirer", "Your tribe", "Kindred soul", "Alter Ego", "A friend", "A digital companion", "A sanctum floater", "A bunny rabbit", "Yoda", "Mr. T", "Bond, James", "William Shakespeare", "A mate", "Clanmate", "A Spirit Animal", "Baby Yoda", "The piano-playing cat", "Spongebob squarepants", "Boss coach", "The person with an anonymous mask", "An ace charcuterie-board maker"]
            random_int = randint(0, (len(greet_title)-1))
            selected_title = greet_title[random_int]
            # add in future ai call out and interventions from medical professionals
            postcard_reply_list = ev['postcard_reply']
            postcard_reply_greet = [selected_title, str(postcard_reply)]

            postcard_reply_list.append(postcard_reply_greet)
        else:
            #maintain previous message if no new message has been included
            postcard_reply_list = ev['postcard_reply']

    # update the postcard

        result = a_event.update_one(
            {"event_id" : event_id},
            {"$set": {"postcard_reply" : postcard_reply_list, "postcard_comfort" : postcard_comfort, "postcard_support": postcard_support, "postcard_love": postcard_love}},
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

# generate a challenge code to link two clients together.
# each client for pairing must submit each other's client id + challenge codes.
# the server will then merge the uuids together
@app.route('/challenge/<uuid>', methods=['GET'])
def generate_challenge_codes(uuid):

    #store challenge events in a seperate collection
    a_event = mongo.db.challengeDB

    # if a set of challenge codes of this uuid exists, then skip this.
    a_code = a_event.find_one({'id_client' : str(uuid)})

    if a_code: # challenge code exists already, skip generating a new one and return the existing one in DB
        output = {'id_client' : uuid, 'challenge_id' : a_code['challenge_id'],'challenge_word' : a_code['challenge_word']}

    else:
        #Use random words library to generate 3x random words, at max 5 characters in length each for challenge code
        # plus one challenge word with a random integer as the clientKey (a more user friendly form of the uuid)
        r = RandomWords()
        try:
            clientKey = r.get_random_word(maxLength=6) + str(randint(0,2000))
        except: #try once more due to bug with library
            try:
                clientKey = r.get_random_word(maxLength=6) + str(randint(0,2000))
            except:
                clientKey = None #set to None to allow error to be returned

        try:
            list_random_words = r.get_random_words(maxLength=5, limit=3)
        
        except: #try a second time to generate words - bug with library
            try:
                list_random_words =  r.get_random_words(maxLength=5, limit=3)
            except:
                list_random_words = None #set to None to allow error to be returned

        if list_random_words and clientKey:
            output = {'id_client' : uuid, 'challenge_id' : clientKey,'challenge_word' : list_random_words}
            a_event.insert_one({'id_client' : uuid, 'challenge_id' : clientKey,'challenge_word' : list_random_words})
        else:
            output = "Failed to generate codes. Please report the error."
    return jsonify({'result' : output})

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(debug=True, host='0.0.0.0', port='5000')
