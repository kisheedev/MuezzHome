import time
import logging
import traceback
import os
import pycurl
import re
import json
from io import BytesIO
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import pychromecast
import yaml


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logFormatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s", datefmt='%Y-%m-%d %H:%M:%S')

fileHandler = logging.FileHandler("{0}/{1}.log".format('/home/pi/Desktop/Azan', 'azan_bot'))
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

class AzanBot:
    def __init__(self):
        self.mawaqit_url = None
        self.google_home_name = None
        self.adhan_url = None
        self.fajr_adhan_url = None
        self.volumes = None

    def read_config(self):
        # Get the absolute path of the current working directory
        path, filename = os.path.split(__file__)
        # Combine the current directory path with the filename
        file_path = os.path.join(path, 'config.yaml')
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            self.mawaqit_url = data["mawaqit_url"]
            self.google_home_name = data["google_home_name"]
            self.adhan_url = data["adhan_url"]
            self.fajr_adhan_url = data["fajr_adhan_url"]
            self.volumes = data["volumes"]

    def get_calendar(self, url, max_retries=5, delay=5):
        for attempt in range(max_retries):
            try:
                # Create buffer to store HTTP response
                buffer = BytesIO()
                custom_headers = ['User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0/8mqLkJuL-86']

                # Init pycurl
                c = pycurl.Curl()
                c.setopt(c.URL, url)
                c.setopt(c.WRITEFUNCTION, buffer.write)
                c.setopt(c.FOLLOWLOCATION, True)  # Suivre les redirections
                c.setopt(c.HTTPHEADER, custom_headers)
                c.perform()
                c.close()
                
                # Extract response content
                html_content = buffer.getvalue().decode('utf-8')

                soup = BeautifulSoup(html_content, 'html.parser')

                # Search script balise containing var confData
                script_tag = soup.find("script", string=re.compile("var confData ="))
                if script_tag:
                    # Extract script text
                    script_text = script_tag.string

                    # Extract JSON object with regex
                    match = re.search(r"var confData = (\{.*?\});", script_text, re.DOTALL)
                    if match:
                        conf_data_json = match.group(1)  # Extraire l'objet JSON en texte
                        conf_data = json.loads(conf_data_json)  # Convertir en dictionnaire Python

                        # Extract calendar
                        calendar = conf_data.get("calendar", [])
                        return calendar
                    else:
                        raise Exception("var confData nnot found in the script.")
                else:
                    raise Exception("Script balise containing 'confData' not found.")
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed : {e}")
                time.sleep(delay)
		
        raise Exception(f"Error while getting prayer times after {max_retries} attempt.")

    def get_prayer_times(self, calendar):
        current_time = datetime.now()
        res = calendar[current_time.month - 1][str(current_time.day)]
        prayer_times = {}
                
        # Extract prayer times in order : Fajr, Dhuhr, Asr, Maghrib, Isha
        if len(res) >= 5:
            prayer_times['Fajr'] = res[0]
            #prayer_times['Chourouk'] = res[1]
            prayer_times['Dhuhr'] = res[2]
            prayer_times['Asr'] = res[3]
            prayer_times['Maghrib'] = res[4]
            prayer_times['Isha'] = res[5]

        logger.info(prayer_times)
        return prayer_times
        

    def format_seconds(self, sec):
        td = timedelta(seconds=sec)
        return ", ".join(f"{v} {u}" for v, u in 
                         [(td.days, "days"), 
                          (td.seconds // 3600, "hours"), 
                          (td.seconds % 3600 // 60, "minutes"), 
                          (td.seconds % 60, "seconds")] if v)
                      
    def get_next_prayer(self, prayer_times):
        current_time = datetime.now()
        next_prayer = None
        min_difference = timedelta(days=1) 
        while next_prayer is None:
            for prayer, time_str in prayer_times.items():
                prayer_time = datetime.strptime(time_str, '%H:%M').replace(year=current_time.year, month=current_time.month,
                                                                           day=current_time.day)
                if current_time < prayer_time:
                    time_difference = prayer_time - current_time
                    if time_difference < min_difference:
                        min_difference = time_difference
                        next_prayer = (prayer, prayer_time)
            if next_prayer is None:
                isha_datetime = datetime.strptime(prayer_times['Isha'], '%H:%M')
                if(isha_datetime - datetime.now()).total_seconds() < 0:
                    logger.info("No more prayer for today...")
                    return "NoMore", 0
                else:
                    logger.error("next_prayer is None, will retry in 1min")
                    time.sleep(60)
        
        logger.info(f"Next prayer: {next_prayer[0]} time: {next_prayer[1].strftime('%H:%M')}")
        return next_prayer

    def play_adhan_on_google_home(self, prayer_name, max_retries=5, delay=5):
        for attempt in range(max_retries):
            try:
                chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[self.google_home_name])
                if not chromecasts:
                    logger.error(f"No chromecast with name '{self.google_home_name}' found.")
                    raise Exception(f"ChromeCast not found")
                else:
                    cast = chromecasts[0]
                    cast.wait()
                    # adjust volume
                    volume = next(x['volume'] for x in self.volumes if x['prayer_name'] == prayer_name)
                    logger.info(f"volume set to {volume}%")
                    cast.set_volume(volume / 100)
                    mc = cast.media_controller
                    adhan_url = self.adhan_url
                    if prayer_name == 'Fajr' and self.fajr_adhan_url is not None:
                        adhan_url = self.fajr_adhan_url
                    mc.play_media(adhan_url, 'audio/mp3')
                    mc.block_until_active()
                    time.sleep(5)
                    if(mc.status.player_is_playing):
                        logger.info(f"Adhan for {prayer_name} played on {self.google_home_name}")
                        return
                    else:
                        raise Exception("Adhan not played, retry...")
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed : {e}")
                time.sleep(delay)
        raise Exception(f"Adhan play failed, maximum attempt reached : {max_retries}.")
    
    def wait_for_next_prayer(self, next_prayer):
        # Check every minute if it's time for next prayer
        # When prayer is in less than a minute, check every seconds
        sleepInSec = 60
        while(True):
            delta = int((next_prayer - datetime.now()).total_seconds())
            if delta <= 0:
                break
            elif delta <=60:
                sleepInSec = 1
            else:
                sleepInSec = 60
            time.sleep(sleepInSec)
                
    def run(self):
        self.read_config()
        prayer_times = {}
        need_to_update = True
        wait_next_day = False
        calendar = self.get_calendar(self.mawaqit_url)
        while True:
            try:
                if need_to_update is True:
                    if wait_next_day is True:
                        # Wait until next day + 10 min
                        now = datetime.now()
                        next_day = (now + timedelta(days=1)).replace(hour=0, minute=10, second=0, microsecond=0)
                        time_to_wait = (next_day - now).total_seconds()
                        logger.info(f"Time to wait until the next day : {self.format_seconds(time_to_wait)}")
                        time.sleep(time_to_wait)
                        wait_next_day = False
                    # Get prayer times from calendar
                    prayer_times = self.get_prayer_times(calendar)
                    need_to_update = False
                
                # Détermination de la prochaine prière
                next_prayer = self.get_next_prayer(prayer_times)

                # If it's last prayer of the day, we will wait until next day to refresh prayer times
                if next_prayer[0] == "Isha" or next_prayer[0] == "NoMore" :
                    need_to_update = True
                    wait_next_day = True
                
                if next_prayer[0] != "NoMore":
                    # Compute wait time and wait until next prayer
                    self.wait_for_next_prayer(next_prayer[1])

                    # Play Adhan
                    self.play_adhan_on_google_home(next_prayer[0])

            except Exception as e:
                logger.error(f"Execution error: {e}")
                logger.error(traceback.format_exc())

if __name__ == '__main__':
    try:
        logger.info(f"Script run at {datetime.now()}")
        bot = AzanBot()
        bot.run()
    except Exception as e:
        logger.error(f"Init error: {e}")
        logger.error(traceback.format_exc())
