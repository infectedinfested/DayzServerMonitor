import sched
import time
from datetime import datetime, timedelta
from threading import Thread

def daily_task():
    print("Executing daily task at 4 AM...")


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