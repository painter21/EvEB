import datetime
import subprocess
import time

from playsound import playsound

file = open('E:\Eve_Echoes\Bot\_Bronson\\to_observe.txt')
bronson_tmp = file.readline()
file.close()

file = open('E:\Eve_Echoes\Bot\_Kort\\to_observe.txt')
kort_tmp = file.readline()
file.close()

bronson_active = 1
kort_active = 1

while 1:
    time.sleep(120)

    file = open('E:\Eve_Echoes\Bot\_Bronson\\to_observe.txt')
    bronson_tmp2 = file.readline()
    file.close()

    file = open('E:\Eve_Echoes\Bot\_Kort\\to_observe.txt')
    kort_tmp2 = file.readline()
    file.close()

    if kort_tmp == kort_tmp2 and kort_active:
        subprocess.call(
            ["D:\Program Files\AutoHotkey\AutoHotkey.exe", "E:\\Eve_Echoes\\Bot\\ahk_scripts\\close_kort.ahk"])
        playsound('E:\Eve_Echoes\Bot\EveB\\assets\sounds\\bell.wav')
        kort_active = 0

    if bronson_tmp == bronson_tmp2 and bronson_active:
        subprocess.call(
            ["D:\Program Files\AutoHotkey\AutoHotkey.exe", "E:\\Eve_Echoes\\Bot\\ahk_scripts\\close_kort.ahk"])
        playsound('E:\Eve_Echoes\Bot\EveB\\assets\sounds\\bell.wav')
        bronson_active = 0

    print(str(datetime.datetime.utcnow() + datetime.timedelta(hours=2)), 'bronson: ', bronson_active, 'kort: ', kort_active)

    if not bronson_active and not kort_active:
        quit()

    bronson_tmp = bronson_tmp2
    kort_tmp = kort_tmp2

