# only works on 16000x900

from ppadb.client import Client
import time
import numpy as np
import cv2 as cv
import pytesseract as tess
from numpy import random
from PIL import Image
from playsound import playsound
import string

tess.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'

# will be updated automatically -> calibrate()
health_st = 100
health_ar = 100
health_sh = 100
preferredOrbit = 23
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
    angle = np.random.default_rng().random() * np.pi
    r = 130 + d*2.4
    device.shell(f'input touchscreen swipe {x} {y} {np.cos(angle) * r + x} {np.sin(angle) * r + y} 1000')
    power_nap()


def click_rectangle(x, y, w, h):
    x = w * np.random.default_rng().random() + x
    y = h * np.random.default_rng().random() + y
    device.shell(f'input touchscreen tap {x} {y}')
    power_nap()


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


def swap_filter(string_in_name):
    # swaps to a filter containing the given string
    update_cs()
    # Filter Header, use the cv.imshow to see if it fits
    x, y, w, h = 1269, 10, 124, 53
    crop_img = CS_image[y:y + h, x:x + w]
    if string_in_name not in tess.image_to_string(crop_img):
        # TODO: improve
        click_rectangle(x, y, w, h)
        click_rectangle(x, 118, w, h)
        swap_filter(string_in_name)
    # cv.imshow('.', crop_img)
    # cv.waitKey()


def warp_to(distance, x, y, w, h):
    # x and y must be the upper left corner of the warp object
    click_rectangle(x, y, w, h)
    drag_from_circle(x - 173, y + 146, 40, distance)


def get_good_anomaly():
    # click filter element to expand filter
    click_rectangle(1214, 247, 308, 249)
    list_ano = []

    update_cs()

    # create a list of all anomaly locations (on screen)
    x, y, w, h = 1210, 0, 30, 900
    img_ano = cv.imread('icons\\Ano.png')
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
        if 'Scout' in raw_text or 'Inquis' in raw_text:
            list_ano = []
            return list_ano.append(['scout', 0, x_ano_field, y_ano_field, 310, 80])
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


def combat():
    print('todo')


def warp_to_ano():
    swap_filter('Ano')
    anomaly = get_good_anomaly()
    if anomaly[0] == 'scout':
        playsound('alarm.wav')
        warp_to(0, anomaly[2], anomaly[3], anomaly[4], anomaly[5])
    warp_to(preferredOrbit, anomaly[2], anomaly[3], anomaly[4], anomaly[5])
    time.sleep(10)
    wait_warp()

    # swap to PvE


def main():
    while 1:
        warp_to_ano()
        combat()



main()

# CS = Image.open('screen.png')
# CS = numpy.array(CS, dtype=numpy.uint8)
