import csv
import sys
from typing import List

batch_script_directory = ""

def toBool(val):
    if val in ('y', 'yes', 't', 'true', 'True', '1', 1):
        return 'True'
    elif val in ('n', 'no', 'f', 'false', 'False', '0', 0):
        return "False"
    else:
        raise ValueError("invalid truth value %r" % (val,))

class BannedPerson:
    uniqueid= ""
    active = False
    steamid = 0
    reason = ""
    time = ""
    startDate = ""
    comment = ""

    def __init__(self,  steamid, reason, time,  startDate, comment, uniqueid=0, active=False,):
        if uniqueid == 0:
            with open("ban.csv", 'r') as csvfile:
                reader = csv.reader(csvfile)
                
                # Read all lines into a list
                lines = list(reader)
            uniqueid = int(lines[-1][0])+1
        if isinstance(active, bool):
            self.active = active
        else:
            self.active = toBool(active)

        self.uniqueid = uniqueid
        self.steamid = steamid
        self.reason = reason
        self.time = time
        self.startDate = startDate
        self.comment = comment

    def __str__(self):
        return f"Id: {self.uniqueid}, active: {toBool(self.active)}, steamId: {self.steamid}, reason: {self.reason}, time: {self.time},startDate: {self.startDate}, comment: {self.comment}"

def _readBanCSV():
    bannedPersons= []
    with open("ban.csv", 'r') as file:
        reader = csv.DictReader(file)
        next(reader)
        for row in reader:
            try:
                bannedPerson = BannedPerson(row['steamid'], row['reason'], row['time'], row['startDate'], row['comment'], row['uniqueid'], toBool(row['active']))
                bannedPersons.append(bannedPerson)
            except Exception as e:
                print(e)
                print(row)
    file.close()
    return bannedPersons


def _writeBanTXT(bannedPersons: List[BannedPerson], insert: bool = False):
    j = "a" if insert else "w"
    try:
        with open("ban.txt", j ) as file:
            if not insert:
                header = "//Players added to the ban.txt won't be able to connect to this server.\n//Bans can be added/removed while the server is running and will come in effect immediately, kicking the player.\n//-----------------------------------------------------------------------------------------------------\n//To ban a player, add his player ID (44 characters long ID) which can be found in the admin log file (.ADM).\n//-----------------------------------------------------------------------------------------------------\n//For comments use the // prefix. It can be used after an inserted ID, to easily mark it.\n\n//AABBBCCCCDDDDDEEEEDDDDDFFFF //Example of a character ID\n\n"
                file.write(header)
            for person in bannedPersons:
                line = ""
                if person.active != "True":
                    line += "//"
                file.write(line + person.steamid + " // " + person.reason + " // Length:" + person.time+ " // Starting from:" + person.startDate + " // "+ person.comment+"\n")
        file.close()
    except Exception as e:
        print(e)
    return 'write successfull'





def main():


    # Now you can use the batch script directory as needed in your script
    _writeBanTXT(_readBanCSV(),False)
if __name__ == "__main__":
    main()



