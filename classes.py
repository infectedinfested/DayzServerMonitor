from datetime import date, datetime
import csv
import json



file_path = 'statistics.json'
substitude_list = {
    "Sawed-off": "Sawed-off Shotgun",
    "Nailed" : "Nailed Baseball bat",
    "SK": "SK 59/66",
    "Baseball": "Baseball Bat", 
    "MK": "MK II",
    "Long": "Longhorn",
    "Sharpened":"Sharpened Stone",
    "Short": "Short Stick",
    "Barbed": "Barbed Baseball Bat"
}

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
    
class Log:
    location = ""
    def __init__(self,  location):
        self.location = location

    def write(self, string):
        with open(self.location, "a" ) as file:
            current_time = datetime.now().strftime('%H:%M:%S')
            file.write(str(current_time) + " | " + string)
        return 'write successfull'  



class Statistics:
    def __init__(self):
        self._data = self._read_data()


    def _read_data(self):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            # If the file doesn't exist, set default values and write them to the file
            statistical_data = {
                'Created': date.today().strftime("%d-%m-%Y"),
                'LastEdit': date.today().strftime("%d-%m-%Y"),
                'TotalUniqueLogins': 0,
                'PlayersLoggedIn': [],
                'TotalPlayersKilled': 0,
                'PlayersKilledBy': [],
                'GunsMostUsed': []
            }
            self._write_data(statistical_data)
            return statistical_data

    def _write_data(self, data):
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def write_data(self):
        self._updateTotalPlayersKilled()
        with open(file_path, 'w') as file:
            json.dump(self._data, file, indent=4)

    def isEmpty(self):
        if self._data['TotalUniqueLogins'] == 0:
            return True
        else:
            return False


    # Getters and setters
    @property
    def Created(self):
        return datetime.strptime(self._data.get("Created"), "%d-%m-%Y")
    @Created.setter
    def Created(self, value):
        self._data["Created"] = value
        #self._write_data(self._data)

    @property
    def LastEdit(self):
        return datetime.strptime(self._data.get("LastEdit"), "%d-%m-%Y")
    @LastEdit.setter
    def LastEdit(self, value):
        self._data["LastEdit"] = value
        #self._write_data(self._data)

    @property
    def TotalUniqueLogins(self):
        return self._data.get("TotalUniqueLogins")
    @TotalUniqueLogins.setter
    def TotalUniqueLogins(self, value):
        self._data["TotalUniqueLogins"] = value
        #self._write_data(self._data)
    def updateUniqueLogins(self, count):
        self._data["TotalUniqueLogins"] += count
        #self._write_data(self._data)

    @property
    def PlayersLoggedIn(self):
        return self._data.get("PlayersLoggedIn")
    @PlayersLoggedIn.setter
    def PlayersLoggedIn(self, value):
        self._data["PlayersLoggedIn"] = value
        #self._write_data(self._data)
    def UpdatePlayerLoggedIn(self, name, id):
        #count = self._data["TotalUniqueLogins"]
        for player_entry in self._data['PlayersLoggedIn']:
            if player_entry['id'] == id:
                player_entry['names'].append(name)
                player_entry['names'] = list(set(player_entry['names']))
                #self._write_data(self._data)
                return
        self._data['PlayersLoggedIn'].append({"id": id, "names": [name]})
        self._data["TotalUniqueLogins"] = len(self._data["PlayersLoggedIn"])
        #self._write_data(self._data)


    @property
    def TotalPlayersKilled(self):
        return self._data.get("TotalPlayersKilled")
    @TotalPlayersKilled.setter
    def TotalPlayersKilled(self, value):
        self._data["TotalPlayersKilled"] = value
        #self._write_data(self._data)
    def UpdatePlayerKilled(self):
        self._data["TotalPlayersKilled"] += 1


    @property
    def PlayersKilledBy(self):
        return self._data.get("PlayersKilledBy")
    @PlayersKilledBy.setter
    def PlayersKilledBy(self, value):
        self._data["PlayersKilledBy"] = value
        #self._write_data(self._data)
    @property
    def TotalPlayersKilled(self):
        return self._data.get("TotalPlayersKilled")
    @TotalPlayersKilled.setter
    def TotalPlayersKilled(self, value):
        self._data["TotalPlayersKilled"] = value
    def _updateTotalPlayersKilled(self):
        total_count = 0
        for obj in self._data['PlayersKilledBy']:
            if obj["hazard"] != "Bleeding Out" :
                total_count += obj["counter"]
        self._data['TotalPlayersKilled'] = self._data['TotalPlayersKilled'] - total_count

    @property
    def GunsMostUsed(self):
        return self._data.get("GunsMostUsed")
    @GunsMostUsed.setter
    def GunsMostUsed(self, value):
        self._data["GunsMostUsed"] = value
        #self._write_data(self._data)
    def UpdateGunMostUsed(self, gun):
        for key, value in substitude_list.items():
            if key == gun:
                gun = value
                break
        for item in self._data["GunsMostUsed"]:
            if item['gun'] == gun:
                # If the key exists, increase the counter by 1
                item['counter'] += 1
                return
        self._data["GunsMostUsed"].append({'gun': gun, 'counter': 1})
        #self._write_data(self._data)


    def to_json(self):
        return json.dumps({'Created': self.Created.strftime("%d-%m-%Y"), 'LastEdit': self.LastEdit.strftime("%d-%m-%Y"), 'TotalUniqueLogins': self.TotalUniqueLogins,'PlayersLoggedIn':  self.PlayersLoggedIn, 'TotalUniquePlayerDeaths': self.TotalPlayersKilled ,'PlayersKilledBy': self.PlayersKilledBy, 'GunsMostUsed': self.GunsMostUsed })

