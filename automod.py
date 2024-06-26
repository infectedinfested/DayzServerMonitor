from datetime import date, datetime,  timedelta
import requests
import os
import re
import yaml

import json
import pandas as pd

from enum import Enum

class Type(Enum):
    interval = "interval"
    ban = "ban"

def p(path):
    path = path.split(".")
    with open("settings.yaml", 'r') as f:
        try:
            settings = yaml.safe_load(f)
            for i in path:
                settings = settings.get(i)
            f.close()
            return settings
            
        except Exception as e:
            f.close()
            return False


log_dir = p('dayz.root')+p('dayz.log_dir')
# dateToScanFolder = date.today() - timedelta(days=1)
#to_scan = "2022_06_14"
typeToScan = ".ADM"
dateToScan = [date.today()]
printLines = []



def getMaxDistanceByWeapon(weapon: str, type: Type):
    try:
        maxDistance = p("autoMod.maxWeaponDistance.weapons."+ weapon +"."+ str(type.value))
        if maxDistance:
            return maxDistance
        return 10000
    except Exception as e:
        print("autoMod.maxWeaponDistance."+ weapon +"."+ str(type.value))
        print("no max distance found for:" + weapon)
        return 10000


def weaponExists(weapon: str):
    print(weapon)
    value = p("autoMod.maxWeaponDistance.weapons."+ weapon)
    if value: 
        return True
    return False

def check_within_5_seconds(date_list, maximumOccurance, timespan):

    try:
        newMaxOccurance = p("autoMod.maxWeaponDistance.weapons."+ weapon +".maxWarningAmount")
        if newMaxOccurance:
            maximumOccurance = newMaxOccurance
        newTimespan = p("autoMod.maxWeaponDistance.weapons."+ weapon +".maxWarningTimeSpan")
        if newTimespan:
            timespan = newTimespan
    except Exception as e:
        print("no custom values found")

    def check_dates(dates, maximumOccurance, timespan):
        if len(dates) < maximumOccurance:
            return False
        
        # Convert string times to datetime objects
        datetime_dates = [datetime.strptime(date, '%H:%M:%S') for date in dates]
        
        # Sort datetime objects
        datetime_dates.sort()
        
        # Check if there are at least 3 dates within 5 seconds
        for i in range(len(datetime_dates) - (maximumOccurance-1)):
            tim = (datetime_dates[i + (maximumOccurance-1)] - datetime_dates[i]).total_seconds()
            print(tim)
            print(timespan)
            print(tim <= timespan)
            if (datetime_dates[i + (maximumOccurance-1)] - datetime_dates[i]).total_seconds() <= timespan:
                return True
        return False
    player_id = next(iter(date_list.keys()))

    for wpnEntry in next(iter(date_list.values())):
        weapon = next(iter(wpnEntry))
        dates = wpnEntry[weapon]
        distance = getMaxDistanceByWeapon(weapon,Type.interval)
        has_three_dates_within_5_seconds = check_dates(dates, maximumOccurance, timespan)
        if has_three_dates_within_5_seconds:
            printLines.append(f"ID: {player_id}, Weapon: {weapon}, Has {maximumOccurance} hits lower than {distance} meters within {timespan} seconds. Banning!")
            #print(f"ID: [REDACTED], Weapon: {weapon}, Has {maximumOccurance} hits lower than {distance} meters within {timespan} seconds. Banning!")

def read_file(file_name):
    print(file_name)
    with open(log_dir+file_name, 'r', encoding="utf8") as file:
        return fill_statistics(file, file_name)
          

def parse_log_line(line,filename):
    day = filename[17:25].replace("_","-")
    splitted_log = (line.replace('|',' ').replace('   P',' | p').replace('>) ', '>)| ').replace('] h', ']| h').replace('] k', ']| k').split('|'))
    hit_by_what = None
    location = None
    weapon_used = None
    other = None
    player_pos = None
    alive = None
    player_hp = None
    hit_by_whom = None
    distance = None
    if len(splitted_log)>2:
        #try:
            #print(line)
            if ((len(line) > 120)):
                splitted_log = splitted_log + ['']
                time = splitted_log[0].replace(" ","")
                matches = re.match(r' player\s+(.*?)\s+\(id=([^ ]+) pos=<([^>]+)>\)(?:\[HP:\s*([\d.]+)\])?', splitted_log[1])
                print(matches)
                print(line)
                if matches:
                    player_name = matches.group(1)
                    player_id = matches.group(2)
                    player_pos = matches.group(3)
                    player_hp = float(matches.group(4)) if matches.group(4) else 100
                else:
                    return None
                print(player_name)
                
                log_data = splitted_log[2][1:]
                hit_by_what = log_data
                if log_data.startswith("killed by"):
                    if log_data.startswith("killed by Player"):
                        hit_by_what = "Player"
                        killedBy_pattern = r'killed by Player \"([^"]+)\" \(id=([^ ]+) pos=.*'
                        killedBy_match = re.match(killedBy_pattern, splitted_log[2][1:])
                        if killedBy_match:
                            hit_by_whom = {"player_name": killedBy_match.group(1),"player_id": killedBy_match.group(2) }
                        #print(hit_by_what)
                        try:
                            weapon_used = splitted_log[3][1:].split()[1]
                            distance = int(str(splitted_log[3][1:].split()[3]).split('.')[0])
                            #print(distance)
                        except Exception as e:
                            #print("can't parse casting to FIST " + line)
                            weapon_used = "Fist"
                    elif (log_data.startswith("killed by with") or log_data.startswith("killed by TripwireTrap")):
                        hit_by_what = "Player set grenade trap"
                        #print(hit_by_what)
                        try:
                            weapon_used = splitted_log[3][1:].split()[1]
                        except Exception as e:
                            weapon_used = ""
                    elif log_data.startswith("killed by FallDamage"):
                        hit_by_what = "FallDamage"
                        #print(hit_by_what)
                    elif (log_data.startswith("killed by Fen") or log_data.startswith("killed by Watch")) :
                        hit_by_what = "BarbWire"
                        #print(hit_by_what)
                    elif log_data.replace(' ', '').endswith("TransportHit"):
                        hit_by_what = log_data.split()[2]
                        #print(hit_by_what)
                    elif (log_data.startswith("killed by Zm") or log_data.startswith("killed by Inf")):
                        hit_by_what = "Zombie"
                        #print(hit_by_what)
                    elif log_data.startswith("killed by Animal_Can"):
                        hit_by_what= "Wolf"
                        #print(hit_by_what)
                    elif log_data.startswith("hit by Animal_Urs"):
                        hit_by_what= "Bear"
                        #print(hit_by_what)
                    elif log_data.startswith("killed by Fireplace"):
                        hit_by_what = "Fireplace"
                        #print(hit_by_what)
                    elif "with" in log_data:
                        hit_by_what = log_data.split()[2]
                        #location = log_data.split()[4]
                        #print(log_data)
                        #print(file_name)
                    else:
                        hit_by_what= log_data.split()[2]
                        #location = log_data.split()[4]
                        #print(log_data)
                        #print(file_name)

                    
                elif log_data.startswith("hit by"):
                    if log_data.startswith("hit by Player"):
                        hit_by_what= "Player"
                        #print(hit_by_what)
                        location = splitted_log[3][1:].split()[1]
                        

                        hitBy_pattern = r'hit by Player \"([^"]+)\" \(id=([^ ]+) pos=.*'
                        hitBy_match = re.match(hitBy_pattern, splitted_log[2][1:])
                        if hitBy_match:
                            hit_by_whom = {"player_name": hitBy_match.group(1),"player_id": hitBy_match.group(2) }
                        try:
                            weapon_used = splitted_log[3][1:].split()[7]
                            distance = int(str(splitted_log[3][1:].split()[9]).split('.')[0])
                        except Exception as e:
                            #print("can't parse casting to FIST " + line)
                            weapon_used = "Fist"
                    elif (log_data.startswith("hit by  with") or log_data.startswith("hit by TripwireTrap")):
                        hit_by_what = "Player set grenade trap"
                        #print(hit_by_what)
                        try:
                            weapon_used = splitted_log[3][1:].split()[1]
                        except Exception as e:
                            weapon_used = ""
                    elif log_data.startswith("hit by FallDamage"):
                        hit_by_what= "FallDamage"
                        #print(hit_by_what)
                    elif log_data.startswith("hit by Fen") or log_data.startswith("hit by Watch") :
                        hit_by_what = "BarbWire"
                        #print(hit_by_what)
                    elif log_data.replace(' ', '').endswith("TransportHit"):
                        hit_by_what = log_data.split()[2]
                    elif (log_data.startswith("hit by Zm") or log_data.startswith("hit by Inf")):
                        hit_by_what= "Zombie"
                        #print(hit_by_what)
                        location = log_data.split()[4]
                    elif log_data.startswith("hit by Animal_Can"):
                        hit_by_what= "Wolf"
                        #print(hit_by_what)
                        location = log_data.split()[4]
                    elif log_data.startswith("hit by Animal_Urs"):
                        hit_by_what= "Bear"
                        #print(hit_by_what)
                        location = log_data.split()[4]
                    elif log_data.startswith("hit by Fireplace"):
                        hit_by_what = "Fireplace"
                        #print(hit_by_what)
                    elif "with" in log_data:
                        hit_by_what = log_data.split()[2]
                        #location = log_data.split()[4]
                        #print(log_data)
                        #print(file_name)
                    else:
                        hit_by_what= log_data.split()[2]
                        #location = log_data.split()[4]
                        
                        #print(log_data)
                        #print(file_name)
                elif log_data.startswith(""):
                    return None
            else:
                return None
            
        #except Exception as e:
        #    print(e)
        #    print(line)
        #    return None
    else:
        Login_pattern = r'(\d{2}:\d{2}:\d{2}) \| Player \"([^"]+)\" is connected \(id=([^\)]+)\)'
        Logout_pattern = r'(\d{2}:\d{2}:\d{2}) \| Player \"([^"]+)\"\(id=([^\)]+)\) has been disconnected'
        Login_match = re.match(Login_pattern, line)
        Logout_match = re.match(Logout_pattern, line)
        if Login_match:
            time = Login_match.group(1)
            player_name = Login_match.group(2)
            player_id = Login_match.group(3)
            other = "connected"
        elif Logout_match:
            time = Logout_match.group(1)
            player_name = Logout_match.group(2)
            player_id = Logout_match.group(3)
            other = "disconnected"
        else:
            # everything here can't be parsed
            return None
    
    # Return the extracted information as a dictionary
    return {
        "day": day,
        "time": time,
        "player_name": player_name,
        "player_id": player_id,
        "pos": player_pos,
        "alive": alive,
        "hp": player_hp,
        "event": {
            "hit_by": hit_by_what,
            "location": location,
            "weapon_used": weapon_used,
            "distance": distance,
            "other": other,
            "hit_by_whom": hit_by_whom,
        }        
    }
def fill_statistics(file,fileName):
    last_player_line = []
    json_logData = []
    for log_line in file:
        log = parse_log_line(log_line,fileName)
        if log:
            json_logData.append(log)
    return json_logData
    
    
    
def run():
    files_in_dir = os.listdir(log_dir)
    filtered_files = []
    for date in dateToScan:
        filtered_files = filtered_files + list(filter(lambda x: str(date.strftime('%Y_%m_%d')) in x and x.endswith(typeToScan), files_in_dir))

    
    json_logData = []
    #for file in [filtered_files[-1]]:
    for file in filtered_files:
        json_logData = json_logData + read_file(file)
    
    #print(json_logData)
    with open("LogChecker.json", 'w') as file:
        json.dump(json_logData, file, indent=4)

    df = pd.DataFrame(json_logData)

    filtered_df = df[df['event'].apply(lambda x: x.get('distance') is not None and x.get('distance') > 5)]

    # check hit on max distance for weapon BAN
    filteredByWeaponBan_df = df[df.apply(lambda row: row['event']['distance'] is not None and row['event']['weapon_used'] is not None and 
                           row['event']['distance'] > getMaxDistanceByWeapon(row['event']['weapon_used'],Type.ban), 
                           axis=1)]
    # check hit on max distance for weapon interval
    filteredByWeaponWarn_df = df[df.apply(lambda row: row['event']['distance'] is not None and row['event']['weapon_used'] is not None and 
                           row['event']['distance'] > getMaxDistanceByWeapon(row['event']['weapon_used'],Type.interval), 
                           axis=1)]

    player_shot_counts = []
    exist = False
    for i in json_logData:
        if i['event']['distance'] and i['event']['weapon_used'] and i['event']['hit_by_whom']:
            
            #player_id = i['event']['hit_by_whom']
            player_id = i['player_id']
            distance = i['event']['distance']
            weapon_used= i['event']['weapon_used']
            if not weaponExists(weapon_used):
                global printLines
                printLines.append("no max distance found for: " + weapon_used)
            if distance is not None and distance > getMaxDistanceByWeapon(weapon_used,Type.interval):
                exist = False
                for obj in player_shot_counts:
                    exist = True
                    if player_id in obj:
                        if weapon_used in obj[player_id][0]:
                            for wpn in obj[player_id]:
                                wpn[weapon_used].append(i['time'])
                        else:
                            for wpn in obj[player_id]:
                                wpn[weapon_used] = [i['time']]
                    else:
                        player_shot_counts.append({player_id: [{weapon_used: [i['time']]}]})
                if not exist:
                    player_shot_counts.append({player_id: [{weapon_used: [i['time']]}]})
    print(player_shot_counts)
    print("----------------------------------------------------------------")
    # checking iterative distance
    for player in player_shot_counts:
        check_within_5_seconds(player,p('autoMod.maxWeaponDistance.maxWarningAmount'),p('autoMod.maxWeaponDistance.maxWarningTimeSpan'))
    # checking max distance 
    filteredByWeaponBan_df.to_json('output.json', orient='records')
    for i in filteredByWeaponBan_df.to_dict(orient='records'):
        player_id = i['player_id']
        event = i['event']
        distance = event['distance']
        weapon = event['weapon_used']
        #print(f"ID: [REDACTED], Weapon: {weapon} hit from distance: {distance}. Banning!")
        printLines.append(f"ID: {player_id}, Weapon: {weapon} hit from distance: {distance}. Banning!")


    # checking combat log
    monitorList = []
    reverted_logData = json_logData[::-1]
    for log in reverted_logData:
        def is_time_within_x_minutes(monitorList,target_id, target_time):
            for item in monitorList:
                if item['id'] == target_id:
                    stored_time = datetime.strptime(item['time'], '%H:%M:%S')
                    target_time = datetime.strptime(target_time, '%H:%M:%S')
                    time_difference = abs(target_time - stored_time)
                    if time_difference <= timedelta(minutes=p('autoMod.combatlogTimeMinutes')):
                        return True
                    else:
                        monitorList.remove(item)
                        return False
            return False
        def remove_item_by_id(monitorList,target_id):
            monitorList[:] = [item for item in monitorList if item['id'] != target_id]

        if log['event']['other'] == "disconnected":
            monitorList.append({"id": log['player_id'], "time": log['time']})
        if log['event']['other'] == "connected":
            remove_item_by_id(monitorList,log['player_id'])

        if log['hp'] is not None and log['hp'] < 1:
            remove_item_by_id(monitorList,log['player_id'])
        if log['event']['hit_by_whom']:
            if is_time_within_x_minutes(monitorList,log['event']['hit_by_whom']['player_id'],log['time']):
                printLines.append(f"{log['time']} ID: {log['event']['hit_by_whom']['player_id']}, combat logged. Banning!")
            if is_time_within_x_minutes(monitorList,log['player_id'],log['time']):
                printLines.append(f"{log['time']} ID: {log['player_id']}, combat logged. Banning!")







    printLines = list(set(printLines))
    if printLines:
        message = '\n- '.join(printLines)
        message = f"Server restarted, a rapport got generated from following file: {filtered_files[-1]}\n- " + message
    else: 
        message = f"Server restarted, a rapport got generated from following file: {filtered_files[-1]}\n- No sus behavior found"
    payload = {"channel": "automod-log", "message":message}
    print(message)
    response = requests.post("http://127.0.0.1:5000/api/discord/send", json=payload)
    if response.status_code == 200:
        print("POST request was successful!")
        print("Response:", response.json())
    else:
        print("POST request failed with status code:", response.status_code)
    
run()