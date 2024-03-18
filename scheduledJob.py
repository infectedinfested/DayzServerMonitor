import sched
import time

from threading import Thread

import sys
sys.path.insert(1, 'flows')
import ban_flow 
import dayzStatistics

from datetime import datetime, timedelta






def daily_task():
    print("Executing daily task at 4 AM...")
    ban_flow.unban()
    dayzStatistics.run()
    # dayzStatistics.getloginReport()


def calculate_delay():
    now = datetime.now()
    next_4_am = datetime(now.year, now.month, now.day, 21, 16, 0) + timedelta(days=1)
    print(next_4_am)
    print(now)
    delay = (next_4_am - now).total_seconds()
    print(delay)
    return delay

# Function to run the scheduler in a separate thread
def run_scheduler():
    scheduler = sched.scheduler(time.time, time.sleep)
    delay = calculate_delay()
    scheduler.enter(delay, 1, daily_task)
    scheduler.run()

if __name__ == "__main__":
    run_scheduler()