from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time


def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Exécuter Chromium en mode headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialiser le WebDriver pour Chromium
    s = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(options=chrome_options, service=s)
    return driver



################### 1st CALL ##################
driver = setup_driver()
url = "https://mawaqit.net/fr/mosquee-ennour-sartrouville"
driver.get(url)
time.sleep(5)  # Attendre que le contenu soit chargé
prayer_times = {}
div_list = driver.find_elements(By.XPATH,"//div[contains(@class, 'prayers')]//div[contains(@class, 'time')]//div")
# Exemple de récupération des horaires de prière avec des sélecteurs appropriés
prayer_times['Fajr'] = div_list[0].text
prayer_times['Dhuhr'] = div_list[1].text
prayer_times['Asr'] = div_list[2].text
prayer_times['Maghrib'] = div_list[3].text
prayer_times['Isha'] = div_list[4].text
print(prayer_times)
driver.quit()		
###############################################




#################### 2nd CALL #################
driver = setup_driver()
url = "https://mawaqit.net/fr/mosquee-khalid-ibn-al-walid-marseille"
driver.get(url)
time.sleep(5)  # Attendre que le contenu soit chargé
prayer_times = {}
div_list = driver.find_elements(By.XPATH,"//div[contains(@class, 'prayers')]//div[contains(@class, 'time')]//div")
# Exemple de récupération des horaires de prière avec des sélecteurs appropriés
prayer_times['Fajr'] = div_list[0].text
prayer_times['Dhuhr'] = div_list[1].text
prayer_times['Asr'] = div_list[2].text
prayer_times['Maghrib'] = div_list[3].text
prayer_times['Isha'] = div_list[4].text
print(prayer_times)
driver.quit()	
################################################