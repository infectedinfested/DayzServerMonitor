from flask import Flask, request
from threading import Thread

import psutil
import time


import sched
import time
import json
import csv

from common import strtobool, create_ban_file
import scheduledJob
from  classes import BannedPerson

# log location
logsLocation = "/communityZ"

app = Flask(__name__)


@app.route('/api/unban', methods=['GET'])
def unban_list():
    scheduledJob.unban()
    return "test"


@app.route('/api/ban', methods=['GET'])
def get_ban_list():
    filtered = request.args.get('showAll')
    BannedPeople = []
    with open('DayZServerBackup20220728/ban.csv', 'r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            bannedPerson = BannedPerson(row['steamid'], row['reason'], row['time'], row['startDate'], row['comment'], row['uniqueid'], strtobool(row['active']))
            BannedPeople.append(bannedPerson)

        if filtered !="True":
            BannedPeople = [person for person in BannedPeople if person.active]

        json_data = json.dumps([person.__dict__ for person in BannedPeople])
    return json_data

@app.route('/api/ban/transform', methods=['GET'])
def create_transformed_ban_list():
    counter = 1
    return_lines = ""
    with open('DayZServerBackup20220728/ban.txt', 'r') as file:
        count=0
        for line in file:
            count +=1
            if count > 9:
                line = line.replace('\n', '')
                line = line.split(" // ") + [""]+ [""]+ [""]+ [""]
                
                return_lines += (str(counter)+ ","+ 
                                 str(not line[0].startswith("// ")) +","+  
                                 line[0].replace('// ', '') +","+
                                 line[1] +","+ 
                                 line[2] +","+ 
                                 line[3] +","+ 
                                 line[4] + '\n')
                counter += 1

    return_lines = "uniqueid,active,steamid,reason,time,startDate,comment\n" + return_lines
    with open('DayZServerBackup20220728/ban.csv', 'w') as file:
        file.write(return_lines)
    return "transformation successfull"



@app.route('/api/ban', methods=['POST'])
def post_ban_list():
    data = request.get_json()
    
    #body content
    bannedPerson = BannedPerson(data.get('steamid', ''), data.get('reason', ''), data.get('time', ''), data.get('startDate', ''),data.get('comment', ''))

    with open('DayZServerBackup20220728/ban.csv', 'a', newline='') as file:
        fieldnames = ['uniqueid','active','steamid','reason','time','startDate','comment']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writerow({'uniqueid': bannedPerson.uniqueid, 'active': bannedPerson.active, 'steamid': bannedPerson.steamid, 'reason': bannedPerson.reason, 'time': bannedPerson.time, 'startDate': bannedPerson.startDate, 'comment': bannedPerson.comment  })

        create_ban_file([bannedPerson], 'a')
    return 'banned person inserted with id:' + str(bannedPerson.uniqueid)


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






# Start the scheduler in a separate thread
scheduler_thread = Thread(target=scheduledJob.run_scheduler)
scheduler_thread.start()

if __name__ == '__main__':
    app.run(debug=True)

