# only works on 16000x900

import sys
from ppadb.client import Client
from PIL import Image
import numpy
from playsound import playsound
import time
import cv2 as cv

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


def calibrate():
    #improve listing different modules (by avaidable images?)

    ar = cv.imread('Modules\ArmorRepairModule.png')

    result = cv.matchTemplate(CS, ar, cv.TM_CCOEFF_NORMED)

    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    print('Best match armor rep: %s' % str(max_loc))
    print('best match confidence: %s' % max_val)

    cv.waitKey()



calibrate()

# CS = Image.open('screen.png')
# CS = numpy.array(CS, dtype=numpy.uint8)
