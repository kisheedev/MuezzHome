# MuezzHome

MuezzHome is a Python script that uses Selenium to fetch prayer times from your mosque on Mawaqit website and plays the Adhan on your Google Home device.

## Features

- Fetches prayer times from mawaqit website.
- Plays the Adhan on a Google Home device at each prayer time.
- Supports customization for adhan audio. Fajr audio can be different too
- Supports volume customization for each prayer.
- Designed to run on a Raspberry Pi.

## Prerequisites

- Python 3
- Raspberry Pi
- Google Home device configured and accessible from the network

## Running on a Raspberry Pi

### Installation
```bash
cd ~/Desktop
git clone https://github.com/kisheedev/MuezzHome.git
cd ~/Desktop/MuezzHome
```
Install the dependencies:

```bash
pip install -r requirements.txt
```

### Usage

Run the script with:
```bash
python script.py
```
### Set Up as a Cronjob

To run the script at startup on your Raspberry Pi, set it up as a cronjob:

1. Open the crontab file for the current user:
```bash
crontab -e
```
2. Add the following line at the end of the crontab file to run the script at startup (Make sure to replace /home/pi/MuezzHome/ with the correct path to your script.py script):
```bash
@reboot /usr/bin/python ~/Desktop/MuezzHome/script.py 
```
3. Save and exit the editor.

### Verify the Cronjob

To verify that the cronjob has been added correctly, you can list the cron jobs with the following command:
```bash
crontab -l
```
You should see the line you added to run the script at startup.
Clone the repository and navigate to the directory:


## Configuration

Copy the config.yaml file edit it with your own values:

Here is an example configuration:

```yaml
mawaqit_url: "URL_OF_THE_MAQAQUIT_SITE"
google_home_name: "Google_Home_Name"
adhan_url: "ADHAN_URL"
fajr_adhan_url: "FAJR_ADHAN_URL"
volumes:
  - prayer_name: "Fajr"
    volume: 50
  - prayer_name: "Dhuhr"
    volume: 50
  - prayer_name: "Asr"
    volume: 50
  - prayer_name: "Maghrib"
    volume: 50
  - prayer_name: "Isha"
    volume: 50
```
### Configuration Details

* `mawaqit_url`: The URL of the Mawaqit site where prayer times can be fetched.
* `google_home_name`: The name of your Google Home device as it appears in the Google Home app.
* `adhan_url`: The URL of the Adhan audio file to be played.
* `fajr_adhan_url`: The URL of the Fajr Adhan audio file to be played (optional).
* `volumes`: A list of dictionaries specifying the volume levels for each prayer. Each dictionary should have:
   * `prayer_name`: The name of the prayer (e.g., “Fajr”, “Dhuhr”).
   * `volume`: The volume level (0-100).

## Test Scripts
`test/test_mawaqit.py`
This script tests the functionality of fetching prayer times from the specified URL.
```bash 
python test_mawaqit.py
```

`test/test_google_home.py`
This script tests the functionality of playing the Adhan on the Google Home device.
```bash 
python test_google_home.py
```


## Contributing

If you would like to contribute, please open an issue or submit a pull request.
