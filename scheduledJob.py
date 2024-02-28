from flask import Flask, request
import sched
import time
import csv

from datetime import datetime, timedelta
from threading import Thread


from  classes import BannedPerson

from common import strtobool, create_ban_file



def unban():
    rows = []
    bannedPersons = []
    with open('DayZServerBackup20220728/ban.csv', 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            rows.append(row)
    
    for row in rows:
        try:
            unban_date = datetime.strptime(row['startDate'], "%d-%m-%Y") + get_timeDelta(row['time'])
            if (unban_date <= datetime.now() and row['active']=="True"):
                row['active'] = "False"
                row.update(row)
                print("unbanning; id:"+ str(row['uniqueid']) + " steamid: "+ str(row['steamid']))
        except Exception as e:
            e = None


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
    

    return None


def get_timeDelta(amount):
    match amount:
        case "1d": return timedelta(days=1)
        case "2d": return timedelta(days=2)
        case "3d": return timedelta(days=3)
        case "4d": return timedelta(days=4)
        case "1w": return timedelta(weeks=1)
        case "2w": return timedelta(weeks=2)
        case "3w": return timedelta(weeks=3)
        case "1m": return timedelta(days=30)
        case "2m": return timedelta(days=60)
        case "3m": return timedelta(days=90)
        case "6m": return timedelta(days=182)
        case "1y": return timedelta(days=365)
        case _: return timedelta(days=36500)












def daily_task():
    print("Executing daily task at 4 AM...")
    unban()

def calculate_delay():
    now = datetime.now()
    next_4_am = datetime(now.year, now.month, now.day, 4, 0, 0) + timedelta(days=1)
    delay = (next_4_am - now).total_seconds()
    return delay

# Function to run the scheduler in a separate thread
def run_scheduler():
    scheduler = sched.scheduler(time.time, time.sleep)
    delay = calculate_delay()
    scheduler.enter(delay, 1, daily_task)
    scheduler.run()

if __name__ == "__main__":
    run_scheduler()