from datetime import date, timedelta
import concurrent.futures
from concurrent import futures
import os
from tqdm import tqdm
import re
import time as timer

import json


from  classes import Statistics

log_dir = 'DayZServerBackup20220728/communityZ/'
# dateToScanFolder = date.today() - timedelta(days=1)
#to_scan = "2022_06_14"
to_scan = ".ADM"

def filter_by_date(filename):
    return to_scan in filename

def add_or_update_entry(id, log, array = []):
    if array:
        for i, entry in enumerate(array):
            if entry['id'] == id:
                # If the id already exists, overwrite the existing entry
                array[i] = {"id": id, "log": log}
                return
    # If the id doesn't exist, append the new entry to the array
    array.append({"id": id, "log": log})
    return 
def remove_entry_by_id(id_to_remove, array):
    if array:
        for i, entry in enumerate(array):
            if entry['id'] == id_to_remove:
                del array[i]
                return
    return

def read_file(statistic, file_name):
    with open(log_dir+file_name, 'r', encoding="utf8") as file:
        fill_statistics(statistic, file, file_name)
    if not statistic.isEmpty():
        statistic.write_data()      

def parse_log_line(line):

    
    splitted_log = (line.replace('|',' ').replace('   P',' | p').replace('>) ', '>)| ').replace('] h', ']| h').replace('] k', ']| k').split('|'))
    if len(splitted_log)>2:
        #try:
            #print(line)
            if ((len(line) > 120) and (not line.split('"')[2].startswith(" is connected"))) :
                splitted_log = splitted_log + ['']
                time = splitted_log[0]
                player_info = (splitted_log[1].replace('(id=','|(id=')).split('|')
                player_pre = player_info[0].replace(' "',' |').replace('" ','|').split('|')
                try:
                    player_name = player_pre[1]
                except Exception as e:
                    print("can't parse line:player_name " + line)
                    return None
                if len(player_pre)>2 and player_pre[2].startswith("(DEAD)"):
                    alive = False
                else:
                    alive = True
                try:
                    player_id_pos = player_info[1].replace('(','').replace(')','').split(" pos")
                except Exception as e:
                    print("can't parse line:player_id_pos" + line)
                    return None
                player_id = player_id_pos[0][3:]
                if player_id_pos[1].endswith("]"):
                    player_pos= (player_id_pos[1].split(">["))[0][2:]
                    player_hp = (player_id_pos[1].split(">["))[1][4:-1]
                else:
                    player_pos = player_id_pos[0]
                    player_hp = "100"
                
                log_data = splitted_log[2][1:]
                hit_by_what = log_data
                location = ""
                weapon_used = ""
                #for string in check_list:
                #    # Check if the current string exists in the given string
                #    if string in line:
                #        print(splitted_log[3][1:].split()[1])
                #        print(splitted_log[3][1:])
                #        break  # Exit the loop as soon as a match is found
                if log_data.startswith("killed by"):
                    if log_data.startswith("killed by Player"):
                        hit_by_what = "Player"
                        #print(hit_by_what)
                        try:
                            weapon_used = splitted_log[3][1:].split()[1]
                        except Exception as e:
                            weapon_used = "Fist"
                    elif (log_data.startswith("killed by  with") or log_data.startswith("killed by TripwireTrap")):
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
                        try:
                            weapon_used = splitted_log[3][1:].split()[7]
                        except Exception as e:
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
        return None
    
    # Return the extracted information as a dictionary
    return {
        "time": time,
        "player_name": player_name,
        "player_id": player_id,
        "pos": player_pos,
        "alive": alive,
        "hp": player_hp,
        "hit_by": hit_by_what,
        "location": location,
        "weapon_used": weapon_used 
    }
def fill_statistics(statistic, file,fileName):
    last_player_line = []
    for log_line in file:
            
            logData = parse_log_line(log_line)
            
            
            if logData:
                # print(log_line)
                statistic.UpdatePlayerLoggedIn(logData['player_name'], logData['player_id'])
                if not logData['alive']: 
                    for entry in last_player_line:
                        if entry['id'] == logData['player_id']:
                            statistic.UpdatePlayerKilledBy(str(logData['hit_by']))
                            
                if logData['weapon_used'] != "":
                    statistic.UpdateGunMostUsed(logData['weapon_used'])
                           
                if logData['alive']:
                    add_or_update_entry(logData['player_id'],log_line, last_player_line)
                else:
                    remove_entry_by_id(logData['player_id'], last_player_line)
    #if not statistic.isEmpty():
    #    statistic.write_data()
    
def run():
    files_in_dir = os.listdir(log_dir)

    filtered_files = list(filter(filter_by_date, files_in_dir))


    statistic = Statistics()

    counter = 1
    # Create a ThreadPoolExecutor with max_workers set to the number of files you want to process concurrently
    with tqdm(total=len(filtered_files), unit='files') as bar:
        with futures.ProcessPoolExecutor() as pool:
            # Add every asset to a thread pool for processing
            fut = [pool.submit(read_file,statistic, file_name) for file_name in filtered_files]
            for r in futures.as_completed(fut):
                bar.update(counter)

    print("handled " + str(len(filtered_files)) + " logsFiles")
    #print(result)
           

