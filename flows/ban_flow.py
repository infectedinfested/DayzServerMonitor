#public imports
import csv

#local imports
import scheduledJob
from classes import BannedPerson
from common import strtobool, create_ban_file,error

def unban(uuid,id = 0):
    if id == 0:
        scheduledJob.unban()
        return ({"message":"Running unban scrip"})
    else:
        print("todo")
        return ({"message":"unbanning player" + str(id)})
   


def getBanList(uuid,filtered):
    BannedPeople = []
    try:
        with open('DayZServerBackup20220728/ban.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                bannedPerson = BannedPerson(row['steamid'], row['reason'], row['time'], row['startDate'], row['comment'], row['uniqueid'], strtobool(row['active']))
                BannedPeople.append(bannedPerson)

        if filtered !="True":
            BannedPeople = [person for person in BannedPeople if person.active]

        file.close()
        return BannedPeople
    except Exception as e:
        return error(e)

def ban(uuid,data):
    bannedPerson = BannedPerson(data.get('steamid', ''), data.get('reason', ''), data.get('time', ''), data.get('startDate', ''),data.get('comment', ''))
    with open('DayZServerBackup20220728/ban.csv', 'a', newline='') as file:
        fieldnames = ['uniqueid','active','steamid','reason','time','startDate','comment']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writerow({'uniqueid': bannedPerson.uniqueid, 'active': bannedPerson.active, 'steamid': bannedPerson.steamid, 'reason': bannedPerson.reason, 'time': bannedPerson.time, 'startDate': bannedPerson.startDate, 'comment': bannedPerson.comment  })

        create_ban_file([bannedPerson], 'a')
    return bannedPerson

def transform(uuid):
    try:
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
        return {"message": "transformation successfull"} 
    except Exception as e:
        return error(e)
