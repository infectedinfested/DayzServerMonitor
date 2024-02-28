
import csv

class BannedPerson:
    uniqueid= ""
    active = 1
    steamid = 0
    reason = ""
    time = ""
    startDate = ""
    comment = ""

    def __init__(self,  steamid, reason, time,  startDate, comment, uniqueid=0, active=0,):
        if uniqueid == 0:
            with open('DayZServerBackup20220728/ban.csv', 'r') as csvfile:
                reader = csv.reader(csvfile)
                
                # Read all lines into a list
                lines = list(reader)
            uniqueid = int(lines[-1][0])+1
        if active == 0:
            active = "True"

        self.uniqueid = uniqueid
        self.active = active
        self.steamid = steamid
        self.reason = reason
        self.time = time
        self.startDate = startDate
        self.comment = comment




    def __str__(self):
        return f"Id: {self.uniqueid}, active: {self.active}, steamId: {self.steamid}, reason: {self.reason}, time: {self.time},startDate: {self.startDate}, comment: {self.comment}"
