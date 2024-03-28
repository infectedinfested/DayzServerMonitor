from datetime import date, timedelta
import concurrent.futures
from concurrent import futures
import os
from tqdm import tqdm
import re
import time as timer

import json
import pandas as pd


from  classes import Statistics

log_dir = 'DayZServerBackup20220728/communityZNew/'
# dateToScanFolder = date.today() - timedelta(days=1)
#to_scan = "2022_06_14"
typeToScan = ".ADM"
dateToScan = [date.today()]


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
                player_info = (splitted_log[1].replace('(id=','|(id=')).split('|')
                player_pre = player_info[0].replace(' "',' |').replace('" ','|').split('|')
                try:
                    player_name = player_pre[1]
                except Exception as e:
                    print("can't parse line:player_name " + line)
                    return "can't parse line:player_name " + line
                if len(player_pre)>2 and player_pre[2].startswith("(DEAD)"):
                    alive = False
                else:
                    alive = True
                try:
                    player_id_pos = player_info[1].replace('(','').replace(')','').split(" pos")
                except Exception as e:
                    print("can't parse line:player_id_pos" + line)
                    return "can't parse line:player_id_pos" + line
                player_id = player_id_pos[0][3:]
                if player_id_pos[1].endswith("]"):
                    player_pos= (player_id_pos[1].split(">["))[0][2:]
                    player_hp = (player_id_pos[1].split(">["))[1][4:-1]
                else:
                    player_pos = player_id_pos[0]
                    player_hp = "100"
                
                log_data = splitted_log[2][1:]
                hit_by_what = log_data
                #for string in check_list:
                #    # Check if the current string exists in the given string
                #    if string in line:
                #        print(splitted_log[3][1:].split()[1])
                #        print(splitted_log[3][1:])
                #        break  # Exit the loop as soon as a match is found
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
    print("TEST")
    files_in_dir = os.listdir(log_dir)
    filtered_files = []
    for date in dateToScan:
        filtered_files = filtered_files + list(filter(lambda x: str(date.strftime('%Y_%m_%d')) in x and x.endswith(typeToScan), files_in_dir))
    print(filtered_files)

    counter = 1

    # Create a ThreadPoolExecutor with max_workers set to the number of files you want to process concurrently
    '''
    with tqdm(total=len(filtered_files), unit='files') as bar:
        with futures.ProcessPoolExecutor() as pool:
            # Add every asset to a thread pool for processing
            fut = [pool.submit(read_file,statistic, file_name) for file_name in filtered_files]
            for r in futures.as_completed(fut):
                bar.update(counter)

    print("handled " + str(len(filtered_files)) + " logsFiles")
    #print(result)
    '''
    json_logData = []
    for file in filtered_files:
        json_logData = json_logData + read_file(file)
    

    with open("LogChecker.json", 'w') as file:
        json.dump(json_logData, file, indent=4)

    df = pd.DataFrame(json_logData)
    weapon_min_distances = {"ak": 200, "sniper": 500, "IJ-70": 2}

    filtered_df = df[df['event'].apply(lambda x: x.get('distance') is not None and x.get('distance') > 5)]


    filteredByWeapon_df = df[df.apply(lambda row: row['event']['distance'] is not None and row['event']['weapon'] is not None and 
                           row['event']['distance'] > weapon_min_distances.get(row['event']['weapon'], 0), 
                           axis=1)]

    # Display the filtered DataFrame
    print("Filtered DataFrame where 'distance' is not null:")
    print(filtered_df)
    print(filteredByWeapon_df)
    filtered_df.to_json('output.json', orient='records')
        #print(filtered_list)
    #with open("output.json", 'w') as file:
    #    json.dump(filtered_df.to_json(orient='records'), file, indent=4)
    


run()