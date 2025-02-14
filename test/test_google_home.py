import pychromecast, time

google_home_name = 'Google Home mini'
chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[google_home_name])
if not chromecasts:
    print(f"No chromecast with name '{google_home_name}' found.")
    exit()
cast = chromecasts[0]
cast.wait()
cast.set_volume(0.1)
mc = cast.media_controller
mc.play_media('http://91.167.152.138:32481/share/Xm9QULyw4FTl5lL_/adhan%20makkah.mp3', 'audio/mp3')
mc.block_until_active()
time.sleep(5)
print(mc.status)
if(mc.status.player_is_playing):
    print(f"Adhan played on {google_home_name}")
else:
    print("ERROR")
