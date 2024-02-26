from flask import Flask, request
from threading import Thread

import sched
import time
import json


import scheduledJob

# log location
logsLocation = "/communityZ"

app = Flask(__name__)

@app.route('/api/ban', methods=['GET'])
def get_ban_list():
    filtered = request.args.get('showComment')

    return_lines = ""
    with open('DayZServerBackup20220728/ban.txt', 'r') as file:
        for line in file:
            if filtered =="True":
                return_lines += line
            else: 
                if not line.startswith("//"):
                    return_lines += line
    return return_lines

@app.route('/api/ban', methods=['POST'])
def post_ban_list():
    data = request.get_json()
    
    #body content
    user = data.get('user', '')
    comment = data.get('comment', '')
    time = data.get('time', '')

    with open('DayZServerBackup20220728/ban.txt', 'a') as file:
        file.write('\n' + user + ' // ' + comment)

    return 'write successfull'



# Start the scheduler in a separate thread
scheduler_thread = Thread(target=scheduledJob.run_scheduler)
scheduler_thread.start()

if __name__ == '__main__':
    app.run(debug=True)
