# only works on 960x540

import re
import subprocess
import sys
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
from random import randint

tess.pytesseract.tesseract_cmd = 'E:\\Eve_Echoes\\Bot\Programs\\Tesseract-OCR\\tesseract.exe'
def read_config_file_uni():
    print('\tread_config_file_uni')
    file = open(path + 'config.txt')
    tmp = file.readline()
    while tmp != '':
        tmp = str(tmp).split()
        if tmp[0] == 'ship':
            global ship
            ship = tmp[1]
            if ship == 'cruiser':
                global module_icon_radius
                module_icon_radius = 23
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
        if tmp[0] == 'safety_time':
            global safety_time
            safety_time = int(tmp[1])
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
        if tmp[0] == 'ding':
            global ding
            print('set ding when ganked to ', tmp[1])
            ding = int(tmp[1])
        tmp = file.readline()
    file.close()


COLOR_WHITE = [255, 255, 255, 255]

# INIT GLOBAL VALUES
if 1:
    # updated by functions
    health_st_list, health_ar_list, health_sh_list, cap_list = [], [], [], []
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
    confirm_green = [47, 94, 89, 255]
    undock_yellow = [174, 147, 40, 255]

    # to be changed by user / fixed
    path = ''
    path_to_script = ''
    start = 'main'
    ship = 'frigate'
    ding = 0
    preferredOrbit = 29
    planet = 0
    repeat = 0
    safety_time = 300
    device_nr = 1
    name = ''
    home = 0
    bait = 0
    random_warp = 1
    time_farming = time.time()
    # connect to Bluestacks
    Adb = Client(host='127.0.0.1', port=5037)
    Devices = Adb.devices()
    if len(Devices) < 1:
        print('no device attached')
        quit()
    # CS = current Screenshot
    Device = Devices[0]
    CS = Device.screencap()
    with open(path + 'screen.png', 'wb') as f:
        f.write(CS)
    CS_cv = cv.imread('screen.png')
    CS_image = Image.open('screen.png')
    CS_image = np.array(CS_image, dtype=np.uint8)

# GETTERS
# every simple setter and getter with internal values
def get_module_list():
    return ModuleList
def get_safety_time():
    return safety_time
def get_eco_mode():
    return eco_mode
def set_eco_mode():
    global eco_mode
    eco_mode = 1
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
def get_start():
    return start
def set_path(pa):
    global path
    path = pa
def set_path_to_script(pa):
    global path_to_script
    path_to_script = pa
def toggle_planet():
    global planet
    planet = abs(planet - 1)
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# INTERNAL HELPER FUNCTIONS
# big slow warum up functions
def update_modules():
    global ModuleList
    ModuleList = []
    file = open(path_to_script + 'assets\\modules\\' + ship + '\\_pos.txt')
    tmp = file.readline()
    while tmp != '':
        tmp = tmp.split()

        # only 1 prop module (often sees afterburner and warpdrive as the same)
        continue_value = 1
        if tmp[1] == 'prop':
            for module in ModuleList:
                if module[1] == 'prop':
                    continue_value = 0
        if continue_value == 1:

            ar = cv.imread(path_to_script + 'assets\\modules\\' + ship + '\\' + tmp[0] + '.png')
            result = cv.matchTemplate(CS_cv, ar, cv.TM_CCORR_NORMED)
            threshold = 0.98
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
    file.close()
    # cv.imshow('tmp', CS_cv)
    # cv.waitKey()
    print(str(len(ModuleList)) + ' Modules found')
def config_uni():
    read_config_file_uni()
    calc_hp_pos()
    global CS_cv, CS_image, Device
    # connect to Bluestacks
    if len(Devices) < device_nr + 1:
        print('not enough devices attached')
        quit()
    # CS = current Screenshot
    Device = Devices[device_nr]
    cs = Device.screencap()
    with open(path + 'screen.png', 'wb') as f:
        f.write(cs)
    CS_cv = cv.imread(path + 'screen.png')
    CS_image = Image.open(path + 'screen.png')
    CS_image = np.array(CS_image, dtype=np.uint8)

# READING
# everything that reads the screen and returns something
# fast
def get_hp():
    health_str, health_arm, health_shi = 0, 0, 0
    length_lists = len(health_st_list)
    for i in range(length_lists):
        pos = health_st_list[i]
        if CS_image[pos[1]][pos[0]][2] > 90:
            health_str = int(100-i*100/length_lists)
            break
    for i in range(length_lists):
        pos = health_ar_list[i]
        if CS_image[pos[1]][pos[0]][2] > 90:
            health_arm = int(100-i*100/length_lists)
            break
    for i in range(length_lists):
        pos = health_sh_list[i]
        if CS_image[pos[1]][pos[0]][2] > 90:
            health_shi = int(100-i*100/length_lists)
            break
    print('\t\t\tget_hp(): ', health_shi, health_arm, health_str)
    return health_shi, health_arm, health_str
def get_cap():
    length_list = len(cap_list)
    for i in range(length_list):
        pos = cap_list[i]
        if CS_image[pos[1]][pos[0]][0] < 200:
            print('\t\t\tget_cap(): ', i * 100 / length_list)
            return i * 100 / length_list

    print('\t\t\tget_cap():', 100)
    return 100
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
            result = int(tmp / precision * 100)
            print('\t\t\tget_speed():', result)
            return result
        tmp += 1
    # cv.imshow('image', CS_cv)
    # cv.waitKey(0)
    print('\t\t\tget_speed():', 100)
    return 100
def get_cargo():
    steps = 33
    x, y, w = 3, 61, 85 / steps
    # 0.55 match, 0.69 no match
    old_color = CS_image[y][x]
    for i in range(steps):
        i += 1
        new_color = CS_image[y][int(x + (i * w))]
        # cv.rectangle(CS_cv, (int(x + (i * w)), y), (int(x + (i * w)), y), color=(0, 255, i * 10), thickness=1, lineType=cv.LINE_4)
        # print(compare_colors(new_color, old_color), new_color)
        if compare_colors(new_color, old_color) > 9:
            result = int(100 * (i-1) / steps)
            print('\t\t\tget_cargo(): ', result)
            return result
        old_color = new_color
    # cv.imshow('image', CS_cv)
    # cv.waitKey(0)
    # no contrast in there, have to work with colors:
    cargo_yellow = [52, 47, 26, 255]
    # print(CS_image[y][int(x + ((steps-1) * w))],  CS_image[y][int(x + (steps * w) + 7)], cargo_yellow, compare_colors(CS_image[y][int(x + (steps * w))] - CS_image[y][int(x + (steps * w) + 7)], cargo_yellow))
    if compare_colors(CS_image[y][int(x + (steps * w))] - CS_image[y][int(x + (steps * w) + 7)], cargo_yellow) < 10:
        print('\t\t\tget_cargo(): ', 100)
        return 100
    print('\t\t\tget_cargo(): ', 0)
    return 0
def get_autopilot():
    x_a, y_a, x_b, y_b = 43, 102, 43, 127
    # check if autopilot is online (2 pixels because safety)
    if compare_colors(CS_image[y_a][x_a], outer_autopilot_green) < 10 and \
            compare_colors(CS_image[y_b][x_b], outer_autopilot_green) < 10:
        print('\t\t\tget_autopilot(): ', 1)
        return 1
    print('\t\t\tget_autopilot(): ', 0)
    return 0
def get_autopilot_active():
    x_c, y_c = 26, 121
    # add_point(x_c, y_c)
    # show_image()
    if compare_colors(CS_image[y_c][x_c], inner_autopilot_green) < 13:
        print('\t\t\tget_autopilot_active(): ', 1)
        return 1
    print('\t\t\tget_autopilot_active(): ', 0)
    return 0
def get_is_capsule():
    print('\t\t\tget_is_capsule(): start')
    tmp_module_list = []
    file = open(path_to_script + 'assets\\modules\\' + ship + '\\_pos.txt')
    print(0)
    tmp = file.readline()
    while tmp != '':
        print(tmp)
        tmp = tmp.split()
        if tmp[0] != 'web':
            ar = cv.imread(path_to_script + 'assets\\modules\\' + ship + '\\' + tmp[0] + '.png')
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
                    tmp_module_list.append([tmp[0], tmp[1], center[0], center[1]])
                    # cv.circle(CS_cv, center, module_icon_radius, color=(0, 255, 0), thickness=2, lineType=cv.LINE_4)
        tmp = file.readline()
    print(1)
    file.close()
    if len(tmp_module_list) == 0:
        print('\t\t\tget_is_capsule(): ', 1)
        return 1
    print('\t\t\tget_is_capsule(): ', 0)
    return 0
def get_is_in_station():
    # basically checking for the huge undock symbol
    x_a, y_a, x_b, y_b = 822, 174, 838, 174
    if compare_colors(CS_image[y_a][x_a], undock_yellow) < 8 and \
            compare_colors(CS_image[y_b][x_b], undock_yellow) < 8:
        print('\t\t\tget_is_in_station(): ', 1)
        return 1
    print('\t\t\tget_is_in_station(): ', 0)
    return 0
def get_inventory_open():
    color = [51, 110, 100]
    x_a, y_a, x_b, y_b = 37, 18, 37, 40
    if compare_colors(CS_image[y_a][x_a], color) < 8 and \
            compare_colors(CS_image[y_b][x_b], color) < 8:
        print('\t\t\tget_inventory_open(): ', 1)
        return 1
    print('\t\t\tget_inventory_open(): ', 0)
    return 0
# slow
def get_filter_icon(filter_name):
    print('\t\tget_filter_icon(): ', filter_name)
    x, y, w, h = 932, 40, 5, 277
    crop_img = CS_cv[y:y + h, x:x + w]
    for icon_file in os.listdir(path_to_script + 'assets\\filter_icons\\'):
        if filter_name in icon_file:
            image2 = cv.imread(path_to_script + 'assets\\filter_icons\\' + icon_file)
            result = cv.matchTemplate(crop_img, image2, cv.TM_CCORR_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
            border = 0.99
            if ship == 'cruiser':
                border = 0.975
            if filter_name == 'npc':
                border = 0.89
            print('\t\t\ticon, max, border: ', icon_file, max_val, border)
            if max_val > border:
                # icon gen
                # crop_img = CS_cv[y+max_loc[1]:y+max_loc[1] + 10, x+max_loc[0]:x+max_loc[0] + 6]
                # show_image(image_remove_dark(crop_img, 130), 1)
                return max_loc[0] + x, max_loc[1] + y
    return 0
# todo
def get_filter_list_size():
    return random_warp
def get_is_locked(target):
    target -= 1
    # if target = 0
    if target == 1:
        x, y, h = 629, 32, 12
        pix_not_gray = 0
        for i in range(h):
            if abs(int(CS_cv[y + i][x][0]) - CS_cv[y + i][x][1]) > 4 or \
                    abs(int(CS_cv[y + i][x][1]) - CS_cv[y + i][x][2]) > 4 or \
                    58 > CS_cv[y + i][x][0] or CS_cv[y + i][x][0] > 160:
                pix_not_gray += 1
        if pix_not_gray < 5:
            print('\t\t\tget_is_locked(): ', target, 1)
            return 1
        print('\t\t\tget_is_locked(): ', target, 0)
        return 0
    outer_x, outer_y, inner_x, inner_y, hp_x, hp_y = 631, 16, 671, 22, 656, 50
    # is something targeted?
    outer_brightness = image_get_blur_brightness(outer_x, outer_y)
    inner_brightness = image_get_blur_brightness(inner_x, inner_y)
    hp_brightness = image_get_blur_brightness(hp_x, hp_y)
    # print(outer_brightness, inner_brightness, hp_brightness - inner_brightness)
    if outer_brightness*9/12 > inner_brightness:
        if hp_brightness - inner_brightness > 16:
            print('\t\t\tget_is_locked(): ', target, 1)
            return 1
    print('\t\t\tget_is_locked(): ', target, 0)
    return 0
def get_criminal():
    # in a small screen criminals have a 6x6 red symbol, ill check that area,
    # if more then 12 pix are really red, i decalare it as criminal
    x, y = [673, 613, 552, 492, 431, 370], 38
    for i in range(6):
        # add_rectangle(x[i], y, 5, 5)
        crop_img = CS_cv[y:y + 6, x[i]:x[i] + 6]
        red_pixel_count = 0
        for row in crop_img:
            for pixel in row:
                if pixel[2] > 180 and int(pixel[0])+int(pixel[1]) < 160:
                    red_pixel_count += 1
                    if red_pixel_count > 15:
                        print('get_criminal(): target', i)
                        return i + 1
    print('\t\t\tget_criminal():no')
    return 0
def get_tar_cross():
    tar_cross_green = [136, 138, 122]
    if image_get_blur_brightness(597, 341) > 30:
        return 0
    x, y, h = 599, 333, 15
    pix_not_green = 0
    for i in range(h):
        for c in range(3):
            if abs(CS_cv[y + i][x][c] - tar_cross_green[c]) > 20:
                pix_not_green += 1
    if pix_not_green > 4:
        print('\t\t\tget_tar_cross():', 0)
        return 0
    print('\t\t\tget_tar_cross():', 1)
    return 1
def get_module_is_active(module):
    if module[1] == 'drone':
        # i doubt always getting the perfect center for drone modules, so we have to look out for the cross
        for i in range(5):
            x, y, h = module[2] - 22 + i, module[3] - 27, 19
            pix_not_green = 0
            for i in range(h):
                for c in range(3):
                    if CS_cv[y + i][x][c] < 135:
                        pix_not_green += 1
            if pix_not_green < 9:
                return 1
        return 0
    activate_blue, activate_red = [206, 253, 240, 255], [250, 253, 216, 255]
    x, y = module[2] + 2, module[3] - module_icon_radius
    add_rectangle(x, y, 0, 0)
    # print(compare_colors(CS_image[y][x], activate_blue))
    if compare_colors(CS_image[y][x], activate_blue) < 25:
        print('\t\t\tget_module_is_active():', module[0], 1)
        return 1
    print('\t\t\tget_module_is_active():', module[0], 0)
    # show_image(0, 0)
    return 0
# combined
def get_inventory_value_small_screen(to_open):
    print('\t\t\tget_inventory_value_small_screen()')
    x, y, w, h = 327, 492, 180, 26
    if to_open:
        # open inventory
        device_click_rectangle(5, 61, 83, 26)
        time.sleep(1.5)
        device_update_cs()
    crop_img = CS_cv[y:y + h, x:x + w]
    # show_image(crop_img, 1)
    raw_text = '0' + str(tess.image_to_string(crop_img).strip())
    raw_text = re.sub('\D', '', raw_text)
    if to_open:
        # click on close
        device_click_circle(926, 30, 10)
    print('\t\t\tcurrent inventory value: ', int(raw_text))
    return int(raw_text)
def get_wallet_balance():
    print('\t\t\tget_wallet_balance()')
    device_click_rectangle(95, 60, 84, 28)
    time.sleep(2)
    device_update_cs()
    x, y, w, h = 193, 118, 238, 27
    crop_img = image_remove_dark(CS_cv[y:y + h, x:x + w], 180)
    raw_text = '0' + str(tess.image_to_string(crop_img).strip())
    raw_text = re.sub('\D', '', raw_text)
    # click on close
    device_click_circle(926, 30, 10)
    print('\t\t\tcurrent wallet balance: ', int(raw_text))
    return int(raw_text)

# PRINTING
# everything that creates a basic UI for the programmer
def add_point(x, y, stroke_width=1):
    print('\t\t\tadd_point(): ', x, y)
    cv.rectangle(CS_cv, (x, y), (x + 1, y + 1),
                 color=(0, 255, 0), thickness=stroke_width, lineType=cv.LINE_4)
def add_rectangle(x, y, w, h, stroke_width=2):
    print('\t\t\tadd_rectangle(): ', x, y, w, h)
    cv.rectangle(CS_cv, (x, y), (x + w, y + h),
                 color=(0, 255, 0), thickness=stroke_width, lineType=cv.LINE_4)
def show_image(image=CS_cv, add=0):
    print('\t\tshow_image()')
    if add == 0:
        cv.imshow('tmp', CS_cv)
    else:
        cv.imshow('tmp', image)
    cv.waitKey()
def save_screenshot(name_of_image=None):
    print('\t\tsave_screenshot')
    # import random
    # import string
    # file_name = 'z'.join(random.choice(string.ascii_lowercase) for i in range(6))
    if name_of_image is None:
        now = datetime.datetime.now()
        with open('z' + str(now.hour) + '_' + str(now.minute) + '_' + str(now.second) + '.png', 'wb') as h:
            h.write(CS)
    else:
        with open(name_of_image + '.png', 'wb') as h:
            h.write(CS)
def ding_when_ganked():
    print('\t\tding_when_ganked() ', ding_when_ganked)
    if ding == 1:
        playsound(path_to_script + 'assets\\sounds\\bell.wav')
def log(something_to_write):
    absolutely_professional_database = open('E:\\Eve_Echoes\\Bot\\professional_database.txt', 'a')
    absolutely_professional_database.write(something_to_write + "\n\n")
    absolutely_professional_database.close()
def interface_show_player():
    print('\t\tinterface_show_player')
    x, y, h, w = 66, 1, 87, 127
    crop_img = CS_cv[y:y + h, x:x + w]
    cv.imshow('tmp', crop_img)
    cv.waitKey()

# CALCULATIONS
# number crunching and image processing
def get_point_in_circle(x, y, r):
    a = 3.  # shape
    angle = np.random.default_rng().random() * np.pi
    r = r - np.random.default_rng().power(a) * r
    return np.cos(angle) * r + x, np.sin(angle) * r + y
def calc_hp_pos():
    print('\t\t\tcalc_hp_pos()')
    r_st = 39
    r_ar = 49
    r_sh = 57
    r_cap = -57
    calc_hp_pos_helper(r_st, 1/10, -1, 0, 0)
    calc_hp_pos_helper(r_ar, 1/6, 0, 0, 1)
    calc_hp_pos_helper(r_sh, 1/6, 0, 0, 2)
    calc_hp_pos_helper(r_cap, 1/8, 0, -0.041, 3)
    # cv.imshow('image', CS_cv)
    # cv.waitKey(0)
def calc_hp_pos_helper(r, off, offset, rad_off, nbr):
    print('\t\t\tcalc_hp_pos_helper()')
    global health_st_list, health_ar_list, health_sh_list
    tmp = 0
    precision = 20
    factor_y = 0.67
    center_x = 479
    center_y = 466
    while tmp < precision:
        angle = np.pi * (1.32 + rad_off - 0.63 * tmp / precision)
        x = int(center_x + np.cos(angle) * r)
        y = int(center_y + np.sin(angle) * r * factor_y - abs(10 - abs(tmp - precision / 2)) * off + offset)
        if nbr == 0:
            health_st_list.append([x, y])
        if nbr == 1:
            health_ar_list.append([x, y])
        if nbr == 2:
            health_sh_list.append([x, y])
        if nbr == 3:
            cap_list.append([x, y])
        # cv.rectangle(CS_cv, (x, y), (x, y), color=(0, 255, tmp * 10), thickness=1, lineType=cv.LINE_4)
        # if CS_image[y][x][2] > 90:
        #    return int(100 - tmp / precision * 100)
        tmp += 1
    return 0
# todo
def compare_colors(a, b):
    # print('\t\t\tcompare_colors()')
    fir = abs(int(a[0]) - int(b[0]))
    sec = abs(int(a[1]) - int(b[1]))
    thi = abs(int(a[2]) - int(b[2]))
    return int((fir + sec + thi) / 7.5)
def image_remove_dark(image, border):
    print('\t\t\timage_remove_dark() ')
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
    # print('\t\t\timage_compare_text()')
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
    print('\t\t\timage_get_blur_brightness()')
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

# TASK BASICS
# task sub functions, rarely used directly
# short
def power_nap():
    # print('\t\t\t\tpower_nap()')
    time.sleep(np.random.default_rng().random() * 0.3 + 0.5)
def device_click_circle(x, y, r):
    tmp = get_point_in_circle(x, y, r)
    print('\t\t\tdevice_click_circle(): ', tmp[0], tmp[1])
    Device.shell(f'input touchscreen tap {tmp[0]} {tmp[1]}')
    power_nap()

    # great display:
    # https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.power.html#numpy.random.Generator.power
def device_click_rectangle(x, y, w, h):
    x = w * np.random.default_rng().random() + x
    y = h * np.random.default_rng().random() + y
    print('\t\t\tdevice_click_rectangle(): ', x, y)
    Device.shell(f'input touchscreen tap {x} {y}')
    power_nap()
    return x, y
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
    r = 77 + d * 1.5
    print('\t\t\tdevice_swipe_from_circle(): ', x, y, d, direction)
    Device.shell(f'input touchscreen swipe {x} {y} {np.cos(angle) * r + x} {np.sin(angle) * r + y} 1000')
    power_nap()
def target_action(target_nbr, action_nbr, distance=0):
    print('\t\t\ttarget_action()', target_nbr, action_nbr)
    target_nbr -= 1
    action_nbr -= 1
    tar_x, tar_y, tar_off_x = 670, 38, -61
    dd_x, dd_y, dd_off_y = 525, 78, 58
    device_click_circle(tar_x + target_nbr * tar_off_x, tar_y, module_icon_radius)
    # device_click_rectangle(dd_x + target_nbr * tar_off_x, dd_y + dd_off_y * action_nbr, 170, 47)
    device_swipe_from_circle(dd_x + target_nbr * tar_off_x + randint(1, 170),  dd_y + dd_off_y * action_nbr + randint(1, 47), 0, distance, 1)
    return
def filter_action(target_nbr, action_nbr, expected_list_size):
    print('\t\t\tfilter_action()', target_nbr, action_nbr, expected_list_size)
    if target_nbr < 1 or action_nbr < 1:
        print('filter action needs 1 or higher')
        quit()
    if target_nbr > 5:
        device_click_filter_block()
    target_nbr -= 1
    action_nbr -= 1
    tar_x, tar_y, w, h, tar_off_y = 742, 47, 157, 37, 52
    dd_x, dd_off_y = 539, 57
    device_click_rectangle(tar_x, tar_y + tar_off_y * target_nbr, w, h)
    # device_update_cs()
    # add_rectangle(tar_x, tar_y + tar_off_y * target_nbr, w, h)
    # add_rectangle(dd_x, min(tar_y + tar_off_y * target_nbr, 540 - expected_list_size * 57) + dd_off_y * action_nbr, 170, 47)
    device_click_rectangle(dd_x, min(tar_y + tar_off_y * target_nbr, 540 - expected_list_size * 57 + 5) + dd_off_y * action_nbr, 170, 47)
    # show_image(0, 0)
    return
def filter_swipe(direction):
    print('\t\t\tfilter_swipe()')
    # 0 is swipe down
    if direction == 0:
        device_swipe_from_circle(822, 493, 20, 400, 3)
        return
    device_swipe_from_circle(822, 100, 20, 400, 1)
# longer
def catch_bad_eco_mode(expected_autopilot_status):
    time.sleep(5)
    return
    print('\t\tcatch_bad_eco_mode()', expected_autopilot_status)
    # basically asks if the task is mining
    if ship == 'dump': #'frigate':
        # tries to catch bad eco modes and returns the ship home
        activate_autopilot(1)
        time.sleep(2.5)
        device_update_cs()
        if get_autopilot_active() == expected_autopilot_status:
            print(' got bad eco_mode')
            set_eco_mode()
            device_toggle_eco_mode()
            set_home()
            time.sleep(1)
            device_update_cs()
            activate_autopilot(0)
            wait_end_navigation(20)
            return 1
        activate_autopilot(1)
        return 0
# todo
def device_toggle_eco_mode():
    global eco_mode
    eco_mode = 1 - eco_mode
    # if eco_mode == 0:
        # ding_when_ganked()
    print('\t\ttoggle eco mode to: ', eco_mode)
    # subprocess.call(["D:\Program Files\AutoHotkey\AutoHotkey.exe", "E:\\Eve_Echoes\\Bot\\ahk_scripts\\toggle_eco_" + name + ".ahk"])
def device_record_video():
    print('device_record_video')
    subprocess.call(["D:\Program Files\AutoHotkey\AutoHotkey.exe", "E:\\Eve_Echoes\\Bot\\ahk_scripts\\recording_" + name + ".ahk"])
def device_update_cs():
    print('\t\t\tdevice_update_cs()')
    global CS_cv, CS, CS_image
    CS = Device.screencap()
    with open(path + 'screen.png', 'wb') as g:
        g.write(CS)
    CS_cv = cv.imread(path + 'screen.png')
    CS_image = Image.open(path + 'screen.png')
    CS_image = np.array(CS_image, dtype=np.uint8)
# specialized
def device_click_filter_block():
    print('\t\t\tdevice_click_filter_block()')
    device_click_rectangle(740, 46, 161, 269)
def close_pop_ups():
    print('\t\t\tclick_close_for_full_window()')
    started = 0
    stopped = 0
    for i in range(10):
        device_update_cs()
        if get_inventory_open():
            started = 1
            # click on close
            device_click_circle(926, 30, 10)
            time.sleep(2)
        else:
            stopped = 1
            break

    if started == 1 and stopped == 0:

        device_click_circle(932, 31, 10)


# TASKS
# construction blocks for combined tasks or algorithms
# short
def activate_filter_window():
    x, y = 923, 302
    # match was about 0.22, no match was 0.64, match = need fix
    if compare_colors(CS_image[y][x], color_white) < 40:
        device_click_circle(x, y, 5)
        print('\t\tactivate_filter_window()', 1)
        return 1
    print('\t\tactivate_filter_window()', 0)
    return 0
def dump_items():
    # open inventory
    device_click_rectangle(5, 61, 83, 26)
    time.sleep(1.5)
    # print('\t\tdump_items()', int(dump_tail()))
    # return int(dump_tail())
def dump_both():
    print('\t\tdump_ore()')
    # open inventory
    device_click_rectangle(5, 61, 83, 26)
    time.sleep(1.5)

    # venture ore
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

    # venture cargo
    device_click_rectangle(18, 315, 119, 59)
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
def dump_ore():
    print('\t\tdump_ore()')
    # open inventory
    device_click_rectangle(5, 61, 83, 26)
    time.sleep(1.5)
    # venture ore
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
def dump_tail():
    print('\t\t\tdump_tail()')
    # select all
    device_click_rectangle(701, 458, 68, 60)
    time.sleep(1)
    device_update_cs()
    value = get_inventory_value_small_screen(0)
    # move to
    device_click_rectangle(21, 80, 145, 56)
    time.sleep(0.3)
    # item hangar
    device_click_rectangle(294, 96, 194, 54)
    time.sleep(5)
    # click on close
    device_click_circle(926, 30, 10)
    print('inventory value:', value)
    return value
def activate_autopilot(force_click=0):
    print('\t\tactivate_autopilot()', force_click)
    if force_click:
        device_click_circle(22, 116, 10)
        return
    if get_autopilot():
        if not get_autopilot_active():
            device_click_circle(22, 116, 10)
            return
# todo does sometimes get info window in eco mode
def activate_module(module):
    print('\t\tactivate_module()', module[0])
    activate_blue, activate_red = [206, 253, 240, 255], [250, 253, 216, 255]
    x, y = module[2] + 2, module[3] - module_icon_radius
    if module[1] == 'esc':
        device_click_circle(module[2], module[3], module_icon_radius)
    # print('\t\t\t', get_module_is_active(module), compare_colors(CS_image[y][x], activate_red), CS_image[y][x])
    if get_module_is_active(module) == 0 and compare_colors(CS_image[y][x], activate_red) > 8:
        device_click_circle(module[2], module[3], module_icon_radius)
        return 1
    return 0
def activate_the_modules(its_name):
    print('\t\tactivate_modules()', its_name)
    tmp = 0
    for module in ModuleList:
        if module[1] == its_name:
            if activate_module(module):
                tmp = 1
    return tmp
def deactivate_the_modules(its_name):
    print('\t\tdeactivate_modules()', its_name)
    tmp = 0
    for module in ModuleList:
        if module[1] == its_name:
            if deactivate_module(module):
                tmp = 1
    return tmp
def deactivate_module(module):
    print('\t\tdeactivate_module()', module[0])
    x, y = module[2] + 2, module[3] - module_icon_radius
    if get_module_is_active(module) == 1:
        device_click_circle(module[2], module[3], module_icon_radius)
def repair(desired_hp):
    print('\t\trepair() ', desired_hp)
    # todo not tested
    hp = get_hp()
    for module in ModuleList:
        if module[0] == 'rep':
            if hp[1] < desired_hp:
                activate_module(module)
            else:
                deactivate_module(module)
        if module[1] == 'boost':
            if hp[0] < desired_hp:
                activate_module(module)
            else:
                deactivate_module(module)
def set_filter(string_in_name, force):
    print('\t\tset_filter() ', string_in_name, force)
    # swaps to a filter containing the given string
    if activate_filter_window():
        time.sleep(2)
        device_update_cs()
        if activate_filter_window():
            time.sleep(1)
            device_update_cs()
    # Filter Header, use the cv.imshow to see if it fits
    x, y, w, h, y_first_option, y_off = 735, 7, 74, 30, 75, 52
    crop_img = CS_image[y:y + h, x:x + w]
    if string_in_name not in tess.image_to_string(crop_img) or force:
        # TODO: improve
        device_click_rectangle(x, y, w, h)
        if string_in_name in 'Anomalies':
            device_click_rectangle(x, y_first_option, w, h)
            return
        if string_in_name in 'PvE':
            device_click_rectangle(x, y_first_option + y_off, w, h)
            return
        if string_in_name in 'esc':
            device_click_rectangle(731, 338, 180, 45)
            device_update_cs()
            if check_for_lock_on_police():
                time.sleep(2)
                device_click_rectangle(731, 338, 180, 45)
            return
        if string_in_name in 'Mining':
            device_click_rectangle(731, 286, 180, 45)
            return
        else:
            print('todo swap filter')
        set_filter(string_in_name, force)
    # cv.imshow('.', crop_img)
    # cv.waitKey()
# longer
def reset():
    save_screenshot()
    log('reset: ' + str(datetime.datetime.utcnow()+datetime.timedelta(hours=2)))
    # does the screen react?  open and close inventory
    device_click_rectangle(5, 61, 83, 26)
    for i in range(5):
        time.sleep(1.5)
        device_update_cs()
        if get_inventory_open():
            does_react = 1
            break
        if i == 4:
            hard_reset()

    close_pop_ups()
    time.sleep(2)
    set_home()
    time.sleep(2)
    activate_autopilot()
    wait_end_navigation()
    if get_is_in_station():
        os.system("start E:\Eve_Echoes\Bot\\ahk_scripts\start_bat_" + get_name() + ".ahk")
    else:
        hard_reset()
def hard_reset():
    # for /f "tokens=3,*" %a in ('tasklist /fo list /v ^| find "Window Title"') do @if not "%a"=="N/A" echo %a %b
    os.system("cmd /k Taskkill /F /FI \"WindowTitle eq Kort Foster\" /T")
    os.system("cmd /k Taskkill /F /FI \"WindowTitle eq Bronson Barton\" /T")
    playsound(path_to_script + 'assets\\sounds\\bell.wav')
    quit()
def set_home():
    print('\t\tset_home()')
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
    print('\t\tset_pi_planet_for_autopilot()', target)
    # only works for pI location
    # click portrait
    device_click_rectangle(50, 4, 60, 40)
    time.sleep(0.5)
    # planetary production
    device_click_rectangle(481, 332, 82, 84)
    time.sleep(1)
    # click planet
    off = 86
    device_click_rectangle(25, 123 + target * off, 115, 36)
    # click set des
    device_click_rectangle(791, 460, 154, 49)
    # click on close
    device_click_circle(925, 30, 15)
    # time.sleep(1)
    # device_click_circle(925, 30, 15)
    time.sleep(5)
def escape_autopilot():
    activate_autopilot(1)
    device_record_video()
    print('\tescape_autopilot()')
    if get_eco_mode():
        device_toggle_eco_mode()
    time.sleep(1)
    device_update_cs()
    repair(100)
    activate_autopilot(0)
    time.sleep(2)
    deactivate_the_modules('prop')
    activate_the_modules('esc')
    device_click_rectangle(465, 431, 32, 5)

    for i in range(20):
        device_update_cs()
        if get_speed() > 80:
            break
        time.sleep(1)

    print(' \tchecking if dead')
    in_station = get_is_in_station()
    is_capsule = get_is_capsule()
    if is_capsule or in_station:
        print('seems to be dead')
        absolutely_professional_database = open('E:\\Eve_Echoes\\Bot\\professional_database.txt', 'a')
        absolutely_professional_database.write(
            get_name() + ' died at:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1347517370)) + '\n\n')
        absolutely_professional_database.close()
        quit()
    else:
        print('going home')
        # wait until autopilot gone
        wait_end_navigation(20)
def return_autopilot():
    activate_autopilot(1)
    wait_end_navigation(20)

def wait_end_navigation(safety_time=20):
    print('\t\twait_end_navigation()')
    while 1:
        device_update_cs()
        if not get_autopilot():
            if get_is_in_station():
                return 1
            # for stargate warps
            time.sleep(10)
            device_update_cs()
            if not get_autopilot():
                if get_is_in_station():
                    return 1
                time.sleep(10)
                device_update_cs()
                if not get_autopilot():
                    return 1
        activate_autopilot(0)
        time.sleep(safety_time)
# special stuff
def check_for_lock_on_police():
    print('\t\tcheck_for_lock_on_police()')
    x_a, y_a, x_b, y_b = 804, 408, 804, 387
    # check if autopilot is online (2 pixels because safety)
    if compare_colors(CS_image[y_a][x_a], confirm_green) < 15 and \
            compare_colors(CS_image[y_b][x_b], confirm_green) < 15:
        device_click_rectangle(623, 388, 150, 46)
        return 1
    return 0
# with catch
def undock():
    # waits for screen to go black and waits for screen to get color again
    # return: 0 all okay, 1: undock unsuccessful, black screen for eternity
    print('\tundock')
    device_click_rectangle(817, 165, 111, 26)
    interrupt = 0
    count = 0
    while interrupt == 0 and count < 100:
        time.sleep(0.5)
        device_update_cs()
        count += 1
        if image_get_blur_brightness(45, 24) < 4:
            interrupt = 1

    if interrupt == 0:
        print('undock waited for 50s to undock, something is not right')
        return 1

    interrupt = 0
    count = 0
    while interrupt == 0 and count < 100:
        time.sleep(0.5)
        device_update_cs()
        count += 1
        if image_get_blur_brightness(45, 24) > 5:
            time.sleep(5)
            interrupt = 1

    if interrupt == 0:
        print('undock waited for 50s to undock, something is not right')
        return 1
    return 0



# COMBINED TASKS
# todo add quit notification
def undock_and_modules(error_count=0):
    print('\tundock_and_modules()')
    # set destination
    # set_system(planet)
    # wait until autopilot gone
    # wait_end_navigation(20)

    # clear popup
    if not get_is_in_station():
        device_click_circle(818, 87, 10)
        time.sleep(2)

    if undock():
        reset()

    # sometimes the speed meter gets broken, redock to fix
    device_update_cs()
    update_modules()
    if len(ModuleList) == 0:
        if error_count == 5:
            save_screenshot('kill')
            log(get_name() + ' got destroyed. ')
            set_home()
            activate_autopilot()
            quit()
        log(get_name() + ' no modules, try again.')
        set_home()
        activate_autopilot()
        wait_end_navigation()
        undock_and_modules(error_count+1)
    speed_x, speed_y = 460, 495
    print('speed-o-meter value: ', get_cs_cv()[speed_y][speed_x][2])
    if get_cs_cv()[speed_y][speed_x][2] < 130 or len(ModuleList) < 2:
        # re dock
        time.sleep(10)
        set_home()
        time.sleep(5)
        device_click_circle(22, 116, 10)
        time.sleep(25)
        undock_and_modules()
        return

    print('calibrating')
    # sometimes there is a sentry in the way, gotta wait for space target to vanish
# todo eco mode catch unstable
def warp_in_system(target_nbr, distance, should_set_home, desired_filter):
    print('\twarp_in_system()', target_nbr, distance, should_set_home, desired_filter)
    # the filter has to be set correctly, list cannot be scrolled, no planets/ stations, eco must be off
    # returns : 0 fine: 1 found pirates, 2:
    if target_nbr > 5:
        device_click_filter_block()

    tar_x, tar_y, w, h, tar_off_y = 742, 47, 157, 37, 52
    dd_x, dd_off_y = 539, 57

    if distance != 0:
        target_nbr -= 1
        action_nbr = 1
        device_click_rectangle(tar_x, tar_y + tar_off_y * target_nbr, w, h)
        device_swipe_from_circle(dd_x + 50, min(tar_y + tar_off_y * target_nbr, 540 - 2 * 57 + 5) + 10 + dd_off_y * action_nbr, 25, distance, 2)
    else:
        filter_action(target_nbr, 2, 2)
        filter_action(2, 2, 2)

    set_filter(desired_filter, 1)

    time.sleep(2)
    return warp_wait_trouble_fix_extension(should_set_home)
def warp_wait_trouble_fix_extension(should_set_home):
    print('\twarp_wait_trouble_fix_extension()')
    # autopilot is active and warp is initiated, checking for safe landing and eco mode trouble, if autopilot set
    # ends when enemy player found 5 sec after start or when warp ends
    if get_autopilot() == 0:
        if should_set_home:
            set_home()
            time.sleep(1)
        else:
            time.sleep(4)
    else:
        if catch_bad_eco_mode(0):
            return 2
    time.sleep(2)
    return warp_wait()
def warp_wait():
    print('\t\twarp_wait()')
    for i in range(500):
        # does nothing until speed bar goes to 15%
        device_update_cs()
        if get_filter_icon('all_ships') != 0 or get_criminal() != 0:
            return 1
        if get_speed() < 15:
            return 0
        time.sleep(0.5)
    reset()






