# only works on 16000x900

from ppadb.client import Client
import time
import numpy as np
import cv2 as cv
import pytesseract as tess
from numpy import random
from PIL import Image

tess.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'
health_st = 100
health_ar = 100
health_sh = 100
ModuleList = [None]

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


def update_cs():
    global CS_cv, CS, CS_image
    CS = device.screencap()
    with open('screen.png', 'wb') as f:
        f.write(CS)
    CS_cv = cv.imread('screen.png')
    CS_image = Image.open('screen.png')
    CS_image = np.array(CS_image, dtype=np.uint8)


def calibrate():
    # improve listing different modules (by available images?)

    ar = cv.imread('Modules\ArmorRepairModule2.png')

    result = cv.matchTemplate(CS, ar, cv.TM_CCORR_NORMED)

    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    print('Best match armor rep: %s' % str(max_loc))
    print('best match confidence: %s' % max_val)


def click_circle(x, y, r):
    a = 3.  # shape
    angle = np.random.default_rng().random() * np.pi
    r = r - np.random.default_rng().power(a) * r
    device.shell(f'input touchscreen tap {np.cos(angle) * r + x} {np.sin(angle) * r + y}')

    # great display:
    # https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.power.html#numpy.random.Generator.power


def update_hp_helper(r, off, offset):
    tmp = 0
    stop = 0
    precision = 20
    factor_y = 0.67
    center_x = 800
    center_y = 779
    while tmp < precision and not stop:
        angle = np.pi * (1.32 - 0.62 * tmp / precision)
        x = int(center_x + np.cos(angle) * r)
        y = int(center_y + np.sin(angle) * r * factor_y - abs(10-abs(tmp-precision/2))/3 * off + offset)
        # cv.rectangle(CS_cv, (x, y), (x, y), color=(0, 255, tmp*10), thickness=3, lineType=cv.LINE_4)
        if CS_image[y][x][2] > 90:
            print(int(100 - tmp / precision * 100))
            stop = 1
        tmp += 1
    if not stop:
        print('0')


def update_hp():
    r_st = 64
    r_ar = 80
    r_sh = 98
    update_hp_helper(r_st, 1/2, -2)
    update_hp_helper(r_ar, 1, 0)
    update_hp_helper(r_sh, 1/3, 0)
    # cv.imshow('image', CS_cv)
    # cv.waitKey(0)


def main():
    while 1:
       update_cs()
       update_hp()
       print('----------')
       time.sleep(0.5)
    # cropping
    # whole anos area crop_img = CSp[85:840, 1321:1524]
    y = 847
    h = 26
    x = 710
    w = 172
    # crop_img = CSp[y:y + h, x:x + w]

    # print(tess.image_to_string(crop_img))
    # cv.imshow('.', crop_img)
    # cv.waitKey()


main()

# CS = Image.open('screen.png')
# CS = numpy.array(CS, dtype=numpy.uint8)
