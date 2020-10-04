# only works on 960x540
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
import re

tess.pytesseract.tesseract_cmd = 'E:\\Eve_Echoes\\Bot\Programs\\Tesseract-OCR\\tesseract.exe'

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
device_nr = 0
name = ''


def read_config_file():
    file = open('config.txt')
    tmp = file.readline()
    while tmp != '':
        tmp = str(tmp).split()
        if tmp[0] == 'planet':
            global planet
            planet = int(tmp[1])
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
        tmp = file.readline()


# read_config_file()

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


# BASIC FUNCTIONS
def power_nap():
    time.sleep(np.random.default_rng().random() * 0.3 + 0.3)
def update_cs():
    global CS_cv, CS, CS_image
    CS = device.screencap()
    with open('screen.png', 'wb') as g:
        g.write(CS)
    CS_cv = cv.imread('screen.png')
    CS_image = Image.open('screen.png')
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
def click_circle(x, y, r):
    tmp = get_point_in_circle(x, y, r)
    device.shell(f'input touchscreen tap {tmp[0]} {tmp[1]}')
    power_nap()

    # great display:
    # https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.power.html#numpy.random.Generator.power
def click_rectangle(x, y, w, h):
    x = w * np.random.default_rng().random() + x
    y = h * np.random.default_rng().random() + y
    device.shell(f'input touchscreen tap {x} {y}')
    power_nap()
def swipe_from_circle(x, y, r, d, direction):
    tmp = get_point_in_circle(x, y, r)
    x, y = tmp[0], tmp[1]
    if d == 0:
        device.shell(f'input touchscreen tap {x} {y}')
        return

    # random direction: 0- random, 1 is down, 2 is ?, 3 is up, 4 is up

    if direction > 0:
        angle = np.pi / 2 * direction
    else:
        angle = np.random.default_rng().random() * np.pi
    r = 130 + d * 2.4

    device.shell(f'input touchscreen swipe {x} {y} {np.cos(angle) * r + x} {np.sin(angle) * r + y} 1000')
    power_nap()
def toggle_eco_mode():
    subprocess.call(["D:\Program Files\AutoHotkey\AutoHotkey.exe", "E:\\Eve_Echoes\\Bot\\ahk_scripts\\toggle_eco_" + name + ".ahk"])


# INTERNAL HELPER FUNCTIONS
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
def wait_warp():
    # does nothing until speed bar goes to 15%
    update_cs()
    if get_speed() > 15:
        wait_warp()
def show_player_for_confirmation():
    x, y, h, w = 66, 1, 87, 127
    crop_img = CS_cv[y:y + h, x:x + w]
    cv.imshow('tmp', crop_img)
    cv.waitKey()
def calibrate():
    global ModuleList
    ModuleList = []
    file = open('modules\small\_pos.txt')
    tmp = file.readline()
    while tmp != '':
        tmp = tmp.split()
        ar = cv.imread('modules\\small\\' + tmp[0] + '.png')
        result = cv.matchTemplate(CS_cv, ar, cv.TM_CCORR_NORMED)
        threshold = 0.95
        loc = np.where(result >= threshold)
        previous_point_y, previous_point_x = 0, 0
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
                ModuleList.append([tmp[0], tmp[1], center[0], center[1]])
                # cv.circle(CS_cv, center, module_icon_radius, color=(0, 255, 0), thickness=2, lineType=cv.LINE_4)
        tmp = file.readline()
    # cv.imshow('tmp', CS_cv)
    # cv.waitKey()
    print(str(len(ModuleList)) + ' Modules found')
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
def activate_autopilot():
    if get_autopilot():
        if not get_autopilot_active():
            click_circle(22, 116, 10)
            return
def swap_filter(string_in_name):
    # swaps to a filter containing the given string
    if troubleshoot_filter_window():
        update_cs()
    # Filter Header, use the cv.imshow to see if it fits
    x, y, w, h = 767, 7, 74, 30
    crop_img = CS_image[y:y + h, x:x + w]
    if string_in_name not in tess.image_to_string(crop_img):
        # TODO: improve
        click_rectangle(x, y, w, h)
        if string_in_name in 'Anomalies':
            click_rectangle(x, 118, w, h)
            return
        if string_in_name in 'PvE':
            click_rectangle(x, 206, w, h)
            return
        if string_in_name in 'esc':
            click_rectangle(731, 338, 180, 45)
            return
        if string_in_name in 'Mining':
            click_rectangle(731, 286, 180, 45)
            return
        else:
            print('todo swap filter')
        swap_filter(string_in_name)
    # cv.imshow('.', crop_img)
    # cv.waitKey()
def is_capsule():
    tmp_module_list = []
    file = open('modules\small\_pos.txt')
    tmp = file.readline()
    while tmp != '':
        tmp = tmp.split()
        ar = cv.imread('modules\\small\\' + tmp[0] + '.png')
        result = cv.matchTemplate(CS_cv, ar, cv.TM_CCORR_NORMED)
        threshold = 0.95
        loc = np.where(result >= threshold)
        previous_point_y, previous_point_x = 0, 0
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
def is_in_station():
    # basically checking for the huge undock symbol
    x_a, y_a, x_b, y_b = 822, 174, 838, 174
    print(compare_colors(CS_image[y_a][x_a], undock_yellow))
    if compare_colors(CS_image[y_a][x_a], undock_yellow) < 8 and \
            compare_colors(CS_image[y_b][x_b], undock_yellow) < 8:
        return 1
    return 0

# INTERFACE HELPER FUNCTIONS
def activate_module(module):
    activate_blue, activate_red = [206, 253, 240, 255], [194, 131, 129, 255]
    x, y = module[2] + 2, module[3] - module_icon_radius

    if compare_colors(CS_image[y][x], activate_blue) > 15 and compare_colors(CS_image[y][x], activate_red) > 15:
        click_circle(module[2], module[3], module_icon_radius)
        return 1
    return 0
def deactivate_module(module):
    activate_blue, activate_red = [206, 253, 240, 255], [194, 131, 129, 255]
    x, y = module[2] + 2, module[3] - module_icon_radius

    if compare_colors(CS_image[y][x], activate_blue) < 15:
        click_circle(module[2], module[3], module_icon_radius)
def troubleshoot_filter_window():
    x, y = 923, 302
    # match was about 0.22, no match was 0.64, match = need fix
    if compare_colors(CS_image[y][x], color_white) < 40:
        click_circle(x, y, 10)
        return 1
    return 0
def warp_to_random(maximum):
    for i in range(maximum):
        j = i + 1
        rng = random.random()
        if rng < (j + 1) / maximum:
            print('true')
            click_rectangle(742, 47 + 51 * i, 158, 44)
            click_rectangle(543, 101 + 51 * i, 174, 55)
            break


# PLAIN SCRIPTS
def dump_cargo():
    # open inventory
    click_rectangle(5, 61, 83, 26)
    time.sleep(1.5)
    # venture cargo
    click_rectangle(18, 393, 173, 41)
    time.sleep(1.5)
    # select all
    click_rectangle(701, 458, 68, 60)
    time.sleep(1)
    # move to
    click_rectangle(21, 80, 145, 56)
    time.sleep(0.3)
    # item hangar
    click_rectangle(294, 96, 194, 54)
    time.sleep(5)
    # click on close
    click_circle(926, 30, 10)
    return 1
def set_home():
    # open inventory
    click_rectangle(5, 61, 83, 26)
    time.sleep(1.5)
    # click on assets
    click_rectangle(12, 493, 182, 36)
    time.sleep(2.5)
    # click on station
    click_rectangle(12, 182, 181, 70)
    time.sleep(2)
    # click on set des
    click_rectangle(525, 461, 71, 55)
    time.sleep(0.5)
    # click set des
    click_rectangle(138, 443, 185, 42)
    time.sleep(2)
    # click on close
    click_circle(925, 30, 15)
    time.sleep(1)
    click_circle(925, 30, 15)
def set_system(target):
    # only works for pI location
    # click portrait
    click_circle(140, 45, 30)
    time.sleep(0.5)
    # planetary production
    click_rectangle(803, 562, 135, 135)
    time.sleep(1)
    # click planet
    off = 145
    click_rectangle(32, 205 + target*off, 211, 64)
    # click set des
    click_rectangle(1321, 767, 253, 81)
    # click on close
    click_circle(1543, 51, 10)
    click_circle(1543, 51, 10)
    # click on autopilot
    click_circle(38, 191, 15)
    time.sleep(1)
    # confirm
    click_rectangle(1318, 641, 253, 87)
def mine_something(maximum):
    for i in range(maximum + 1):
        rng = random.random()
        if rng < i / maximum:
            time.sleep(0.5)
            click_rectangle(742, 47 + 51 * (i - 1), 158, 44)
            time.sleep(0.5)
            click_rectangle(546, 101 + 51 * (i - 1), 158, 44)
            time.sleep(1)
            click_rectangle(742, 47 + 51 * (i - 1), 158, 44)
            click_rectangle(543, 45 + 51 * (i - 1), 174, 49)
            for module in ModuleList:
                if module[1] == 'prop':
                    activate_module(module)
            time.sleep(25)
            for module in ModuleList:
                if module[1] == 'harvest':
                    activate_module(module)
            break
    time.sleep(1)


# STATES
def wait_end_navigation(safety_time):
    print('wait for navigation')
    while 1:
        update_cs()
        if not get_autopilot():
            # for stargate warps
            time.sleep(5)
            update_cs()
            if not get_autopilot():
                time.sleep(5)
                update_cs()
                if not get_autopilot():
                    return 1
        time.sleep(safety_time)
def mining_from_station():
    # set destination
    # set_system(planet)
    # wait until autopilot gone
    # wait_end_navigation(20)
    print('undocking')
    click_rectangle(817, 165, 111, 26)
    time.sleep(15)

    print('calibrating')
    update_cs()
    troubleshoot_filter_window()
    time.sleep(1)
    calibrate()
    # warp to site todo: should implement get_list_size

    print('warp to site')
    swap_filter('esc')
    time.sleep(2)
    warp_to_random(4)
    time.sleep(5)
    warp_to_random(1)
    wait_warp()
    time.sleep(4)

    print('mine something')
    # select some asteroid
    swap_filter('ining')
    mine_something(1)

    print('setting path home')
    # set home
    set_home()

    print('waiting')
    # eco mode
    toggle_eco_mode()
    # wait x time
    time.sleep(mining_time)
    # deactivate eco mode
    toggle_eco_mode()
    time.sleep(5)

    print('checking if dead')
    if is_capsule() or is_in_station():
        absolutely_professional_database = open('E:\\Eve_Echoes\\Bot\\professional_database.txt', 'a')
        absolutely_professional_database.write(name + ' died at:' + str(time.time()))
        absolutely_professional_database.close()
        quit()

    print('going home')
    update_cs()
    # activate autopilot
    activate_autopilot()
    # wait until autopilot gone
    wait_end_navigation(20)

    print('arriving')
    # dump ressources
    dump_cargo()
    # repeat?
    if repeat == 0:
        playsound('assets\\sounds\\bell.wav')
        quit()
    mining_from_station()
    return
def mining_from_station_in_null():
    # set destination
    set_system(planet)
    # wait until autopilot gone
    wait_end_navigation(20)
    print('undocking')
    click_rectangle(817, 165, 111, 26)
    time.sleep(15)

    print('calibrating')
    update_cs()
    troubleshoot_filter_window()
    time.sleep(1)
    calibrate()

    print('going to system')
    update_cs()
    # activate autopilot
    activate_autopilot()
    # wait until autopilot gone
    wait_end_navigation(20)

    # warp to site todo: should implement get_list_size
    print('warp to site')
    swap_filter('esc')
    time.sleep(2)
    warp_to_random(1)
    time.sleep(5)
    warp_to_random(1)
    wait_warp()
    time.sleep(4)

    print('mine something')
    # select some asteroid
    swap_filter('ining')
    mine_something(1)

    print('setting path home')
    # set home
    set_home()

    print('waiting')
    # eco mode
    toggle_eco_mode()
    # wait x time
    time.sleep(mining_time)
    # deactivate eco mode
    toggle_eco_mode()
    time.sleep(5)

    print('going home')
    update_cs()
    # activate autopilot
    activate_autopilot()
    # wait until autopilot gone
    wait_end_navigation(20)

    print('arriving')
    # dump ressources
    dump_cargo()
    # repeat?
    if repeat == 0:
        playsound('assets\\sounds\\bell.wav')
        quit()
    mining_from_station()
    return
def main():
    show_player_for_confirmation()
    mining_from_station()


main()