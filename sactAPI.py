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
  print(ev)
  if ev:
    output = {'event_id' : ev['event_id'], 'event_data' : ev['event_data']}
  else:
    output = "No such event_id"
  return jsonify({'result' : output})


#@app.route('/postcards/<c_id>', methods=['GET'])
#def get_one_event(c_id):
  #print (event_id)
#  a_event = mongo.db.sanctDb

 # for postcard in all_postcards.find({"c_id": c_id}):
  #      jpprint.pprint(postcard)
  #ev = a_event.find_one({'event_id' : str(event_id)})
  #print(ev)
  #if ev:
  #  output = {'event_id' : ev['event_id'], 'event_data' : ev['event_data']}
  #else:
   # output = "No such event_id"
  #return jsonify({'result' : output})

@app.route('/postcard', methods=['POST'])
def add_postcard_event():
  eventDb = mongo.db.sanctDb
 
  event_id = str(uuid.uuid1()) # generate uuid on server side for event // request.json['name'] 

  event_data_type = request.json['event_data_type']
  event_data = request.json['event_data']
  c_id = request.json['c_id']
  ev_ins_id = eventDb.insert({'event_id': event_id, 'event_data_type': event_data_type, 'event_data': event_data, 'c_id': c_id})
  new_ev = eventDb.find_one({'_id': ev_ins_id })
  output = {'event_id' : new_ev['event_id'], 'event_data_type' : new_ev['event_data_type'],'event_data' : new_ev['event_data']}
  return jsonify({'result' : output})

if __name__ == '__main__':
    app.run(debug=True)
