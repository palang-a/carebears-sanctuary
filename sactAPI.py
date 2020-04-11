from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
import uuid

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'sanctWorld'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/sanctEventdb'

mongo = PyMongo(app)

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
  #print(ev)
  if ev:
    output = {'event_id' : ev['event_id'], 'event_data' : ev['event_data']}
  else:
    output = "No such event_id"
  return jsonify({'result' : output})


@app.route('/postcard/reply/<event_id>', methods=['POST'])
def postcard_reply(event_id):
  #print (event_id)
  a_event = mongo.db.sanctDb
  ev = a_event.find_one({'event_id' : str(event_id)})
  print(ev)

  postcard_love = request.json['postcard_love']
  postcard_support = request.json['postcard_support']
  postcard_comfort = request.json['postcard_comfort']

  postcard_reply = request.json['postcard_reply']

  if ev:
    # add postcard love if exists in post
    if postcard_love:
        postcard_love = int(ev['postcard_love'])
        postcard_love = postcard_love + 1
    else:
        postcard_love = int(ev['postcard_love'])
    
    # add postcard support if exists in post
    if postcard_support:
        postcard_support = int(ev['postcard_support'])
        postcard_support = postcard_support + 1
    else:
         postcard_support = int(ev['postcard_support'])

    # add postcard if comfort exists in post
    if postcard_comfort:
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

    #:{"city":"Visakhapatnam"}})
  else:
    output = "No such event_id"
  return jsonify({'result' : output})


@app.route('/postcard', methods=['POST'])
def add_postcard_event():
  eventDb = mongo.db.sanctDb
 
  event_id = str(uuid.uuid1()) # generate uuid on server side for event // request.json['name'] 

  event_data_type = request.json['event_data_type']
  event_data = request.json['event_data']

  int postcard_love = 0
  int postcard_support = 0
  int postcard_comfort = 0

  str postcard_reply = ""

  c_id = request.json['c_id']
  ev_ins_id = eventDb.insert({'event_id': event_id, 'event_data_type': event_data_type, 'event_data': event_data, 'c_id': c_id, 'postcard_love' : postcard_love, 'postcard_support' : postcard_support, 'postcard_comfort': postcard_comfort, 'postcard_reply' : postcard_reply})
  new_ev = eventDb.find_one({'_id': ev_ins_id })
  output = {'event_id' : new_ev['event_id'], 'event_data_type' : new_ev['event_data_type'],'event_data' : new_ev['event_data']}
  return jsonify({'result' : output})

if __name__ == '__main__':
    app.run(debug=True)
