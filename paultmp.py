
from playsound import playsound
import cv2 as cv
import time
from ppadb.client import Client
from PIL import Image
import numpy as np

# INIT
# updated by functions
health_st = 100
health_ar = 100
health_sh = 100
ModuleList = []
start_farm_time = time.time()
last_farm_site = 0
last_inventory_value = 0
interrupted_farming = 0

module_icon_radius = 30
color_white = [255, 255, 255, 255]
outer_autopilot_green = [46, 101, 122, 255]
inner_autopilot_green = [155, 166, 158, 255]
undock_yellow = [174, 147, 40, 255]
# to be changed by user / fixed
task = 'combat'
start = 'from_station'
preferredOrbit = 29
planet = 0
repeat = 0
mining_time = 0
device_nr = 1
name = ''
home = 0
bait = 0
time_stamp_farming = time.time()

# connect to Bluestacks
adb = Client(host='127.0.0.1', port=5037)
devices = adb.devices()
if len(devices) < device_nr + 1:
    print('no device attached')
    quit()
# CS = current Screenshot
print(devices)
device = devices[device_nr]
CS = device.screencap()
with open('screen.png', 'wb') as f:
    f.write(CS)
CS_cv = cv.imread('screen.png')
CS_image = Image.open('screen.png')
CS_image = np.array(CS_image, dtype=np.uint8)

def read_config_file():
    file = open('config.txt')
    tmp = file.readline()
    while tmp != '':
        tmp = str(tmp).split()
        if tmp[0] == 'planet':
            global planet
            planet = int(tmp[1])
        if tmp[0] == 'home':
            global home
            home = int(tmp[1])
        if tmp[0] == 'repeat':
            global repeat
            repeat = int(tmp[1])
        if tmp[0] == 'mining_time':
            global mining_time
            mining_time = int(tmp[1])
        if tmp[0] == 'device':
            global device_nr
            device_nr = int(tmp[1])
        if tmp[0] == 'name':
            global name
            name = tmp[1]
        if tmp[0] == 'bait':
            global bait
            bait = tmp[1]
        tmp = file.readline()
def update_cs():
    global CS_cv, CS, CS_image
    CS = device.screencap()
    with open('screen.png', 'wb') as g:
        g.write(CS)
    CS_cv = cv.imread('screen.png')
    CS_image = Image.open('screen.png')
    CS_image = np.array(CS_image, dtype=np.uint8)

def get_player_thread():
    x, y, w, h = 1547, 86, 18, 445
    as_icon = cv.imread('assets\\all_ships_icon.png')
    crop_img = CS_cv[y:y + h, x:x + w]
    result = cv.matchTemplate(crop_img, as_icon, cv.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    print(max_val)
    if max_val > 0.99:
        return 1
    return 0

def main():
    update_cs()
    if get_player_thread():
        playsound('assets\\sounds\\bell.wav')
        quit()
    time.sleep(5)
    main()

main()
