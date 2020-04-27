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
        resp = redirect(url_for('generate_challenge_codes', uuid=cookie))
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

@app.route("/merge_account")
def merge_account():
    cookies = request.cookies.get('c_id')
    a_event = mongo.db.challengeDb
    a_code = a_event.find_one({'id_client' : cookies})
    return render_template('merge_account.html', cookies=cookies, code=a_code)

@app.route("/pair_account")
def pair_account():
    cookies = request.cookies.get('c_id')
    a_event = mongo.db.challengeDb
    a_code = a_event.find_one({'id_client' : cookies})
    return render_template('pair_account.html', cookies=cookies, code=a_code)

@app.route("/merge_response")
def merge_response():
    merge_message = request.args['merge_message']
    return render_template('merge_account.html', merge_message=merge_message)

@app.route("/pair_response")
def pair_response():
    cookies = request.cookies.get('c_id')
    pair_message = request.args['pair_message']
    return render_template('pair_response.html', cookies=cookies, pair_message=pair_message)

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
    a_event = mongo.db.challengeDb

    # if a set of challenge codes of this uuid exists, then skip this.
    a_code = a_event.find_one({'id_client' : str(uuid)})

    if a_code: # challenge code exists already, skip generating a new one and return the existing one in DB
        output = {'id_client' : uuid, 'challenge_id' : a_code['challenge_id'],'challenge_word' : a_code['challenge_word']}

    else:
        #Use random words library to generate 3x random words, at max 5 characters in length each for challenge code
        # plus one challenge word with a random integer as the clientKey (a more user friendly form of the uuid)
        r = RandomWords()
        try:
            clientKey = (r.get_random_word(maxLength=6)).lower() + str(randint(0,2000))
        except: #try once more due to bug with library
            try:
                clientKey = (r.get_random_word(maxLength=6)).lower() + str(randint(0,2000))

            except:
                clientKey = None #set to None to allow error to be returned

        try:
            list_random_words = r.get_random_words(maxLength=5, limit=3)
            list_random_words[:] = [word.lower() for word in list_random_words]
        
        except: #try a second time to generate words - bug with library
            try:
                list_random_words =  r.get_random_words(maxLength=5, limit=3)
                list_random_words[:] = [word.lower() for word in list_random_words]
            except:
                list_random_words = None #set to None to allow error to be returned

        if list_random_words and clientKey:
            output = {'id_client' : uuid, 'challenge_id' : clientKey,'challenge_word' : list_random_words}
            a_event.insert_one({'id_client' : uuid, 'challenge_id' : clientKey,'challenge_word' : list_random_words, 'prev_verifications' : None, 'merged_account_id' : None})
        else:
            output = "Failed to generate codes. Please report the error."
    print(jsonify({'result' : output}))
    return redirect(url_for('main'))

# merge two accounts together, if the client submits correct responses to the challenge codes for the 
# accounts they are trying to link

@app.route('/challenge/response/<uuid>', methods=['POST'])
def response_challenge_codes(uuid):

    # Extract challenge codes responses
    aClientId = str(request.form.get('clientKey')).lower() # challengeid for a client that the responses relate to
    challengeResponses = [] #create a list to store challenge responses

    challengeResponses.append(str(request.form.get('challenge_word_1')).lower())
    challengeResponses.append(str(request.form.get('challenge_word_2')).lower())
    challengeResponses.append(str(request.form.get('challenge_word_3')).lower())

    #print ("aClientId is: " + aClientId)
    #print(challengeResponses, sep='\n')

    #look in db for previously generated challenge codes, if it exists, then proceed with verification
    challenge_codesDB = mongo.db.challengeDb
    previous_codes = challenge_codesDB.find_one({'challenge_id' : aClientId})

    #print(previous_codes, sep='\n')


    if previous_codes:
        if (previous_codes['id_client'] == uuid): #if this code is this client's, then skip merging
            output = "Please attempt to merge with another client"
            return jsonify({'result' : output})

        # add one to the number of challenge verifications
        if (previous_codes['prev_verifications']):
            numOf_Verifications = int(previous_codes['prev_verifications'])
            numOf_Verifications = numOf_Verifications + 1
        else:
            numOf_Verifications = 1 #first verification - set to 1 to initialise

        result = challenge_codesDB.update_one(
            {"challenge_id" : aClientId},
            {"$set": {"prev_verifications" : numOf_Verifications}},
            upsert=False
        )

        # to fix - exit early from function if update prevverifications doesn't work
        if (result):
            output = "Successfully updated"
        else:
            output = "Failed to update"
            return jsonify({'result' : output})

        if (verify_challenge_codes(previous_codes['challenge_word'],challengeResponses)):
            #same codes so proceed to next stage for syncing for the two accounts
            #store sucessful challenge response events in a seperate collection
            a_response_event = mongo.db.challengeResponses
            a_response_event.insert_one({'id_client' : uuid, 'challenge_id' : aClientId})

            #verify if two clients have submitted the right responses
            if (setReadyForMerge(uuid, aClientId)):
                output = "Both clients have verified. Please send a merge account request."
            else:
                output = "Successful response recieved. Please verify on the other client."
        else:
            #not the same codes, failed challenge
            output = "Failed challenge - please retry"

    # otherwise, respond with a message that the challenge code need to be generated first
    else:
        output = "Generate a challenge code first."

    print (jsonify({'result' : output}))
    return redirect(url_for("pair_response", pair_message=output))

@app.route('/account/merge/<uuid>', methods=['POST'])
def merge_accounts(uuid):

    aClientId = str(request.form.get('clientKey')).lower()
    #look in db for previously generated challenge codes, to get the other uuid based on clientKey
    challenge_codesDB = mongo.db.challengeDb
    other_uuid = challenge_codesDB.find_one({'challenge_id' : aClientId})['id_client']

    merge_id_this = challenge_codesDB.find_one({'id_client' : uuid})['merged_account_id']
    other_client_merge_id = challenge_codesDB.find_one({'id_client' : other_uuid})['merged_account_id']



    # merge already happened, return success
    if (merge_id_this and other_client_merge_id):
        output = {'id_client' : merge_id_this} #return the new consolidated merged id
    else: #merge needs to happen
        
        target_merge_uuid = sorted([uuid, other_uuid])[0] #ensure always mergeid is the same 
        #check if there was an old uuid, if so set it, so that it can also be updated
        old_merged_uuid = None
        if (merge_id_this):
            old_merged_uuid = merge_id_this

        if (other_client_merge_id):
            old_merged_uuid = other_client_merge_id

       # if ((merge_id_this == None) or (other_client_merge_id == None)): #
        if (do_merge (uuid,other_uuid,target_merge_uuid)):
        
            # update record of merged account
            result = challenge_codesDB.update_one(
                {"id_client" : uuid},
                {"$set": {"merged_account_id" : target_merge_uuid}},
                upsert=False
            )

            if (result):
                result = challenge_codesDB.update_one(
                    {"id_client" : other_uuid},
                    {"$set": {"merged_account_id" : target_merge_uuid}},
                    upsert=False
                )

                if (result == None):
                    output = "Failed to update merge accounts for id: " + other_uuid + " with id: "+ target_merge_uuid
                else: #both challenge code records have been updated                       
                    #clean up any remaining old uuids that refer to an old id
                    if (old_merged_uuid):
                        result = challenge_codesDB.update_many(
                            {"merged_account_id" : old_merged_uuid},
                            {"$set": {"merged_account_id" : target_merge_uuid}},
                            upsert=False
                        )
                    output = "Merge completed"
            else:
                output = "Failed to update merge accounts for id: " + uuid + " with id: "+ target_merge_uuid
        else:
            output = "Failed to update postcards to merge accounts for ids: " + uuid + " and other client id: "+ other_uuid

    print (jsonify({'result' : output}))
    return redirect(url_for("merge_response", merge_message=output))


def do_merge (uuid_this_client, uuid_other_client, uuid_target):

    #access the records for updating
    a_event = mongo.db.sanctDb

    resultThis = a_event.update_many(
        {"c_id" : uuid_this_client},
        {"$set": {"c_id" : uuid_target}},
        upsert=False
    )

    resultOther = a_event.update_many(
        {"c_id" : uuid_other_client},
        {"$set": {"c_id" : uuid_target}},
        upsert=False
    )

    if (resultThis and resultOther): # both updates were successful, otherwise return false as something failed
        return True
    else:
        return False
        
    return False


# verify if both challenge codes have been entered- and if so mark the challenge response and ready for merge
def setReadyForMerge (uuid_this_client,aClientId_other_client):
    
    challenge_events = mongo.db.challengeDb

    this_client_rec = challenge_events.find_one({'id_client' : uuid_this_client})
    other_client_rec = challenge_events.find_one({'challenge_id' : aClientId_other_client})

    if (this_client_rec and other_client_rec):

        thisClient = []
        otherClient = []

        thisClient.append(this_client_rec['id_client']) 
        thisClient.append(this_client_rec['challenge_id']) 

        otherClient.append(other_client_rec['id_client'])
        otherClient.append(other_client_rec['challenge_id'])

        #print(thisClient, sep='\n')

        #print(otherClient, sep='\n')

        a_response_event = mongo.db.challengeResponses

        # check if other client has submited a response yet - if not, return false.
        otherClientComplete = a_response_event.find_one({'id_client' : otherClient[0]})
        #thisClientComplete = a_response_event.find_one({'challenge_id' : thisClient[1]})
        #print("other client is: " + otherClientComplete)

        #print("this client is: " + thisClientComplete)
        if (otherClientComplete == None):
            #print ("Other client is not done verifying")
            return False #other client still need to verify

        # compared uuids. 
        
        thisClientComplete = (a_response_event.find_one({'challenge_id' : thisClient[1]})['id_client'] == otherClient[0])
        otherClientComplete = (a_response_event.find_one({'challenge_id' : otherClient[1]})['id_client'] == thisClient[0])
        
        #print("this client: " + a_response_event.find_one({'challenge_id' : thisClient[1]})['id_client'])
        #print("other client: " + otherClient[0])


        #print("other client: " + a_response_event.find_one({'challenge_id' : otherClient[1]})['id_client'])
        #print("this client: " + thisClient[0])

        if (thisClientComplete and otherClientComplete): # both clients have verified
            #print ("verified both")
            a_response_event.update_one(
                {"challenge_id" : otherClient[1]},
                {"$set": {"merge_ready" : True}},
                upsert=False
            )

            a_response_event.update_one(
                {"challenge_id" : thisClient[1]},
                {"$set": {"merge_ready" : True}},
                upsert=False
            )

            return True
        else:
            return False
    else: #don't flag that accounts are ready to merge yet as other client needs verification
        return False
    
    return True


# check if the challenge codes provides are the same as existing challenge codes in DB
def verify_challenge_codes(existingCodes, newCodes):
    if (len(existingCodes) == len(newCodes)):
        # verify if each item in existingCode exists in NewCodes
        return set(existingCodes) == set(newCodes)
    else:
        return False

    return False


if __name__ == '__main__':
    #app.run(debug=True)
    app.run(debug=True, host='0.0.0.0', port='5000')
