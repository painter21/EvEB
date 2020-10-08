# only works on 960x540
import re
import subprocess
from ppadb.client import Client
import time
import numpy as np
import cv2 as cv
import pytesseract as tess
from numpy import random
from PIL import Image
from playsound import playsound
import os
import datetime

tess.pytesseract.tesseract_cmd = 'E:\\Eve_Echoes\\Bot\Programs\\Tesseract-OCR\\tesseract.exe'
def read_config_file_uni():
    print('update config')
    file = open(path + 'config.txt')
    tmp = file.readline()
    while tmp != '':
        tmp = str(tmp).split()
        if tmp[0] == 'planet':
            global planet
            planet = int(tmp[1])
        if tmp[0] == 'random_warp':
            global random_warp
            random_warp = int(tmp[1])
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
            bait = int(tmp[1])
        if tmp[0] == 'start':
            global start
            start = tmp[1]
        tmp = file.readline()

# INIT GLOBAL VALUES
if 1:
    # updated by functions
    health_st_list, health_ar_list, health_sh_list = [], [], []
    health_st = 100
    health_ar = 100
    health_sh = 100
    ModuleList = []
    start_farm_time = time.time()
    last_farm_site = 0
    last_inventory_value = 0
    interrupted_farming = 0
    eco_mode = 0

    module_icon_radius = 28
    color_white = [255, 255, 255, 255]
    outer_autopilot_green = [46, 101, 122, 255]
    inner_autopilot_green = [155, 166, 158, 255]
    undock_yellow = [174, 147, 40, 255]

    # to be changed by user / fixed
    path = ''
    path_to_script = ''
    start = 'main'
    preferredOrbit = 29
    planet = 0
    repeat = 0
    mining_time = 0
    device_nr = 1
    name = ''
    home = 0
    bait = 0
    random_warp = 1
    time_stamp_farming = time.time()
    # connect to Bluestacks
    Adb = Client(host='127.0.0.1', port=5037)
    Devices = Adb.devices()
    if len(Devices) < 1:
        print('no device attached')
        quit()
    # CS = current Screenshot
    Device = Devices[0]
    with open(path + 'screen.png', 'wb') as f:
        f.write(Device.screencap())
    CS_cv = cv.imread('screen.png')
    CS_image = Image.open('screen.png')
    CS_image = np.array(CS_image, dtype=np.uint8)

# GETTERS
def get_module_list():
    return ModuleList
def get_eco_mode():
    return eco_mode
def get_planet():
    return planet
def get_cs_cv():
    return CS_cv
def get_name():
    return name
def get_bait():
    return bait
def get_random_warp():
    return random_warp
def get_repeat():
    return repeat
def test_main():
    main()
def get_start():
    return start
def set_path(pa):
    global path
    path = pa
def set_path_to_script(pa):
    global path_to_script
    path_to_script = pa

# BASIC FUNCTIONS
def config_uni_helper():
    
def config_uni():
    read_config_file_uni()
    global CS_cv, CS_image, Device
    # connect to Bluestacks
    if len(Devices) < device_nr + 1:
        print('no device attached')
        quit()
    # CS = current Screenshot
    print(Devices)
    Device = Devices[device_nr]
    cs = Device.screencap()
    with open(path + 'screen.png', 'wb') as f:
        f.write(cs)
    CS_cv = cv.imread(path + 'screen.png')
    CS_image = Image.open(path + 'screen.png')
    CS_image = np.array(CS_image, dtype=np.uint8)
def main():
    print('restart wont be overwritten')
def power_nap():
    time.sleep(np.random.default_rng().random() * 0.3 + 0.5)
def device_update_cs():
    global CS_cv, CS, CS_image
    CS = Device.screencap()
    with open(path + 'screen.png', 'wb') as g:
        g.write(CS)
    CS_cv = cv.imread(path + 'screen.png')
    CS_image = Image.open(path + 'screen.png')
    CS_image = np.array(CS_image, dtype=np.uint8)
def compare_colors(a, b):
    fir = abs(int(a[0]) - int(b[0]))
    sec = abs(int(a[1]) - int(b[1]))
    thi = abs(int(a[2]) - int(b[2]))
    fou = abs(int(a[3]) - int(b[3]))
    return (fir + sec + thi + fou) / 10
def get_point_in_circle(x, y, r):
    a = 3.  # shape
    angle = np.random.default_rng().random() * np.pi
    r = r - np.random.default_rng().power(a) * r
    return np.cos(angle) * r + x, np.sin(angle) * r + y

def device_click_circle(x, y, r):
    tmp = get_point_in_circle(x, y, r)
    Device.shell(f'input touchscreen tap {tmp[0]} {tmp[1]}')
    power_nap()

    # great display:
    # https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.power.html#numpy.random.Generator.power
def device_click_rectangle(x, y, w, h):
    x = w * np.random.default_rng().random() + x
    y = h * np.random.default_rng().random() + y
    Device.shell(f'input touchscreen tap {x} {y}')
    power_nap()
def device_swipe_from_circle(x, y, r, d, direction):
    tmp = get_point_in_circle(x, y, r)
    x, y = tmp[0], tmp[1]
    if d == 0:
        Device.shell(f'input touchscreen tap {x} {y}')
        return

    # random direction: 0- random, 1 is down, 2 is ?, 3 is up, 4 is up

    if direction > 0:
        angle = np.pi / 2 * direction
    else:
        angle = np.random.default_rng().random() * np.pi * 1.5
    r = 130 + d * 2.4

    Device.shell(f'input touchscreen swipe {x} {y} {np.cos(angle) * r + x} {np.sin(angle) * r + y} 1000')
    power_nap()
def device_toggle_eco_mode():
    global eco_mode
    eco_mode = 1 - eco_mode
    subprocess.call(["D:\Program Files\AutoHotkey\AutoHotkey.exe", "E:\\Eve_Echoes\\Bot\\ahk_scripts\\toggle_eco_" + name + ".ahk"])

def image_remove_dark(image, border):
    # remove darker pixels
    row_count = -1
    for row in image:
        row_count += 1
        pixel_count = -1
        for pixel in row:
            pixel_count += 1
            brightness = 0
            for color in pixel:
                brightness += color
            if brightness < border:
                image[row_count][pixel_count] = [0, 0, 0]
    return image
def image_compare_text(image1, image2):
    # image2 muss kleiner oder im idealfall gleich groß wie image1 sein
    diff = 0
    count = 0
    row_count = -1
    for row in image1:
        row_count += 1
        pixel_count = -1
        for pixel in row:
            pixel_count += 1
            color_count = -1
            spot_brightness = 0
            for color in pixel:
                color_count += 1
                spot_brightness += color
            if spot_brightness > 300 and image2[row_count][pixel_count][0] < 100:
                diff += 1
            count += 1
    return int(diff*10000/count)
def image_get_blur_brightness(x, y):
    brightness = 0
    count = 0
    for x_off in range(3):
        x_new = x+x_off-1
        for y_off in range(3):
            y_new = y+y_off-1
            for color in CS_cv[y_new][x_new]:
                brightness += color
                count += 1
    return 100*brightness/count/255
def save_screenshot():
    import random
    import string
    file_name = ''.join(random.choice(string.ascii_lowercase) for i in range(6))
    with open(file_name + '.png', 'wb') as h:
        h.write(CS)

def add_rectangle(x, y, w, h):
    cv.rectangle(CS_cv, (x, y), (x + w, y + h),
                 color=(0, 255, 0), thickness=2, lineType=cv.LINE_4)
def show_image(image):
    if image == 0:
        cv.imshow('tmp', CS_cv)
    else:
        cv.imshow('tmp', image)
    cv.waitKey()


# INTERNAL HELPER FUNCTIONS
def update_modules():
    global ModuleList
    ModuleList = []
    print('path ')
    print(path_to_script + 'assets\\modules\\small\\_pos.txt')
    file = open(path_to_script + 'assets\\modules\\small\\_pos.txt')
    tmp = file.readline()
    while tmp != '':
        tmp = tmp.split()
        ar = cv.imread(path_to_script + 'assets\\modules\\small\\' + tmp[0] + '.png')
        result = cv.matchTemplate(CS_cv, ar, cv.TM_CCORR_NORMED)
        threshold = 0.95
        loc = np.where(result >= threshold)
        accepted_list = []
        for pt in zip(*loc[::-1]):
            continue_value = 1
            for point in accepted_list:
                if abs(pt[1] - point[1]) < 10 and abs(pt[0] - point[0]) < 10:
                    continue_value = 0
            if continue_value == 1:
                accepted_list.append(pt)
                center = (pt[0] + int(tmp[2]), pt[1] + int(tmp[3]))
                ModuleList.append([tmp[0], tmp[1], center[0], center[1]])
                # cv.circle(CS_cv, center, module_icon_radius, color=(0, 255, 0), thickness=2, lineType=cv.LINE_4)
        tmp = file.readline()
    # cv.imshow('tmp', CS_cv)
    # cv.waitKey()
    print(str(len(ModuleList)) + ' Modules found')
    print(ModuleList)
def get_speed():
    tmp = 0
    stop = 0
    precision = 10
    factor_y = 0.67
    center_x = 480
    center_y = 470
    r = 50
    while tmp < precision and not stop:
        angle = np.pi * (0.65 - 0.32 * tmp / precision)
        x = int(center_x + np.cos(angle) * r)
        y = int(center_y + np.sin(angle) * r * factor_y)
        # cv.rectangle(CS_cv, (x, y), (x, y), color=(tmp*10, 255, 0), thickness=2, lineType=cv.LINE_4)
        if CS_image[y][x][0] > 175:
            return int(tmp / precision * 100)
        tmp += 1
    # cv.imshow('image', CS_cv)
    # cv.waitKey(0)
    return 100
def get_cargo():
    steps = 20
    x, y, w = 3, 61, 85 / steps
    # 0.55 match, 0.69 no match
    old_color = CS_image[y][x]
    for i in range(steps):
        new_color = CS_image[y][int(x + (i * w))]
        # cv.rectangle(CS_cv, (int(x + (i * w)), y), (int(x + (i * w)), y), color=(0, 255, i * 10), thickness=3, lineType=cv.LINE_4)
        # print(compare_colors(new_color, old_color), new_color)
        if compare_colors(new_color, old_color) > 9:
            return 100 * i / steps
        old_color = new_color
    # cv.imshow('image', CS_cv)
    # cv.waitKey(0)
    # no contrast in there, have to work with colors:
    cargo_yellow = [100, 100, 72, 255]
    if compare_colors(CS_image[y][int(x + (steps * w))], cargo_yellow) < 13:
        return 100
    return 0
def get_autopilot():
    x_a, y_a, x_b, y_b = 43, 102, 43, 127
    # check if autopilot is online (2 pixels because safety)
    if compare_colors(CS_image[y_a][x_a], outer_autopilot_green) < 10 and \
            compare_colors(CS_image[y_b][x_b], outer_autopilot_green) < 10:
        return 1
    return 0
def get_autopilot_active():
    x_c, y_c = 26, 121
    if compare_colors(CS_image[y_c][x_c], inner_autopilot_green) < 13:
        return 1
    return 0
def get_is_capsule():
    tmp_module_list = []
    file = open(path_to_script + 'assets\\modules\\small\\_pos.txt')
    tmp = file.readline()
    while tmp != '':
        tmp = tmp.split()
        print(tmp)
        ar = cv.imread(path_to_script + 'assets\\modules\\small\\' + tmp[0] + '.png')
        result = cv.matchTemplate(CS_cv, ar, cv.TM_CCORR_NORMED)
        threshold = 0.95
        loc = np.where(result >= threshold)
        accepted_list = []
        for pt in zip(*loc[::-1]):
            continue_value = 1
            print(pt)
            for point in accepted_list:
                if abs(pt[1] - point[1]) < 10 and abs(pt[0] - point[0]) < 10:
                    continue_value = 0
            if continue_value == 1:
                accepted_list.append(pt)
                center = (pt[0] + int(tmp[2]), pt[1] + int(tmp[3]))
                tmp_module_list.append([tmp[0], tmp[1], center[0], center[1]])
                # cv.circle(CS_cv, center, module_icon_radius, color=(0, 255, 0), thickness=2, lineType=cv.LINE_4)
        tmp = file.readline()
    if len(tmp_module_list) == 0:
        return 1
    return 0
def get_is_in_station():
    # basically checking for the huge undock symbol
    x_a, y_a, x_b, y_b = 822, 174, 838, 174
    if compare_colors(CS_image[y_a][x_a], undock_yellow) < 8 and \
            compare_colors(CS_image[y_b][x_b], undock_yellow) < 8:
        return 1
    return 0
def get_filter_icon(filter_name):
    x, y, w, h = 932, 40, 5, 277
    crop_img = CS_cv[y:y + h, x:x + w]
    for icon_file in os.listdir(path_to_script + 'assets\\filter_icons\\'):
        if filter_name in icon_file:
            image2 = cv.imread(path_to_script + 'assets\\filter_icons\\' + icon_file)
            result = cv.matchTemplate(crop_img, image2, cv.TM_CCORR_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
            if max_val > 0.99:
                return max_loc[0] + x, max_loc[1] + y
    return 0
def get_filter_list_size():
    return random_warp
# todo: add option to check for more targets
def get_is_target():
    outer_x, outer_y, inner_x, inner_y, hp_x, hp_y = 631, 16, 671, 22, 656, 50
    # is something targeted?
    outer_brightness = image_get_blur_brightness(outer_x, outer_y)
    inner_brightness = image_get_blur_brightness(inner_x, inner_y)
    hp_brightness = image_get_blur_brightness(hp_x, hp_y)
    # print(outer_brightness, inner_brightness, hp_brightness - inner_brightness)
    if outer_brightness*9/12 > inner_brightness:
        if hp_brightness - inner_brightness > 16:
            return 1
    return 0
def get_module_is_active(module):
    activate_blue, activate_red = [206, 253, 240, 255], [194, 131, 129, 255]
    x, y = module[2] + 2, module[3] - module_icon_radius
    if compare_colors(CS_image[y][x], activate_blue) > 15:
        return 1
    return 0
def get_inventory_value_small_screen(is_open):
    x, y, w, h = 327, 492, 180, 26
    if is_open:
        # open inventory
        device_click_rectangle(5, 61, 83, 26)
        time.sleep(1.5)
        device_update_cs()
    crop_img = CS_cv[y:y + h, x:x + w]
    cv.imshow('.', crop_img)
    cv.waitKey()
    raw_text = tess.image_to_string(crop_img).strip()
    raw_text = re.sub('\D', '', raw_text)
    if is_open:
        # click on close
        device_click_circle(926, 30, 10)
    print('current inventory value: ', int(raw_text))
    return int(raw_text)
def interface_show_player():
    x, y, h, w = 66, 1, 87, 127
    crop_img = CS_cv[y:y + h, x:x + w]
    cv.imshow('tmp', crop_img)
    cv.waitKey()
def set_filter(string_in_name):
    # swaps to a filter containing the given string
    if activate_filter_window():
        time.sleep(1)
        time.sleep(1)
        device_update_cs()
        if activate_filter_window():
            time.sleep(1)
            device_update_cs()
    # Filter Header, use the cv.imshow to see if it fits
    x, y, w, h = 767, 7, 74, 30
    crop_img = CS_image[y:y + h, x:x + w]
    if string_in_name not in tess.image_to_string(crop_img):
        # TODO: improve
        device_click_rectangle(x, y, w, h)
        if string_in_name in 'Anomalies':
            device_click_rectangle(x, 118, w, h)
            return
        if string_in_name in 'PvE':
            device_click_rectangle(x, 206, w, h)
            return
        if string_in_name in 'esc':
            device_click_rectangle(731, 338, 180, 45)
            return
        if string_in_name in 'Mining':
            device_click_rectangle(731, 286, 180, 45)
            return
        else:
            print('todo swap filter')
        set_filter(string_in_name)
    # cv.imshow('.', crop_img)
    # cv.waitKey()


# INTERFACE HELPER FUNCTIONS
def wait_warp_and_set_home():
    if not get_autopilot():
        set_home()
    # does nothing until speed bar goes to 15%
    device_update_cs()
    if get_speed() > 15:
        wait_warp_and_set_home()
def wait_warp():
    # does nothing until speed bar goes to 15%
    device_update_cs()
    if get_speed() > 15:
        wait_warp()

def activate_autopilot():
    if get_autopilot():
        if not get_autopilot_active():
            device_click_circle(22, 116, 10)
            return
def activate_filter_window():
    x, y = 923, 302
    # match was about 0.22, no match was 0.64, match = need fix
    if compare_colors(CS_image[y][x], color_white) < 40:
        print('activate filter window')
        device_click_circle(x, y, 5)
        return 1
    return 0
def activate_module(module):
    activate_blue, activate_red = [206, 253, 240, 255], [194, 131, 129, 255]
    x, y = module[2] + 2, module[3] - module_icon_radius
    if compare_colors(CS_image[y][x], activate_blue) > 15 and compare_colors(CS_image[y][x], activate_red) > 15:
        device_click_circle(module[2], module[3], module_icon_radius)
        return 1
    return 0
def deactivate_module(module):
    activate_blue, activate_red = [206, 253, 240, 255], [194, 131, 129, 255]
    x, y = module[2] + 2, module[3] - module_icon_radius

    if compare_colors(CS_image[y][x], activate_blue) < 15:
        device_click_circle(module[2], module[3], module_icon_radius)


# PLAIN SCRIPTS
def dump_ore():
    # open inventory
    device_click_rectangle(5, 61, 83, 26)
    time.sleep(1.5)
    # venture cargo
    device_click_rectangle(18, 393, 173, 41)
    time.sleep(1.5)
    # select all
    device_click_rectangle(701, 458, 68, 60)
    time.sleep(1)
    # move to
    device_click_rectangle(21, 80, 145, 56)
    time.sleep(0.3)
    # item hangar
    device_click_rectangle(294, 96, 194, 54)
    time.sleep(5)
    # click on close
    device_click_circle(926, 30, 10)
    return 1
def set_home():
    # open inventory
    device_click_rectangle(5, 61, 83, 26)
    time.sleep(1.5)
    # click on assets
    device_click_rectangle(12, 493, 182, 36)
    time.sleep(2.5)
    # click on station
    device_click_rectangle(12, 101 + home * 80, 182, 70)
    time.sleep(2)
    # click on set des
    device_click_rectangle(525, 461, 71, 55)
    time.sleep(0.5)
    # click set des
    device_click_rectangle(138, 443, 185, 42)
    time.sleep(2)
    # click on close
    device_click_circle(925, 30, 15)
    time.sleep(1)
    device_click_circle(925, 30, 15)
def set_pi_planet_for_autopilot(target):
    # only works for pI location
    # click portrait
    device_click_circle(140, 45, 30)
    time.sleep(0.5)
    # planetary production
    device_click_rectangle(803, 562, 135, 135)
    time.sleep(1)
    # click planet
    off = 145
    device_click_rectangle(32, 205 + target * off, 211, 64)
    # click set des
    device_click_rectangle(1321, 767, 253, 81)
    # click on close
    device_click_circle(925, 30, 15)
    time.sleep(1)
    device_click_circle(925, 30, 15)

# TASKS
def wait_end_navigation(safety_time):
    print('wait for navigation')
    while 1:
        device_update_cs()
        if not get_autopilot():
            # for stargate warps
            time.sleep(10)
            device_update_cs()
            if not get_autopilot():
                time.sleep(10)
                device_update_cs()
                if not get_autopilot():
                    return 1
        time.sleep(safety_time)
def undock_and_modules():
    # set destination
    # set_system(planet)
    # wait until autopilot gone
    # wait_end_navigation(20)

    # clear popup
    if not get_is_in_station():
        device_click_circle(818, 87, 10)
        time.sleep(2)

    print('undocking')
    device_click_rectangle(817, 165, 111, 26)
    time.sleep(15)

    # sometimes the speed meter gets broken, redock to fix
    device_update_cs()
    speed_x, speed_y = 460, 495
    print('speed-o-meter value: ', get_cs_cv()[speed_y][speed_x][2])
    if get_cs_cv()[speed_y][speed_x][2] < 130:
        # re dock
        set_home()
        time.sleep(5)
        device_click_circle(22, 116, 10)
        time.sleep(25)
        undock_and_modules()
        return

    print('calibrating')
    # sometimes there is a sentry in the way, gotta wait for space target to vanish
    update_modules()
def warp_to(item_nr, should_set_home):
    set_filter('esc')
    time.sleep(2)
    print('warp to site')
    device_click_rectangle(742, 47 + 51 * item_nr, 158, 44)
    device_click_rectangle(543, 101 + 51 * item_nr, 174, 55)
    time.sleep(1)
    # fall back
    device_click_rectangle(742, 47, 158, 44)
    device_click_rectangle(543, 101, 174, 55)
    time.sleep(5)
    if should_set_home:
        wait_warp_and_set_home()
    else:
        wait_warp()
def warp_randomly(item_nr, should_set_home):
    set_filter('esc')
    time.sleep(2)
    print('warp to site')
    if item_nr == -1:
        i = 1 + int((get_filter_list_size() - 1) * random.random())
        device_click_rectangle(742, 47 + 51 * i, 158, 44)
        device_click_rectangle(543, 101 + 51 * i, 174, 55)
        time.sleep(1)
        device_click_rectangle(742, 47 + 51 * 1, 158, 44)
        device_click_rectangle(543, 101 + 51 * 1, 174, 55)
    else:
        i = int(get_filter_list_size() * random.random())
        device_click_rectangle(742, 47 + 51 * i, 158, 44)
        device_click_rectangle(543, 101 + 51 * i, 174, 55)
        time.sleep(1)
        device_click_rectangle(742, 47, 158, 44)
        device_click_rectangle(543, 101, 174, 55)
    time.sleep(5)
    if should_set_home:
        wait_warp_and_set_home()
    else:
        wait_warp()

