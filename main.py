from flask import Flask, request, jsonify, Response
from threading import Thread
from flask_httpauth import HTTPBasicAuth
from flask_httpauth import HTTPTokenAuth

from functools import wraps


import secrets
import string
import time
import json
import sys
import uuid
import asyncio
import hashlib
import multiprocessing


import scheduledJob
from classes import Error
from common import p

# some_file.py
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, 'flows')
import ban_flow


# log location
logsLocation = p("logging.file_path") 
INTERNAL_TOKEN = "Uj1wCJ8AOm59M68loyEpOL8Eu4Xk24EB"
app = Flask(__name__)

#################################
# authentication                #
#################################

auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth(scheme='Bearer')


tokens = {'k6YC5JO44ZMAJF1JFB7qEx4rc8LkGt3K6aJl218P65K03xXUx26ElP1EkKcnBy4rVCYRrYYC3tRNjxaxThDo4LmNafdBkXm6ykNCfl1pJZ2UJSwa3PNoLjORhcyxECtEk0ZJcRk6Ur8TQqoelfxXsqxgszruvvvx2j10b46Kv2zhvzbeYzLKN693vNKXhy2pqETf5uv9IbZIRJV7KxOwSzL3feYhUDMK9nhuvyMNbyvfXSSBcU45j2cY6OVqCoQAa4EBFCZ4iSQeQF2nS2osUrnRK6TcWBmBx07VFO4mUkxe58X65ECas4k6Qjrvwi2jiQEchYZfHWIDF0sZ7KQ2564ClTgGcRWw1yaIWple1nBQImWDw5X5r1Tht1woKjuE0Pq7CB27haHzzpNst5vjjflmBHUIbHdQZcOPx5E0jhF1iuA8Xsgf9HvrpTxlVGJCsUjqXGd7gqQrMtDcihVVkobZ1u0bVzqmP0agXq4Ndg1RbJMreeAYAmEGfcKG2N7z': {'user': 'scruffy', 'created': 1710198638.5790105}}
last_attempts= {}
# Salted passwords stored in a file
PASSWORD_FILE = "passwords.txt"
# Define the retry timer duration (in seconds)
RETRY_TIMER = 5 * 60  # 5 minutes

# Store the last failed authentication attempt time
last_failed_auth_time = {}

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
    authenticated = False
    if username in passwords:
        salt, password_hash = passwords[username]
        authenticated = password_hash == hashlib.sha256((password + salt).encode()).hexdigest()
        if not authenticated:
            global last_failed_auth_time
            last_failed_auth_time[request.remote_addr + ":"+  request.authorization.username] = time.time()
            return False
        else:
            return True
    return False

def bruteforceChecker(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.headers.get('Authorization').split()[1] == INTERNAL_TOKEN:
            return func(*args, **kwargs)
        global last_failed_auth_time
        id = request.remote_addr + ":"+  (request.authorization.username or "132456")
        # If the last failed authentication attempt occurred more than 5 minutes ago
        if not (id in last_failed_auth_time): 
            return func(*args, **kwargs)
        if time.time() - last_failed_auth_time[id] > RETRY_TIMER:
            del last_failed_auth_time[id]
            return func(*args, **kwargs)
        # Otherwise, return a response indicating the retry timer is active
        return Response('Retry timer active. Please wait.', status=429)
    return wrapper

# Issue a token after successful basic authentication
@app.route('/api/authenticate', methods=['POST'])
@bruteforceChecker
@auth.login_required
def authenticate():
    username = request.authorization.username
    token = ''.join(secrets.choice(string.ascii_letters + string.digits) for x in range(512))
    tokens[token] = ({
            "user":username,
            "created": time.time()
        })
    print(tokens)
    return jsonify({'token': token}), 200



# Protect other APIs with token authentication
@app.route('/api/protected', methods=['GET'])
@bruteforceChecker
@token_auth.login_required
def protected():
    if is_token_expired(request.headers.get('Authorization').split()[1]):
        return jsonify({'message': 'Token expired'}), 401
    return jsonify({'message': 'Access granted'}), 200

@token_auth.verify_token
def verify_token(token):
    if token == INTERNAL_TOKEN: # DEBUG
        return INTERNAL_TOKEN # DEBUG
    if token in tokens:
        return tokens[token]
    global last_failed_auth_time
    last_failed_auth_time[request.remote_addr + ":132456"] = time.time()

# Check if a token has expired
def is_token_expired(token):
    token = token.split()[1]
    if token == INTERNAL_TOKEN:
        return False # DEBUG
    if time.time() - tokens[token]['created'] > 30 * 60:
        return True
    else:
        tokens[token]['created'] = time.time()
        return False
    
def lookup_user(token):
    token = token.split()[1]
    if token == INTERNAL_TOKEN:
        return "communityBot"
    return tokens[token]['user']
#########################################

# ban endpoints
@app.route('/api/server/unban', methods=['GET'])
@bruteforceChecker
@token_auth.login_required
async def unban_list():
    if is_token_expired(request.headers.get('Authorization')):
        return jsonify({'message': 'Token expired'}), 401
    _uuid = request.headers.get('X-Correlation-ID') if request.headers.get('X-Correlation-ID') else uuid.uuid4()

    response = ban_flow.unban(_uuid)
    if isinstance(response,Error):
        return Response(response.to_json(), mimetype='application/json'), response.statusCode()
    await post_alert("bot_log",f"user: {lookup_user(request.headers.get('Authorization'))} is retrieving the ban list")
    return Response(json.dumps(response), mimetype='application/json')


@app.route('/api/server/unban/<id>', methods=['GET'])
@bruteforceChecker
@token_auth.login_required
async def get_unbannedPersonById(id):
    if is_token_expired(request.headers.get('Authorization')):
        return jsonify({'message': 'Token expired'}), 401
    _uuid = request.headers.get('X-Correlation-ID') if request.headers.get('X-Correlation-ID') else uuid.uuid4()

    response = ban_flow.unban(_uuid,id)
    if isinstance(response,Error):
        return Response(response.to_json(), mimetype='application/json'), response.statusCode()
    # await post_alert("bot_log",f"user: {lookup_user(request.headers.get('Authorization'))} is retrieving the ban list")
    return Response(json.dumps(response), mimetype='application/json')
    

@app.route('/api/server/ban', methods=['GET'])
@bruteforceChecker
@token_auth.login_required
async def get_ban_list():
    print(request.headers.get('Authorization'))
    if is_token_expired(request.headers.get('Authorization')):
        return jsonify({'message': 'Token expired'}), 401
    
    _uuid = request.headers.get('X-Correlation-ID') if request.headers.get('X-Correlation-ID') else uuid.uuid4()

    filtered = request.args.get('showAll')
    response = ban_flow.getBanList(_uuid,filtered)
    
    if isinstance(response,Error):
        return Response(response.to_json(), mimetype='application/json'), response.statusCode()
    # post_alert("bot_log",f"user: {lookup_user(request.headers.get('Authorization'))} is retrieving the ban list")
    return Response(json.dumps([person.__dict__ for person in response]), mimetype='application/json')


@app.route('/api/server/ban/transform', methods=['GET'])
@bruteforceChecker
@token_auth.login_required
async def create_transformed_ban_list():
    if is_token_expired(request.headers.get('Authorization')):
        return jsonify({'message': 'Token expired'}), 401
    _uuid = request.headers.get('X-Correlation-ID') if request.headers.get('X-Correlation-ID') else uuid.uuid4()

    response = ban_flow.transform(_uuid)
    if isinstance(response,Error):
        return Response(response.to_json(), mimetype='application/json'), response.statusCode()
    # await post_alert("bot_log",f"user: {lookup_user(request.headers.get('Authorization'))} is retrieving the ban list")
    return Response(json.dumps(response), mimetype='application/json')


@app.route('/api/server/ban', methods=['POST'])
@bruteforceChecker
@token_auth.login_required
async def post_ban():
    if is_token_expired(request.headers.get('Authorization')):
        return jsonify({'message': 'Token expired'}), 401
    _uuid = request.headers.get('X-Correlation-ID') if request.headers.get('X-Correlation-ID') else uuid.uuid4()

    data = request.get_json()
    response = ban_flow.ban(_uuid,data)
    if isinstance(response,Error):
        return Response(response.to_json(), mimetype='application/json'), response.statusCode()
    # await post_alert("bot_log",f"user: {lookup_user(request.headers.get('Authorization'))} is retrieving the ban list")
    return Response(json.dumps({"message" :'banned person inserted with id: ' + str(data['steamid'])}), mimetype='application/json')


@app.route('/api/server/ban/<id>', methods=['GET'])
@bruteforceChecker
@token_auth.login_required
async def get_bannedperson_by_id(id):
    if is_token_expired(request.headers.get('Authorization')):
        return jsonify({'message': 'Token expired'}), 401
    _uuid = request.headers.get('X-Correlation-ID') if request.headers.get('X-Correlation-ID') else uuid.uuid4()

    response = ban_flow.get_ban(_uuid,id)
    if isinstance(response,Error):
        return Response(response.to_json(), mimetype='application/json'), response.statusCode()
    # await post_alert("bot_log",f"user: {lookup_user(request.headers.get('Authorization'))} is retrieving the ban list")
    return Response(json.dumps(response.__dict__), mimetype='application/json')


@app.route('/api/server/ban/<id>', methods=['PATCH'])
@bruteforceChecker
@token_auth.login_required
async def patch_bannedperson_by_id(id):
    if is_token_expired(request.headers.get('Authorization')):
        return jsonify({'message': 'Token expired'}), 401
    _uuid = request.headers.get('X-Correlation-ID') if request.headers.get('X-Correlation-ID') else uuid.uuid4()

    data = request.get_json()
    
    response = ban_flow.edit_ban(_uuid,data,id)
    if isinstance(response,Error):
        return Response(response.to_json(), mimetype='application/json'), response.statusCode()
    # await post_alert("bot_log",f"user: {lookup_user(request.headers.get('Authorization'))} is retrieving the ban list")
    return Response(json.dumps(response.__dict__), mimetype='application/json')




'''
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

'''
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


#############################################################################################
# main utility functions
def post_alert(channel, message):
    queue.put((channel, message))
    print(f"Message added to the queue: Channel={channel}, Message={message}")

# Start the scheduler in a separate thread
scheduler_thread = Thread(target=scheduledJob.run_scheduler)
scheduler_thread.start()

if __name__ == '__main__':
    queue = multiprocessing.Queue()
    app.run(debug=True, port=8001)

