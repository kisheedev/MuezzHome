import pycurl
import re
import json
from io import BytesIO
from bs4 import BeautifulSoup


def get_prayer_times(url):
    # Créer un buffer pour stocker la réponse HTTP
    buffer = BytesIO()
    custom_headers = ['User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0/8mqLkJuL-86']

    # Initialiser pycurl
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.setopt(c.FOLLOWLOCATION, True)  # Suivre les redirections
    c.setopt(c.HTTPHEADER, custom_headers)
    c.perform()
    c.close()
    
    # Extraire le contenu de la réponse
    html_content = buffer.getvalue().decode('utf-8')

    # Utiliser BeautifulSoup pour analyser le HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Initialiser un dictionnaire pour stocker les horaires de prière
    prayer_times = {}

    # Exemple d'extraction des horaires (à adapter selon la structure du site)
    try:
        # Trouver le script contenant confData
        script_tag = soup.find("script", string=re.compile("let confData ="))
        if script_tag:
            # Extraire le texte du script
            script_text = script_tag.string

            # Extraire l'objet JSON avec regex
            match = re.search(r"let confData = (\{.*?\});", script_text, re.DOTALL)
            if match:
                conf_data_json = match.group(1)  # Extraire l'objet JSON en texte
                conf_data = json.loads(conf_data_json)  # Convertir en dictionnaire Python

                # Extraire les times
                res = conf_data.get("times", [])

            else:
                print("confData non trouvé dans le script.")
        else:
            print("Script contenant confData non trouvé.")
        # Extraire les horaires dans l'ordre Fajr, Dhuhr, Asr, Maghrib, Isha
        if len(res) >= 5:
            prayer_times['Fajr'] = res[0]
            prayer_times['Dhuhr'] = res[1]
            prayer_times['Asr'] = res[2]
            prayer_times['Maghrib'] = res[3]
            prayer_times['Isha'] = res[4]

        return prayer_times
    except Exception as e:
        print(f"Erreur lors de l'extraction des horaires : {e}")
        return None


################### 1er appel ##################
url_1 = "https://mawaqit.net/fr/mosquee-ennour-sartrouville"
prayer_times_1 = get_prayer_times(url_1)
if prayer_times_1:
    print("Horaires de prière pour la Mosquée Ennour Sartrouville:")
    print(prayer_times_1)
else:
    print("Erreur lors de la récupération des horaires pour la Mosquée Ennour Sartrouville.")
#################################################

################### 2ème appel ##################
url_2 = "https://mawaqit.net/fr/mosquee-khalid-ibn-al-walid-marseille"
prayer_times_2 = get_prayer_times(url_2)
if prayer_times_2:
    print("Horaires de prière pour la Mosquée Khalid Ibn Al-Walid Marseille:")
    print(prayer_times_2)
else:
    print("Erreur lors de la récupération des horaires pour la Mosquée Khalid Ibn Al-Walid Marseille.")
#################################################
