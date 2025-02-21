from datetime import datetime
import time

def wait_for_next_prayer(next_prayer):
    # Check every minute if it's time for next prayer
    # When prayer is in less than a minute, check every seconds
    sleepInSec = 60
    while(True):
        delta = int((next_prayer - datetime.now()).total_seconds())
        print(delta)
        if delta <= 0:
            break
        elif delta <=60:
            sleepInSec = 1
        else:
            sleepInSec = 60
        time.sleep(sleepInSec)

wait_for_next_prayer(datetime(2025, 2, 21, 20, 40))
print(datetime.now())
