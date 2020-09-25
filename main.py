# only works on 16000x900

import sys
from ppadb.client import Client
from PIL import Image
import numpy as np
from playsound import playsound
import time
import cv2 as cv
import pytesseract as tess
from numpy import random

tess.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'


def calibrate():
    # improve listing different modules (by avaidable images?)

    ar = cv.imread('Modules\ArmorRepairModule2.png')

    result = cv.matchTemplate(CS, ar, cv.TM_CCORR_NORMED)

    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    print('Best match armor rep: %s' % str(max_loc))
    print('best match confidence: %s' % max_val)

    cv.waitKey()


def clickCircle(x, y, r):
    angle = np.random.default_rng().random()*np.pi
    angle = np.random.default_rng().random() * np.pi
    a = 3.  # shape
    r = r - np.random.default_rng().power(a) * r
    print(np.cos(angle) * r + x)
    print(np.sin(angle) * r + y)

    # super Darstellung: https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.power.html#numpy.random.Generator.power
    # print(1 - random.default_rng().power(1.5, 10))
    # device.shell(f'input touchscreen swipe 1000 202 999 750 300')


def main():
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
    CS = cv.imread('screen.png')
    CSp = cv.cvtColor(CS, cv.COLOR_BGR2RGB)

    # cropping
    # whole anos area crop_img = CSp[85:840, 1321:1524]
    y = 847
    h = 26
    x = 710
    w = 172
    crop_img = CSp[y:y + h, x:x + w]

    print(tess.image_to_string(crop_img))
    # cv.imshow('.', crop_img)
    # cv.waitKey()


clickCircle(100, 100, 100)

# CS = Image.open('screen.png')
# CS = numpy.array(CS, dtype=numpy.uint8)
