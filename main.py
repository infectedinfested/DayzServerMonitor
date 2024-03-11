from flask import Flask, request, jsonify, Response
from threading import Thread
from flask_httpauth import HTTPBasicAuth
from flask_httpauth import HTTPTokenAuth


import secrets
import time
import json
import csv
import sys
import uuid
import asyncio
import hashlib


import scheduledJob
from classes import BannedPerson
from common import strtobool, create_ban_file, p, post_alert

# some_file.py
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, 'flows')
import ban_flow


# log location
logsLocation = p("logging.file_path") 

app = Flask(__name__)

#################################
# authentication                #
#################################

auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth(scheme='Bearer')


tokens = {}

# Salted passwords stored in a file
PASSWORD_FILE = "passwords.txt"


# Load passwords from file
def load_passwords():
    passwords = {}
    with open(PASSWORD_FILE, "r") as file:
        for line in file:
            username, salt, password_hash = line.strip().split(":")
            passwords[username] = (salt, password_hash)
    return passwords

# Verify a password against a hash
@auth.verify_password
def verify_password(username, password):
    passwords = load_passwords()

    if username in passwords:
        salt, password_hash = passwords[username]
        return password_hash == hashlib.sha256((password + salt).encode()).hexdigest()
    return False

# Issue a token after successful basic authentication
@app.route('/api/authenticate', methods=['POST'])
@auth.login_required
def authenticate():
    username = request.authorization.username
    token = secrets.token_hex(16)
    tokens[token] = ({
            "user":username,
            "created": time.time()
        })
    return jsonify({'token': token}), 200



# Protect other APIs with token authentication
@app.route('/api/protected', methods=['GET'])
@token_auth.login_required
def protected():
    if is_token_expired(request.headers.get('Authorization').split()[1]):
        return jsonify({'message': 'Token expired'}), 401
    return jsonify({'message': 'Access granted'}), 200

@token_auth.verify_token
def verify_token(token):
    if token in tokens:
        return tokens[token]

# Check if a token has expired
def is_token_expired(token):
    print("checking if token is expired")
    if time.time() - tokens[token]['created'] > 30 * 60:
        return True
    else:
        tokens[token]['created'] = time.time()
        return False

################################



# ban endpoints
@app.route('/api/unban', methods=['GET'])
@token_auth.login_required
async def unban_list():
    if is_token_expired(request.headers.get('Authorization').split()[1]):
        return jsonify({'message': 'Token expired'}), 401
    await post_alert("bot_log","moderator: Scruffy is rerunning the unban script")
    if request.headers.get('X-Correlation-ID'):
        return Response(json.dumps(ban_flow.unban(request.headers.get('X-Correlation-ID'))), mimetype='application/json')
    else:
        return Response(json.dumps(ban_flow.unban(uuid.uuid4())), mimetype='application/json')

@app.route('/api/unban/<id>', methods=['GET'])
@token_auth.login_required
async def get_unbannedPersonById(id):
    if is_token_expired(request.headers.get('Authorization').split()[1]):
        return jsonify({'message': 'Token expired'}), 401

    if request.headers.get('X-Correlation-ID'):
        return Response(json.dumps(ban_flow.unban(request.headers.get('X-Correlation-ID'),id)), mimetype='application/json')
    else:
        return Response(json.dumps(ban_flow.unban(uuid.uuid4(),id)), mimetype='application/json')
    

@app.route('/api/ban', methods=['GET'])
@token_auth.login_required
async def get_ban_list():
    if is_token_expired(request.headers.get('Authorization').split()[1]):
        return jsonify({'message': 'Token expired'}), 401

    await post_alert("bot_log","moderator: Scruffy is retrieving the ban list")
    filtered = request.args.get('showAll')
    if request.headers.get('X-Correlation-ID'):
        return Response(json.dumps([person.__dict__ for person in ban_flow.getBanList(request.headers.get('X-Correlation-ID'),filtered).itervalues()]), mimetype='application/json')
    else:
        return Response(json.dumps([person.__dict__ for person in ban_flow.getBanList(uuid.uuid4(),filtered)]), mimetype='application/json')

@app.route('/api/ban/transform', methods=['GET'])
def create_transformed_ban_list():
    if request.headers.get('X-Correlation-ID'):
        return Response(json.dumps(ban_flow.transform(request.headers.get('X-Correlation-ID'))), mimetype='application/json')
    else:
        return Response(json.dumps(ban_flow.transform(uuid.uuid4())), mimetype='application/json')

@app.route('/api/ban', methods=['POST'])
def post_ban_list():
    data = request.get_json()

    return Response(json.dumps( {"message" :'banned person inserted with id:' + str((ban_flow.ban(uuid.uuid4(),data)).uniqueid)}), mimetype='application/json')


@app.route('/api/ban/<id>', methods=['GET'])
def get_bannedperson_by_id(id):
    with open('DayZServerBackup20220728/ban.csv', 'r') as file:
        reader = csv.DictReader(file)
        bannedPeople= []
        for row in reader:
            bannedPerson = BannedPerson(row['steamid'], row['reason'], row['time'], row['startDate'], row['comment'], row['uniqueid'], strtobool(row['active']))
            bannedPeople.append(bannedPerson)

        for bannedPerson in bannedPeople:
            if bannedPerson.uniqueid == id:
                json_data = json.dumps(bannedPerson.__dict__)
    return json_data


@app.route('/api/ban/<id>', methods=['PATCH'])
def patch_bannedperson_by_id(id):
    data = request.get_json()
    rows = []
    bannedPersons = []
    with open('DayZServerBackup20220728/ban.csv', 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            rows.append(row)

    # Find the row with the desired ID and edit it
    for row in rows:
        if row['uniqueid'] == id:  # Assuming 'ID' is the name of the unique identifier column
            data['uniqueid'] = id
            row.update(data)  # Update the row with new data
  
    # Write the updated data back to the CSV file
    fieldnames = rows[0].keys() if rows else []
    with open('DayZServerBackup20220728/ban.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in list(row)[:7]})
    
    for row in rows:
        bannedPersons.append(BannedPerson(row['steamid'], row['reason'], row['time'], row['startDate'], row['comment'], row['uniqueid'], strtobool(row['active'])))
    create_ban_file(bannedPersons, "w")
    return "update successful"



def _sendAlert(channel, message) -> None:
    data = request.get_json()
    asyncio.run(post_alert(data.get('channel', ''), data.get('message', '')))



# Server status endpoints
server_status = {
    'status': 'stopped'
}

@app.route('/api/server/status', methods=['GET'])
def get_status():
    return jsonify(server_status)

@app.route('/api/server/start', methods=['POST'])
def start_server():
    # Code to start the DayZ server
    server_status['status'] = 'running'
    return jsonify({'message': 'Server started successfully'})

@app.route('/api/server/stop', methods=['POST'])
def stop_server():
    # Code to stop the DayZ server
    server_status['status'] = 'stopped'
    return jsonify({'message': 'Server stopped successfully'})

@app.route('/api/server/restart', methods=['POST'])
def restart_server():
    # Code to stop the DayZ server
    server_status['status'] = 'restarting'
    return jsonify({'message': 'Server restarting successfully'})

@app.route('/api/server/update', methods=['POST'])
def update_server():
    # Code to update the DayZ server
    return jsonify({'message': 'Server updated successfully'})


# server settings endpoints

'''
@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(server_status)

@app.route('/start', methods=['POST'])
def start_server():
    # Code to start the DayZ server
    server_status['status'] = 'running'
    return jsonify({'message': 'Server started successfully'})

@app.route('/stop', methods=['POST'])
def stop_server():
    # Code to stop the DayZ server
    server_status['status'] = 'stopped'
    return jsonify({'message': 'Server stopped successfully'})

@app.route('/update', methods=['POST'])
def update_server():
    # Code to update the DayZ server
    return jsonify({'message': 'Server updated successfully'})
'''




# Start the scheduler in a separate thread
scheduler_thread = Thread(target=scheduledJob.run_scheduler)
scheduler_thread.start()

if __name__ == '__main__':
    app.run(debug=True)

