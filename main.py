# only works on 16000x900

from ppadb.client import Client
import time
import numpy as np
import cv2 as cv
import pytesseract as tess
from numpy import random
from PIL import Image
from playsound import playsound

tess.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'

# will be updated automatically -> calibrate()
health_st = 100
health_ar = 100
health_sh = 100
preferredOrbit = 23
module_icon_radius = 40
ModuleList = []

# INIT
# connect to Bluestacks
adb = Client(host='127.0.0.1', port=5037)
devices = adb.devices()
if len(devices) == 0:
    print('no device attached')
    quit()
# CS = current Screenshot
device = devices[0]
CS = device.screencap()
with open('screen.png', 'wb') as f:
    f.write(CS)
CS_cv = cv.imread('screen.png')
CS_image = Image.open('screen.png')
CS_image = np.array(CS_image, dtype=np.uint8)

# BASIC FUNCTIONS
def power_nap():
    time.sleep(np.random.default_rng().random() * 0.1 + 0.2)
def update_cs():
    global CS_cv, CS, CS_image
    CS = device.screencap()
    with open('screen.png', 'wb') as f:
        f.write(CS)
    CS_cv = cv.imread('screen.png')
    CS_image = Image.open('screen.png')
    CS_image = np.array(CS_image, dtype=np.uint8)
def compare_colors(a, b):
    return (abs(a[0]-b[0])+abs(a[1]-b[1])+abs(a[2]-b[2])+abs(a[3]-b[3]))/255/4
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
def drag_from_circle(x, y, r, d):
    tmp = get_point_in_circle(x, y, r)
    x, y = tmp[0], tmp[1]
    if d == 0:
        device.shell(f'input touchscreen tap {x} {y}')
    angle = np.random.default_rng().random() * np.pi
    r = 130 + d*2.4
    device.shell(f'input touchscreen swipe {x} {y} {np.cos(angle) * r + x} {np.sin(angle) * r + y} 1000')
    power_nap()
def click_rectangle(x, y, w, h):
    x = w * np.random.default_rng().random() + x
    y = h * np.random.default_rng().random() + y
    device.shell(f'input touchscreen tap {x} {y}')
    power_nap()

# HELPER FUNCTIONS
def calibrate():
    file = open('modules\_pos.txt')
    tmp = file.readline()
    while tmp != '':
        tmp = tmp.split()
        ar = cv.imread('modules\\' + tmp[0] + '.png')
        result = cv.matchTemplate(CS_cv, ar, cv.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        if max_val > 0.99:
            center = (max_loc[0] + int(tmp[2]), max_loc[1] + int(tmp[3]))
            ModuleList.append([tmp[0], tmp[1], center[0], center[1]])
            # cv.circle(CS_cv, center, 40, color=(0, 255, 0), thickness=2, lineType=cv.LINE_4)
        else:
            print(tmp[0] + ' not found: ')
            print(max_val)
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
def activate_module(module):
    if module[1] == 'drone':
        x_off, y_off, w, h = -46, -43, 31, 30
        x, y = module[2] + x_off, module[3] + y_off
        img_target = cv.imread('assets\\drone_target.png')
        crop_img = CS_cv[y:y + h, x:x + w]
        result = cv.matchTemplate(crop_img, img_target, cv.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        if max_val < 0.95:
            if random.random() > 0.5:
                engage_enemy(0)
                return 1
            click_circle(module[2], module[3], module_icon_radius)
        return 1
    activate_blue, activate_red = [206, 253, 240, 255], [194, 131, 129, 255]
    x, y = module[2] + 2, module[3] - 40

    if compare_colors(CS_image[y][x], activate_blue) > 0.15 and compare_colors(CS_image[y][x], activate_red) > 0.15:
        click_circle(module[2], module[3], module_icon_radius)
        return 1
    return 0
def deactivate_module(module):
    activate_blue, activate_red = [206, 253, 240, 255], [194, 131, 129, 255]
    x, y = module[2] + 2, module[3] - 40

    if compare_colors(CS_image[y][x], activate_blue) < 0.15:
        click_circle(module[2], module[3], module_icon_radius)
def swap_filter(string_in_name):
    # swaps to a filter containing the given string
    update_cs()
    # Filter Header, use the cv.imshow to see if it fits
    x, y, w, h = 1269, 10, 124, 53
    crop_img = CS_image[y:y + h, x:x + w]
    if string_in_name not in tess.image_to_string(crop_img):
        # TODO: improve
        click_rectangle(x, y, w, h)
        if string_in_name in 'Anomalies':
            click_rectangle(x, 118, w, h)
        if string_in_name in 'PvE':
            click_rectangle(x, 206, w, h)
        else:
            print('todo swap filter')
        swap_filter(string_in_name)
    # cv.imshow('.', crop_img)
    # cv.waitKey()
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
def warp_to(distance, x, y, w, h):
    # x and y must be the upper left corner of the warp object
    click_rectangle(x, y, w, h)
    drag_from_circle(x - 173, y + 146, 40, distance)
def get_good_anomaly():
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
    threshold = 0.95
    loc = np.where(result >= threshold)

    # black magic do not touch
    for pt in zip(*loc[::-1]):
        # icon offset, size of text field
        y_text, x_text = pt[1] - 13, pt[0] + 107 + x
        crop_img = CS_cv[y_text:y_text + 52, x_text:x_text + 204]
        raw_text = tess.image_to_string(crop_img)

        # Todo: i should improve that at some point
        x_ano_field, y_ano_field = pt[0] + x, pt[1] - 28
        if 'Scout' in raw_text or 'nquis' in raw_text:
            playsound('bell.wav')
            return ['scout', 0, x_ano_field, y_ano_field, 310, 80]
        else:
            if 'Small' in raw_text:
                list_ano.append(['small', 0, x_ano_field, y_ano_field, 310, 80])
            else:
                if 'Medium' in raw_text:
                    list_ano.append(['medium', 0, x_ano_field, y_ano_field, 310, 80])
                    if 'Large' in raw_text:
                        list_ano.append(['large', 0, x_ano_field, y_ano_field, 310, 80])
                        # if 'Base' in raw_text:
                        #    list_ano.append(['base', 0, pt[0], pt[1] - 28, pt[0] + 310, pt[1] + 53])
        # icon cv.rectangle(crop_img, pt, (pt[0] + 15, pt[1] + 15), (0, 0, 255), 2)
        # text field cv.rectangle(CS_cv, (x_text, y_text), (x_text + 204, y_text + 52), (0, 0, 255), 2)
    # cv.imshow('.', CS_cv)
    # cv.waitKey()
    if len(list_ano) > 1:
        return list_ano[1]
    return list_ano[0]
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
        # cv.rectangle(CS_cv, (x, y), (x, y), color=(0, 255, tmp*10), thickness=3, lineType=cv.LINE_4)
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
def get_cargo():
    print('todo cargocheck')
def repair():
    # todo not tested
    update_hp()
    armor_turn, shield_turn = 0, 0
    if health_ar < 70:
        armor_turn = 1
    if health_sh < 70:
        shield_turn = 1
    for module in ModuleList:
        if module[1] == 'ar_regen':
            if armor_turn:
                activate_module(module)
            else:
                deactivate_module(module)
        if module[1] == 'sh_regen':
            if shield_turn:
                activate_module(module)
            else:
                deactivate_module(module)
def not_safe():
    if health_st < 70:
        flee()
        go_home()
        return 1
    # if get_player_thread():
    #    flee()
    #    return 1
    return 0
def npc_enemies_count():
    #todo: test for 10+ enemys
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
        import re
        raw_text = re.sub('\D', '', raw_text)
        tmp = 0
        if int(len(raw_text)) == 0:
            print('npc_enemy_count: guessed 2')
            return 2
        while tmp < int(len(raw_text)/2):
            raw_text = raw_text[:-1]
            tmp += 1
        return int(raw_text)
    return 0
def press_lock_button():
    x, y, w, h = 982, 555, 35, 35
    as_icon = cv.imread('assets\\target_button.png')
    crop_img = CS_cv[y:y + h, x:x + w]
    result = cv.matchTemplate(crop_img, as_icon, cv.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    if max_val > 0.95:
        click_circle(x + w/2, y + h/2, 25)
        return 1
    return 0
def orbit_enemy(a):
    x_off = - 100
    click_circle(1118 + a * x_off, 65, module_icon_radius)
    click_rectangle(868 + a * x_off, 319, 308, 96)
def engage_enemy(a):
    x_off = - 100
    click_circle(1118 + a * x_off, 65, module_icon_radius)
    click_rectangle(868 + a * x_off, 416, 308, 96)

# STATE FUNCTIONS
def loot():
    if npc_enemies_count():
        combat()
    print('site done')
    warp_to_ano()
    combat()
    print('todo loot()')
    # playsound('bell.wav')


def flee():
    print('todo flee')


def go_home():
    print('todo go_home')


def combat():
    print('start combat')
    tmp_lock = time.time()
    tmp_weapon = time.time()
    last_npc_count = 0
    while 1:
        update_cs()
        update_hp()

        # players, hull dmg?
        not_safe()
        swap_filter('PvE')

        # check hp
        repair()

        current_npc_count = npc_enemies_count()
        # no enemies
        if not current_npc_count:
            loot()
            return
        else:
            # update targets
            # todo: lock closer targets
            if time.time() - tmp_lock > 0:
                if press_lock_button():
                    tmp_lock = time.time() + 7
                    tmp_weapon = time.time() + 10
            # check if weapons are online
            if time.time() - tmp_weapon > 0:
                for module in ModuleList:
                    if module[1] == 'drone':
                        # or weapon
                        if activate_module(module):
                            tmp_weapon = time.time() + 10



        # activate standard modules, behavior
        if current_npc_count != last_npc_count:
            orbit_enemy(0)
            last_npc_count = current_npc_count
            #todo react to close enemys, nos, web, etc
        # for module in ModuleList:
        #    if module[1] == 'ifpossible':
        #        activate_module(module)

        # update movement
        # no enemys left? loot


def warp_to_ano():
    swap_filter('Ano')
    anomaly = get_good_anomaly()
    if anomaly == 'scout':
        playsound('alarm.wav')
        warp_to(0, anomaly[2], anomaly[3], anomaly[4], anomaly[5])
    warp_to(preferredOrbit, anomaly[2], anomaly[3], anomaly[4], anomaly[5])
    time.sleep(10)
    wait_warp()

    # swap to PvE


def main():
    engage_enemy(2)
    calibrate()
    combat()


main()

# CS = Image.open('screen.png')
# CS = numpy.array(CS, dtype=numpy.uint8)
