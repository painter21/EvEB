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


read_config_file()
config_uni()
main()
