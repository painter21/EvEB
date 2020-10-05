# only works on 16000x900

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

module_icon_radius = 40
color_white = [255, 255, 255, 255]
# to be changed by user / fixed
task = 'combat'
start = 'from_station'
preferredOrbit = 29
planet = 0
repeat = 0

def read_config_file():
    file = open('config.txt')
    tmp = file.readline()
    while tmp != '':
        tmp = tmp.split()
        if tmp[0] == 'preferredOrbit':
            global preferredOrbit
            preferredOrbit = int(tmp[1])
        if tmp[0] == 'planet':
            global planet
            planet = int(tmp[1])
        if tmp[0] == 'start:':
            if tmp[1] == 'combat_from_station':
                from_station()
            if tmp[1] == 'combat_from_ano':
                from_ano()
            if tmp[1] == 'combat_from_system':
                from_system()
        tmp = file.readline()
read_config_file()


# connect to Bluestacks
adb = Client(host='127.0.0.1', port=5037)
devices = adb.devices()
print(devices)
if len(devices) == 0:
    print('no device attached')
    quit()
# CS = current Screenshot
print(devices)
device = devices[0]
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


# INTERNAL HELPER FUNCTIONS
def calibrate():
    file = open('modules\_pos.txt')
    tmp = file.readline()
    while tmp != '':
        tmp = tmp.split()
        ar = cv.imread('modules\\' + tmp[0] + '.png')
        result = cv.matchTemplate(CS_cv, ar, cv.TM_CCORR_NORMED)
        threshold = 0.99
        loc = np.where(result >= threshold)
        previous_point_y, previous_point_x = 0, 0
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
                cv.circle(CS_cv, center, 40, color=(0, 255, 0), thickness=2, lineType=cv.LINE_4)
        tmp = file.readline()
    # cv.imshow('tmp', CS_cv)
    # cv.waitKey()
    print(str(len(ModuleList)) + ' Modules found')
def get_speed():
    tmp = 0
    stop = 0
    precision = 10
    factor_y = 0.67
    center_x = 800
    center_y = 779
    r = 82
    while tmp < precision and not stop:
        angle = np.pi * (0.65 - 0.32 * tmp / precision)
        x = int(center_x + np.cos(angle) * r)
        y = int(center_y + np.sin(angle) * r * factor_y)
        # cv.rectangle(CS_cv, (x, y), (x, y), color=(tmp*10, 255, 0), thickness=int((22-tmp)/2), lineType=cv.LINE_4)
        if CS_image[y][x][0] > 175:
            return int(tmp / precision * 100)
        tmp += 1
    # cv.imshow('image', CS_cv)
    # cv.waitKey(0)
    return 100
def get_player_thread():
    swap_filter('PvE')
    x, y, w, h = 1547, 86, 18, 445
    as_icon = cv.imread('assets\\all_ships_icon.png')
    crop_img = CS_cv[y:y + h, x:x + w]
    result = cv.matchTemplate(crop_img, as_icon, cv.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    if max_val > 0.999:
        return 1
    return 0
def get_list_anomaly():
    swap_filter('Ano')
    # todo: ignore closest ano
    # click filter element to expand filter
    click_rectangle(1214, 247, 308, 249)
    list_ano = []

    update_cs()

    # create a list of all anomaly locations (on screen)
    x, y, w, h = 1210, 0, 30, 900
    img_ano = cv.imread('assets\\Ano.png')
    crop_img = CS_cv[y:y + h, x:x + w]
    result = cv.matchTemplate(crop_img, img_ano, cv.TM_CCORR_NORMED)
    threshold = 0.93
    loc = np.where(result >= threshold)
    # black magic do not touch
    previous_point_y = 0
    first_run = 1
    for pt in zip(*loc[::-1]):
        # ignore double results
        if pt[1] > previous_point_y + 10:
            previous_point_y = pt[1]
            if first_run == 1:
                first_run = 0
            else:

                # icon offset, size of text field
                y_text, x_text = pt[1] - 13, pt[0] + 107 + x
                crop_img = CS_cv[y_text:y_text + 52, x_text:x_text + 204]

                # find the level of the anomaly
                # find icon
                crop_ano_level_img = CS_cv[y_text + 3:y_text + 28, x_text:x_text + 13]
                # remove darker pixels
                row_count = -1
                for row in crop_ano_level_img:
                    row_count += 1
                    pixel_count = -1
                    for pixel in row:
                        pixel_count += 1
                        brightness = 0
                        for color in pixel:
                            brightness += color
                        if brightness < 250:
                            crop_ano_level_img[row_count][pixel_count] = [0, 0, 0]
                # cv.imwrite('tmp.png', crop_ano_level_img)

                # compare it to all icon files
                highest_result = 0
                lvl = 0
                for file in os.listdir('assets\\base_level'):
                    lvl_icon = cv.imread('assets\\base_level\\' + file)
                    cv.waitKey()
                    result = cv.matchTemplate(crop_ano_level_img, lvl_icon, cv.TM_CCORR_NORMED)
                    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
                    if highest_result < max_val:
                        highest_result = max_val
                        lvl = int(file[:-4])

                raw_text = tess.image_to_string(crop_img)

                # Todo: i should improve that at some point
                x_ano_field, y_ano_field = pt[0] + x, pt[1] - 28
                if 'Scout' in raw_text or 'nquis' in raw_text:
                    list_ano.append(['scout', lvl, x_ano_field, y_ano_field, 310, 80])
                else:
                    if 'Small' in raw_text:
                        list_ano.append(['small', lvl, x_ano_field, y_ano_field, 310, 80])
                    else:
                        if 'Medium' in raw_text:
                            list_ano.append(['medium', lvl, x_ano_field, y_ano_field, 310, 80])
                        else:
                            if 'Large' in raw_text:
                                list_ano.append(['large', lvl, x_ano_field, y_ano_field, 310, 80])
                            else:
                                if 'Base' in raw_text:
                                    print('ignore base')
                                    # list_ano.append(['base', lvl, pt[0], pt[1] - 28, pt[0] + 310, pt[1] + 53])
                # icon cv.rectangle(crop_img, pt, (pt[0] + 15, pt[1] + 15), (0, 0, 255), 2)
                # text field cv.rectangle(CS_cv, (x_text, y_text), (x_text + 204, y_text + 52), (0, 0, 255), 2)
            # cv.imshow('.', CS_cv)
            # cv.waitKey()
    for ano in list_ano:
        print(ano)
    return list_ano
def search_new_system():
    print('todo search_new_system()')
    quit()
def choose_anomaly():
    # todo
    ano_list = get_list_anomaly()
    if len(ano_list) == 0:
        print('system empty')
        search_new_system()
        quit()
    for ano in ano_list:
        if ano[0] == 'scout':
            playsound('assets\\sounds\\bell.wav')
            return ano
    for ano in ano_list:
        if ano[1] == 4:
            return ano
    for ano in ano_list:
        if ano[1] == 5:
            return ano
    for ano in ano_list:
        if ano[1] == 6 and ano[0] == 'medium':
            return ano
    for ano in ano_list:
        if ano[1] == 6 and ano[0] == 'small':
            return ano
    return ano_list[0]
def wait_warp():
    # does nothing until speed bar goes to 15%
    update_cs()
    if get_speed() > 15:
        wait_warp()
def update_hp_helper(r, off, offset):
    tmp = 0
    precision = 20
    factor_y = 0.67
    center_x = 800
    center_y = 779
    while tmp < precision:
        angle = np.pi * (1.32 - 0.62 * tmp / precision)
        x = int(center_x + np.cos(angle) * r)
        y = int(center_y + np.sin(angle) * r * factor_y - abs(10 - abs(tmp - precision / 2)) / 3 * off + offset)
        # cv.rectangle(CS_cv, (x, y), (x, y), color=(0, 255, tmp * 10), thickness=3, lineType=cv.LINE_4)
        if CS_image[y][x][2] > 90:
            return int(100 - tmp / precision * 100)
        tmp += 1
    return 0
def update_hp():
    r_st = 64
    r_ar = 80
    r_sh = 98
    global health_sh, health_ar, health_st
    health_st = update_hp_helper(r_st, 1 / 2, -2)
    health_ar = update_hp_helper(r_ar, 1, 0)
    health_sh = update_hp_helper(r_sh, 1 / 3, 0)
    # cv.imshow('image', CS_cv)
    # cv.waitKey(0)
def danger_handling_combat():
    if health_st < 90:
        print('hull critical')
        for i in range(3):
            flee(1)
        go_home()
        return 1
    if get_capacitor() < 10:
        print('capacitor critical')
        for i in range(3):
            flee(1)
        wait_for_cap()
        warp_to_ano()
        combat()
        return 1
    if get_player_thread():
        print('player detected')
        for i in range(3):
            flee(4)
        wait_warp()
        warp_to_ano()
        combat()
        return 1
    return 0
def danger_handling_farming():
    if get_player_thread():
        print('player detected')
        for i in range(3):
            flee(4)
        wait_warp()
        warp_to_ano()
        combat()
        return 1
    return 0
def get_npc_count():
    # todo: test for 10+ enemys
    swap_filter('PvE')
    x, y, w, h = 1547, 86, 18, 445
    as_icon = cv.imread('assets\\enemy_npc.png')
    crop_img = CS_cv[y:y + h, x:x + w]
    result = cv.matchTemplate(crop_img, as_icon, cv.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    if max_val > 0.95:
        y = max_loc[1] + y
        x = max_loc[0] + 10 + x
        h, w = 35, 25
        crop_img = CS_cv[y:y + h, x:x + w]
        blank_img = np.zeros((h, w * 2, 3), np.uint8)
        line = 0
        while line < h - 2:
            row = 0
            while row < w - 2:
                brightness = 0
                for color in crop_img[line][row]:
                    brightness += color
                    if brightness > 300:
                        blank_img[line][row] = crop_img[line][row]
                        blank_img[line][row + w - 10] = crop_img[line][row]
                row += 1
            line += 1
        raw_text = tess.image_to_string(blank_img).strip()
        raw_text = re.sub('\D', '', raw_text)
        tmp = 0
        if int(len(raw_text)) == 0:
            return 2
        while tmp < int(len(raw_text) / 2):
            raw_text = raw_text[:-1]
            tmp += 1
        return int(raw_text)
    return 0
def warp_to_ano():
    swap_filter('Ano')
    anomaly = choose_anomaly()
    if anomaly == 'scout':
        warp_to(0, anomaly[2], anomaly[3], anomaly[4], anomaly[5])
        solve_scouts()
    print()
    print(anomaly)
    # sometimes the interface times out and i have to reopen it
    click_rectangle(1243, 265, 275, 254)
    warp_to(preferredOrbit, anomaly[2], anomaly[3], anomaly[4], anomaly[5])
    time.sleep(3)
    farm_tracker(anomaly)
    time.sleep(7)
    wait_warp()

    # swap to PvE
def get_cargo():
    steps = 20
    x, y, w = 6, 105, int(145 / steps)
    # 0.55 match, 0.69 no match
    old_color = CS_image[y][x]
    for i in range(steps):
        new_color = CS_image[y][x + (i * w)]
        # cv.rectangle(CS_cv, (x + (i * w), y), (x + (i * w), y), color=(0, 255, i * 10), thickness=3, lineType=cv.LINE_4)
        # print(compare_colors(new_color, old_color), new_color)
        if compare_colors(new_color, old_color) > 9:
            return 100 * i / steps
        old_color = new_color
    # cv.imshow('image', CS_cv)
    # cv.waitKey(0)
    # no contrast in there, have to work with colors:
    cargo_yellow = [100, 100, 72, 255]
    if compare_colors(CS_image[y][x + (i * w)], cargo_yellow) < 9:
        return 100
    return 0
def get_capacitor():
    r_ca = - 80
    tmp = 1
    precision = 20
    factor_y = 0.67
    center_x = 800
    center_y = 779
    while tmp < precision + 1:
        angle = np.pi * (1.32 - 0.62 * tmp / precision)
        x = int(center_x + np.cos(angle) * r_ca)
        y = int(center_y + np.sin(angle) * r_ca * factor_y - abs(10 - abs(tmp - precision / 2) / 3) + 2)
        # cv.rectangle(CS_cv, (x, y), (x, y), color=(0, 255, tmp*10), thickness=3, lineType=cv.LINE_4)
        # match 222, no match under worst conditions 90
        if CS_image[y][x][0] < 180:
            return int((tmp - 1) / precision * 100)
        tmp += 1
    # cv.imshow('image', CS_cv)
    # cv.waitKey(0)
    return 100
def show_player_for_confirmation():
    x, y, h, w = 66, 1, 87, 127
    crop_img = CS_cv[y:y + h, x:x + w]
    cv.imshow('tmp', crop_img)
    cv.waitKey()
def farm_tracker(ano):
    # t5med = 653k with frig in end
    fri_six, des_six, cru_six = 19000, 19000, 90000
    fri_five, des_five, cru_five = 15000, 20000, 53000
    # see if there was a site done before and estimate the value gained / time
    global last_farm_site, start_farm_time, last_inventory_value
    if last_farm_site == 0 or interrupted_farming:
        last_farm_site = ano
        start_farm_time = time.time()
        last_inventory_value = get_inventory_value()
        return
    # i should not do it like that because it is just not transparent:
    # updates inventory value and calculates the difference in one line
    inventory_value = abs(last_inventory_value - (last_inventory_value := get_inventory_value()))

    bounty_value = 0
    # ano bounties
    if last_farm_site[1] == 6:
        if last_farm_site[0] == 'large':
            bounty_value += 6 * fri_six + 10 * des_six + 16 * cru_six
        if last_farm_site[0] == 'medium':
            bounty_value += 6 * fri_six + 8 * des_six + 11 * cru_six
        if last_farm_site[0] == 'small':
            bounty_value += 4 * fri_six + 3 * des_six + 3 * cru_six
    if last_farm_site[1] == 5:
        if last_farm_site[0] == 'large':
            bounty_value += 12 * fri_five + 8 * des_five + 10 * cru_five
        if last_farm_site[0] == 'medium':
            bounty_value += 6 * fri_five + 8 * des_five + 11 * cru_five
        if last_farm_site[0] == 'small':
            bounty_value += 4 * fri_five + 3 * des_five + 3 * cru_five

    print('new inventory value:', last_inventory_value)
    print('difference:', inventory_value)
    print('bountys:', bounty_value)
    print((inventory_value + bounty_value)/(time.time() - start_farm_time))

    string = str(last_farm_site[1]) + last_farm_site[0] + '\n' + \
             'Items:\t\t' + str(inventory_value) + '\n' + \
             'Bountys:\t' + str(bounty_value) + '\n' + \
             'Total:\t\t' + str(inventory_value + bounty_value) + '\n' + \
             'Time:\t\t' + str(int(time.time() - start_farm_time)) + '\n' + \
             str(int((inventory_value + bounty_value)/(time.time() - start_farm_time)*3600)) + ' ISK/h\n\n'

    absolutely_professional_database = open('E:\\Eve_Echoes\\Bot\\professional_database.txt', 'a')
    absolutely_professional_database.write(string)
    absolutely_professional_database.close()

    start_farm_time = time.time()
    if ano != 0:
        last_farm_site = ano
def get_inventory_value():
    x, y, w, h = 550, 825, 269, 39

    # open inventory
    click_rectangle(7, 101, 141, 46)
    time.sleep(2)
    update_cs()
    crop_img = CS_cv[y:y + h, x:x + w]
    # cv.imshow('.', crop_img)
    # cv.waitKey()
    raw_text = tess.image_to_string(crop_img).strip()
    raw_text = re.sub('\D', '', raw_text)
    # click on close
    click_circle(1543, 51, 10)
    print('current inventory value: ', int(raw_text))
    return int(raw_text)
def get_autopilot():
    x_a, y_a, x_b, y_b, x_c, y_c = 71, 171, 71, 207, 37, 189
    autopilot_green = [66, 138, 122, 255]
    # check if autopilot is online (2 pixels because safety)
    if compare_colors(CS_image[y_a][x_a], autopilot_green) < 10 and \
            compare_colors(CS_image[y_b][x_b], autopilot_green) < 10:
        # check if autopilot is running (should i just turn it on? nah)
        if compare_colors(CS_image[y_c][x_c], autopilot_green) > 13:
            return 1
    return 0


# INTERFACE HELPER FUNCTIONS
def press_lock_button():
    x, y, w, h = 982, 555, 35, 35
    as_icon = cv.imread('assets\\target_button.png')
    crop_img = CS_cv[y:y + h, x:x + w]
    result = cv.matchTemplate(crop_img, as_icon, cv.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    if max_val > 0.95:
        click_circle(x + w / 2, y + h / 2, 25)
        return 1
    return 0
def warp_to(distance, x, y, w, h):
    # x and y must be the upper left corner of the warp object
    click_rectangle(x, y, w, h)
    swipe_from_circle(x - 173, min(y + 146, 845), 40, distance, 0)
def swap_filter(string_in_name):
    # swaps to a filter containing the given string
    troubleshoot_filter_window()
    update_cs()
    # Filter Header, use the cv.imshow to see if it fits
    x, y, w, h = 1269, 10, 124, 53
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
            click_rectangle(1291, 588, 136, 48)
            return
        else:
            print('todo swap filter')
        swap_filter(string_in_name)
    # cv.imshow('.', crop_img)
    # cv.waitKey()
def activate_module(module):
    if module[1] == 'drone':
        x_off, y_off, w, h = -46, -43, 31, 30
        x, y = module[2] + x_off, module[3] + y_off
        img_target = cv.imread('assets\\drone_target.png')
        crop_img = CS_cv[y:y + h, x:x + w]
        result = cv.matchTemplate(crop_img, img_target, cv.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        print('trying to activate drone')
        if max_val < 0.95:
            print('activating drone')
            if random.random() > 0.5:
                print(0)
                engage_enemy(0)
                return 1
            print(1)
            click_circle(module[2], module[3], module_icon_radius)
        return 1
    activate_blue, activate_red = [206, 253, 240, 255], [194, 131, 129, 255]
    x, y = module[2] + 2, module[3] - 40

    if compare_colors(CS_image[y][x], activate_blue) > 15 and compare_colors(CS_image[y][x], activate_red) > 15:
        click_circle(module[2], module[3], module_icon_radius)
        return 1
    return 0
def deactivate_module(module):
    activate_blue, activate_red = [206, 253, 240, 255], [194, 131, 129, 255]
    x, y = module[2] + 2, module[3] - 40

    if compare_colors(CS_image[y][x], activate_blue) < 15:
        click_circle(module[2], module[3], module_icon_radius)
def repair(desired_hp):
    # todo not tested
    update_hp()
    armor_turn, shield_turn = 0, 0
    if health_ar < desired_hp:
        armor_turn = 1
    if health_sh < desired_hp:
        shield_turn = 1
    for module in ModuleList:
        if module[1] == 'ar_regen':
            if armor_turn:
                activate_module(module)
                print(health_ar)
            else:
                deactivate_module(module)
        if module[1] == 'sh_regen':
            if shield_turn:
                activate_module(module)
            else:
                deactivate_module(module)
def warp_to_random(maximum):
    for i in range(maximum + 1):
        rng = random.random()
        if rng < i / maximum:
            click_rectangle(1210, 67 + 87 * (i - 1), 314, 88)
            click_rectangle(903, 168 + 87 * (i - 1), 301, 91)
            break
def flee(maximus_dist):
    global interrupted_farming
    interrupted_farming = 1
    swap_filter('esc')
    warp_to_random(maximus_dist)
    for module in ModuleList:
        if module[1] == 'esc':
            activate_module(module)
        if module[1] == 'prop':
            deactivate_module(module)
def update_and_checkup_for_combat():
    update_cs()
    update_hp()
    swap_filter('PvE')

    # check hp
    repair(85)

    # players, hull dmg?
    return danger_handling_combat()
def troubleshoot_filter_window():
    x, y = 1539, 504
    # match was about 0.22, no match was 0.64, match = need fix
    if compare_colors(CS_image[504][1539], color_white) < 40:
        click_circle(x, y, 14)
    return
def check_if_in_station():
    print('todo station check')
    return 1


# PLAIN SCRIPTS
def set_and_start_autopilot(target):
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
def orbit_enemy(a):
    x_off = - 100
    click_circle(1118 + a * x_off, 65, module_icon_radius)
    click_rectangle(868 + a * x_off, 319, 308, 96)
def engage_enemy(a):
    # todo: feels like it is not working
    x_off = - 100
    click_circle(1118 + a * x_off, 65, module_icon_radius)
    time.sleep(0.5)
    click_rectangle(870 + a * x_off, 421, 302, 90)
def dump_cargo():
    # open inventory
    click_rectangle(7, 101, 141, 46)
    time.sleep(1.5)
    # select all
    click_rectangle(1169, 763, 120, 107)
    time.sleep(1)
    # move to
    click_rectangle(29, 136, 322, 96)
    time.sleep(0.3)
    # item hangar
    click_rectangle(525, 157, 227, 96)
    time.sleep(5)
    # click on close
    click_circle(1543, 51, 10)
    return 1


# STATES
def go_home():
    # open inventory
    click_rectangle(7, 101, 141, 46)
    time.sleep(1.5)
    # click on assets
    click_rectangle(63, 824, 257, 59)
    time.sleep(2.5)
    # click on station
    click_rectangle(42, 314, 279, 98)
    time.sleep(2)
    # click on set des
    click_rectangle(796, 769, 191, 95)
    time.sleep(0.5)
    # click set des
    click_rectangle(287, 737, 306, 80)
    time.sleep(0.5)
    # click on close
    click_circle(1543, 51, 10)
    click_circle(1543, 51, 10)
    # click on autopilot
    click_circle(38, 191, 15)

    farm_tracker(0)
    if repeat == 0:
        playsound('assets\\sounds\\bell.wav')
        quit()

    wait_end_navigation(30)
    dump_cargo()
    from_station()
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
def wait_for_cap():
    print('waiting for cap')
    for module in ModuleList:
        deactivate_module(module)
    while 1:
        if get_capacitor() > 60:
            return
        troubleshoot_filter_window()
        if get_player_thread():
            for i in range(3):
                flee(4)
                print('player detected')
            playsound('assets\\sounds\\bell.wav')
            wait_warp()
            warp_to_ano()
            combat()
            return 1
        repair(100)
        time.sleep(3)
def work_on_container():
    waiting_time = 10
    click_rectangle(1210, 67, 314, 88)
    click_rectangle(903, 168, 301, 91)
    while 1:
        for i in range(waiting_time):
            update_cs()
            time.sleep(0.1)
            if CS_image[772][600][1] > 85:
                count = 0
                while 1:
                    click_rectangle(454, 748, 261, 67)
                    update_cs()
                    if CS_image[772][600][1] < 85:
                        break
                    if count > 20:
                        playsound('assets\\sounds\\bell.wav')
                    count += 1
                    break
                return 0
            if danger_handling_farming() == 1:
                return 1
            time.sleep(0.9)
        waiting_time *= 2
        print('increased waiting time to', waiting_time)
        if waiting_time > 20:
            return 0
        repair(100)
        if get_speed() == 0:
            click_circle(590, 754, 25)
def loot():
    print('looting')
    # swap to container view

    # turn on prop module
    for module in ModuleList:
        if module[1] == 'prop':
            print('activating prop')
            activate_module(module)

    swap_filter('PvE')
    # scroll up
    swipe_from_circle(1406, 132, 20, 110, 1)

    # find and click wreck icon in filter bar
    x, y, w, h = 1547, 86, 18, 445
    wreck_icon = cv.imread('assets\\wreck.png')
    crop_img = CS_cv[y:y + h, x:x + w]
    result = cv.matchTemplate(crop_img, wreck_icon, cv.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    if max_val > 0.95:
        click_circle(max_loc[0] + x + 5, max_loc[1] + y + 7, 15)
        while 1:

            # behavior
            update_cs()
            repair(100)
            danger_handling_farming()
            if get_npc_count():
                combat()
                return

            if get_cargo() > 95:
                print('cargo full')
                go_home()
                return

            # still containers left?
            crop_img = CS_cv[y:y + h, x:x + w]
            result = cv.matchTemplate(crop_img, wreck_icon, cv.TM_CCORR_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
            if max_val > 0.95:
                if work_on_container():
                    return
            else:
                break
    print('site done')
    warp_to_ano()
    combat()
    return
def combat():
    print('combat')
    tmp_lock = time.time()
    tmp_weapon = time.time()
    tmp_situational = time.time()
    last_npc_count = 0

    orbit_enemy(0)
    # maybe i shouldnt directly engage a potential enemy? it saves me like 6 secs every
    # fight but seems akward, orbit is okay
    engage_enemy(0)

    while 1:
        print('combat cycle')
        if update_and_checkup_for_combat() == 1:
            return
        troubleshoot_filter_window()
        current_npc_count = get_npc_count()
        print(0)
        # update targets
        # todo: lock closer targets
        if time.time() - tmp_lock > 0:
            if press_lock_button():
                tmp_lock = time.time() + 7
                tmp_weapon = time.time() + 10

        # no enemies
        if not current_npc_count:
            time.sleep(2)
            update_cs()
            if not current_npc_count:
                loot()
                return
        if update_and_checkup_for_combat() == 1:
            return
        print(2)
        # check if weapons are online
        if time.time() - tmp_weapon > 0:
            for module in ModuleList:
                if module[1] == 'drone':
                    # or weapon
                    if activate_module(module):
                        print('activating drone successful')
                        # this orbit call should not be necessary, but sometimes it somehow misses orbit
                        orbit_enemy(0)
                        tmp_weapon = time.time() + 10

        print(3)
        # activate standard modules, behavior
        if current_npc_count != last_npc_count:
            orbit_enemy(0)
            engage_enemy(0)
            last_npc_count = current_npc_count
            # todo react to close enemys, nos, web, etc
        for module in ModuleList:
            if module[1] == 'prop':
                activate_module(module)

        # activate dmg amplifiers, nos, web
        if time.time() - tmp_situational > 90:
            tmp_situational = time.time()
            for module in ModuleList:
                if module[1] == 'situational':
                    activate_module(module)
def solve_scouts():
    playsound('assets\\sounds\\bell.wav')
    print('todo: solve_scouts')
    quit()


# STARTS
def from_station():
    show_player_for_confirmation()
    set_and_start_autopilot(planet)
    wait_end_navigation(6)
    calibrate()
    warp_to_ano()
    combat()
def from_ano():
    calibrate()
    for module in ModuleList:
        print(module)
    show_player_for_confirmation()
    combat()
def from_system():
    calibrate()
    for module in ModuleList:
        print(module)
    show_player_for_confirmation()
    warp_to_ano()
    combat()
def custom():
    # wait_end_navigation(6)
    calibrate()
    loot()


show_player_for_confirmation()
from_system()

