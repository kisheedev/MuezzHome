import time
import logging
import traceback
import os
from datetime import datetime, timedelta

import pychromecast
import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

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
        self.driver = None
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

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Exécuter Chromium en mode headless
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Initialiser le WebDriver pour Chromium
        s = Service('/usr/bin/chromedriver')
        self.driver = webdriver.Chrome(options=chrome_options, service=s)

    def get_prayer_times(self, url, max_retries=5, delay=5):
        self.setup_driver()
        for attempt in range(max_retries):
            try:
                self.driver.get(url)
                time.sleep(10)  # Attendre que le contenu soit chargé

                prayer_times = {}
                try:
                    div_list = self.driver.find_elements(By.XPATH,
                                                        "//div[contains(@class, 'prayers')]//div[contains(@class, "
                                                        "'time')]//div")
                    # Exemple de récupération des horaires de prière avec des sélecteurs appropriés
                    prayer_times['Fajr'] = div_list[0].text
                    prayer_times['Dhuhr'] = div_list[1].text
                    prayer_times['Asr'] = div_list[2].text
                    prayer_times['Maghrib'] = div_list[3].text
                    prayer_times['Isha'] = div_list[4].text
                    return prayer_times
                except Exception as e:
                    logger.error(f"Erreur lors de la récupération des horaires de prière: {e}")
                    raise e
            except Exception as e:
                logger.error(f"Tentative {attempt + 1} échouée : {e}")
                time.sleep(delay)
		
        raise Exception(f"Échec de la récupération des horaires de prière après {max_retries} tentatives.")

    def get_next_prayer(self, prayer_times):
        current_time = datetime.now()
        next_prayer = None
        min_difference = timedelta(days=1)  # Initialise à un grand intervalle

        for prayer, time_str in prayer_times.items():
            prayer_time = datetime.strptime(time_str, '%H:%M').replace(year=current_time.year, month=current_time.month,
                                                                       day=current_time.day)
            if current_time < prayer_time:
                time_difference = prayer_time - current_time
                if time_difference < min_difference:
                    min_difference = time_difference
                    next_prayer = (prayer, prayer_time)

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
                logger.error(f"Tentative {attempt + 1} échouée : {e}")
                time.sleep(delay)
        raise Exception(f"Échec de la lecture de l'adhan après {max_retries} tentatives.")
    
    def run(self):
        self.read_config()
        need_to_update = True
        wait_next_day = False
        prayer_times = {}
        while True:
            # Récupération des horaires de prière
            try:
                if need_to_update is True:
                    if wait_next_day is True:
                        # Wait until next day + 10 min
                        now = datetime.now()
                        next_day = (now + timedelta(days=1)).replace(hour=0, minute=10, second=0, microsecond=0)
                        time_to_wait = (next_day - now).total_seconds()
                        logger.info(f"Waiting for {time_to_wait} seconds until the next day.")
                        time.sleep(time_to_wait)
                    prayer_times = self.get_prayer_times(self.mawaqit_url)
                    self.driver.quit()
                    logger.info(prayer_times)
                    need_to_update = False
                    wait_next_day = False
                
                # Détermination de la prochaine prière
                next_prayer = self.get_next_prayer(prayer_times)
                logger.info(f"Prochaine prière: {next_prayer[0]} à {next_prayer[1].strftime('%H:%M')}")
                # Si c'est la derniere prière de la journee, on reactualisera les horraires la prochaine fois:
                if next_prayer[0] == "Isha":
                    need_to_update = True
                    wait_next_day = True

                # Calcul du délai avant la prochaine prière
                delay = (next_prayer[1] - datetime.now()).total_seconds()

                # Attendre jusqu'à l'heure de la prière
                time.sleep(delay)

                # Jouer l'adhan
                self.play_adhan_on_google_home(next_prayer[0])

            except Exception as e:
                logger.error(f"Erreur lors de l'exécution: {e}")
                logger.error(traceback.format_exc())
                need_to_update = True

if __name__ == '__main__':
    try:
        logger.info(f"Script exécuté à {datetime.now()}")
        bot = AzanBot()
        bot.run()
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation: {e}")
        logger.error(traceback.format_exc())
