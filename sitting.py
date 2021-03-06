# only works on 960x540

from universal_small_res import *

Path_to_script = ''
def read_config_file():
    file = open('config.txt')
    tmp = file.readline().strip()
    while tmp != '':
        tmp = str(tmp).split()
        if tmp[0] == 'path':
            set_path(tmp[1])
        if tmp[0] == 'path_to_script':
            global Path_to_script
            Path_to_script = tmp[1]
            set_path_to_script(Path_to_script)
        tmp = file.readline()
    print('\tmining_from_station()')

def main():
    while 1:
        device_update_cs()
        if get_filter_icon('all_ships') or get_criminal():
            ding_when_ganked()
            save_screenshot()
            time.sleep(20)
        time.sleep(3)

def bubble():
    while 1:
        device_click_circle(920, 430, 10)
        time.sleep(32)
        device_click_circle(920, 430, 10)
        time.sleep(47)

def scouting():
    while 1:
        device_update_cs()
        if get_filter_icon('cruiser') or get_filter_icon('battlecruiser') or get_filter_icon('industrial'):
            ding_when_ganked()
            save_screenshot()
            time.sleep(10)
            '''save_screenshot()
            time.sleep(2)
            save_screenshot()'''
        time.sleep(0.5)

def just_rep():
    update_modules()

    while 1:
        repair(80)
        if get_cap() < 20:
            ding_when_ganked()
        if get_hp()[0] < 30:
            ding_when_ganked()
            time.sleep(4)
        if get_tar_cross():
            click_tar_cross_location()
        device_update_cs()

read_config_file()
config_uni()

if get_start() == 'main':
    main()
if get_start() == 'bubble':
    bubble()
if get_start() == 'scouting':
    scouting()
if get_start() == 'rep':
    just_rep()
