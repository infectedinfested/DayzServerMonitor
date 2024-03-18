#public imports
import csv

#local imports
from classes import BannedPerson, Error
from common import toBool,get_timeDelta, p
from datetime import datetime
from typing import List

fieldnames = ['uniqueid','active','steamid','ticket','time','startDate','comment']

def unban(uuid = "",id = 0):
    if id == 0:
        _unbanCheck()
        return ({"message":"Running unban scrip"})
    else:
        bannedpeople = []
        bannedPerson = None
        try:
            for row in _readBanCSV():
                if not row['uniqueid'] == id:
                    try:
                        bannedPerson = BannedPerson(row['steamid'], row['ticket'], row['time'], row['startDate'], row['comment'], row['uniqueid'], toBool(row['active']))
                        bannedpeople.append(bannedPerson, True)
                    except Exception as e:
                        return Error(e,uuid)
            updateBanFiles()
            return ({"message":"unbanning player" + bannedPerson['steamid']})
        except Exception as e:
            return Error(e,uuid)
       
   
def getBanList(uuid,filtered):
    try:
        BannedPeople = _readBanCSV()
        if filtered !="True":
            BannedPeople = [person for person in BannedPeople if person.active]
        return BannedPeople  
    except Exception as e:
        print(e)
        return Error(e,uuid)

def ban(uuid,data):
    bannedPersons = []
    if len(data.get('steamid', '').split(","))==1:
        print("one culprit")
        bannedPerson = BannedPerson(data.get('steamid', ''), data.get('ticket', ''), data.get('time', ''), data.get('startDate', ''),data.get('comment', ''))
        bannedPersons.append(bannedPerson)
    else:
        print("multiple culprit")
        for steamid in data.get('steamid', '').split(","):
            bannedPerson = BannedPerson(steamid, data.get('ticket', ''), data.get('time', ''), data.get('startDate', ''),data.get('comment', ''))
            bannedPersons.append(bannedPerson)
    try:
        updateBanFiles(bannedPersons, True)
        return ({"message":"banning player " + str(data.get('steamid', ''))})
    except Exception as e:
        return Error(e, uuid)

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
                                    str(not line[0].startswith("//")) +","+  
                                    line[0].replace('//', '') +","+
                                    line[1] +","+ 
                                    line[2] +","+ 
                                    line[3] +","+ 
                                    line[4] + '\n')
                    counter += 1

        return_lines = "uniqueid,active,steamid,ticket,time,startDate,comment\n" + return_lines
        with open('DayZServerBackup20220728/ban.csv', 'w') as file:
            file.write(return_lines)
        return {"message": "transformation successfull"} 
    except Exception as e:
        return Error(e,uuid)

def get_ban(uuid,id) -> BannedPerson:
    try:
        for bannedPerson in _readBanCSV():
            if bannedPerson.uniqueid == id:
                return bannedPerson
                #json_data = json.dumps(bannedPerson.__dict__)
    except Exception as e:
        return Error(e,uuid)
    
def edit_ban(uuid, data, id) -> BannedPerson:
    try:
        changeMade = False
        bannedPersons = _readBanCSV()
        # Find the row with the desired ID and edit it
        for bannedPerson in bannedPersons:
            if isinstance(bannedPerson,BannedPerson):
                if bannedPerson.uniqueid == id:  # Assuming 'ID' is the name of the unique identifier column
                    bannedPerson.active = toBool(data['active']) if data['active'] else bannedPerson.active
                    bannedPerson.comment = data['comment'] if data['comment'] else bannedPerson.comment
                    bannedPerson.ticket = data['ticket'] if data['ticket'] else bannedPerson.ticket
                    bannedPerson.startDate = data['startDate'] if data['startDate'] else bannedPerson.startDate
                    bannedPerson.time = data['time'] if data['time'] else bannedPerson.time
                    changeMade = True
            else:
                print(f"row can't be cast to bannedPerson: {bannedPerson}")
        if changeMade:
            _writeBanCSV(bannedPersons, False)
            _writeBanTXT(bannedPersons, False)
            return {"message": "update successful"} 
        else:
            return {"message": "no updates made"} 
    except Exception as e:
        return Error(e,uuid)
    
    






def updateBanFiles(bannedPersons: List[BannedPerson] = False, insert: bool = False):
    if bannedPersons:
        #update csv and txt with bannedPersons dataset
        _writeBanCSV(bannedPersons, insert)
        _writeBanTXT(bannedPersons, insert)
    else:
        #synch csv ->
        bannedPersons = _readBanCSV()
        _writeBanTXT(bannedPersons, False)
        
def _readBanCSV():
    bannedPersons= []
    with open(p("dayz.root")+p("dayz.ban.file_csv_path"), 'r') as file:
        reader = csv.DictReader(file)
        next(reader)
        for row in reader:
            try:
                bannedPerson = BannedPerson(row['steamid'], row['ticket'], row['time'], row['startDate'], row['comment'], row['uniqueid'], toBool(row['active']))
                bannedPersons.append(bannedPerson)
            except Exception as e:
                print(e)
                print(row)
    file.close()
    return bannedPersons

def _writeBanCSV(bannedPersons: List[BannedPerson], insert: bool = False):
    try:
        if not insert:
            with open(p("dayz.root")+p("dayz.ban.file_csv_path"), 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                for bannedPerson in bannedPersons:
                    writer.writerow({'uniqueid': bannedPerson.uniqueid, 'active': bannedPerson.active, 'steamid': bannedPerson.steamid, 'ticket': bannedPerson.ticket, 'time': bannedPerson.time, 'startDate': bannedPerson.startDate, 'comment': bannedPerson.comment  })
                file.close()
        else: 
            with open(p("dayz.root")+p("dayz.ban.file_csv_path"), 'a', newline='') as file:
                for bannedPerson in bannedPersons:
                    file.write(str(bannedPerson.uniqueid)+","+str(bannedPerson.active)+","+str(bannedPerson.steamid)+","+bannedPerson.ticket+","+str(bannedPerson.time)+","+str(bannedPerson.startDate)+","+bannedPerson.comment+"\n")
                file.close() 
    except Exception as e:
        return Error(e)
    return 'write successfull'

def _writeBanTXT(bannedPersons: List[BannedPerson], insert: bool = False):
    j = "a" if insert else "w"
    try:
        with open(p("dayz.root")+p("dayz.ban.file_path"), j ) as file:
            if not insert:
                header = "//Players added to the ban.txt won't be able to connect to this server.\n//Bans can be added/removed while the server is running and will come in effect immediately, kicking the player.\n//-----------------------------------------------------------------------------------------------------\n//To ban a player, add his player ID (44 characters long ID) which can be found in the admin log file (.ADM).\n//-----------------------------------------------------------------------------------------------------\n//For comments use the // prefix. It can be used after an inserted ID, to easily mark it.\n\n//AABBBCCCCDDDDDEEEEDDDDDFFFF //Example of a character ID\n\n"
                file.write(header)
            for person in bannedPersons:
                line = ""
                if not person.active:
                    line += "//"
                file.write(line + person.steamid + " // " + person.ticket + " // Length:" + person.time+ " // Starting from:" + person.startDate + " // "+ person.comment+"\n")
        file.close()
    except Exception as e:
        return Error(e)
    return 'write successfull'


def _unbanCheck():
    bannedPersons = _readBanCSV()
    
    for person in bannedPersons:
        if isinstance(person,BannedPerson):
            try:
                unban_date = datetime.strptime(person.startDate, "%d-%m-%Y") + get_timeDelta(person.time)
                if (unban_date <= datetime.now() and person.active=="True"):
                    person.active = False
                    print("unbanning; id:"+ str(person.uniqueid) + " steamid: "+ str(person.steamid))
            except Exception as e:
                e = None

    _writeBanCSV(bannedPersons, False)
    _writeBanTXT(bannedPersons, False)

    return None