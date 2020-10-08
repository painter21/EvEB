# only works on 960x540

from numpy import random
from universal_small_res import *

last_farm_site, start_farm_time, last_inventory_value = '', time.time(), 0
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
            Path_to_script = (tmp[1])
            set_path_to_script(Path_to_script)
        tmp = file.readline()

# INTERNAL
def farm_tracker(ano):
    # t5med = 653k with frig in end
    fri_six, des_six, cru_six = 19000, 19000, 90000
    fri_five, des_five, cru_five = 15000, 20000, 53000
    # see if there was a site done before and estimate the value gained / time
    global last_farm_site, start_farm_time, last_inventory_value
    if last_farm_site == 0 or interrupted_farming:
        last_farm_site = ano
        start_farm_time = time.time()
        last_inventory_value = get_inventory_value_small_screen(0)
        return
    # i should not do it like that because it is just not transparent:
    # updates inventory value and calculates the difference in one line
    inventory_value = abs(last_inventory_value - (last_inventory_value := get_inventory_value_small_screen(0)))

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
def choose_anomaly():
    # todo
    ano_list = get_list_anomaly()
    file = open('ano_pref.txt')
    tmp = file.readline().strip
    while tmp != '':
        for ano in ano_list:
            if ano[0] == tmp:
                return ano
        tmp = file.readline().strip
    # todo: should swap system
    return ano[0]

# TASKS
def get_npc_count():
    # todo: test for 10+ enemys
    set_filter('PvE')
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
def flee(maximus_dist):
    set_filter('esc')
    warp_randomly(maximus_dist, 1)
    for module in ModuleList:
        if module[1] == 'esc':
            activate_module(module)
        if module[1] == 'prop':
            deactivate_module(module)
def get_list_anomaly():
    set_filter('Ano')
    # todo: so much todo
    # click filter element to expand filter
    device_click_filter_block()
    list_ano = []

    device_update_cs()

    # create a list of all anomaly locations (on screen)
    x, y, w, h = 729, 51, 14, 475
    img_ano = cv.imread('assets\\filter_icons\\ano_left.png')
    crop_img = CS_cv[y:y + h, x:x + w]
    image_remove_dark(crop_img, 75)
    # show_image(crop_img)
    result = cv.matchTemplate(crop_img, img_ano, cv.TM_CCORR_NORMED)
    threshold = 0.90
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
                y_text, x_text = pt[1] - 12, pt[0] + 65 + x
                crop_img = CS_cv[y_text:y_text + 40, x_text:x_text + 120]

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
def wait_and_watch_out(sec):
    for i in range(int(sec/2)):
        device_update_cs()
        if get_filter_icon('all_ships') != 0:
            if get_bait() == 1:
                subprocess.call(["D:\Program Files\AutoHotkey\AutoHotkey.exe",
                                 "E:\\Eve_Echoes\\Bot\\ahk_scripts\\call_paul.ahk"])
                playsound(Path_to_script + 'assets\\sounds\\bell.wav')
                print('trap card activated')
                device_toggle_eco_mode()
                time.sleep(3)
                combat_return(1)
                quit()
            device_toggle_eco_mode()
            print('ganked')
            combat_return(1)
            quit()
        time.sleep(2)
def wait_for_cap():
    activate_filter_window()
    print('waiting for cap')
    for module in ModuleList:
        deactivate_module(module)
    while 1:
        if get_cap() > 60:
            return
        wait_and_watch_out(4)
def work_on_container():
    waiting_time = 10
    device_click_rectangle(1210, 67, 314, 88)
    device_click_rectangle(903, 168, 301, 91)
    while 1:
        for i in range(waiting_time):
            device_update_cs()
            time.sleep(0.1)
            if CS_image[772][600][1] > 85:
                count = 0
                while 1:
                    device_click_rectangle(454, 748, 261, 67)
                    device_update_cs()
                    if CS_image[772][600][1] < 85:
                        break
                    if count > 20:
                        playsound('assets\\sounds\\bell.wav')
                    count += 1
                    break
                return 0
            # if danger_handling_farming() == 1:
            #    return 1
            time.sleep(0.9)
        waiting_time *= 2
        print('increased waiting time to', waiting_time)
        if waiting_time > 20:
            return 0
        repair(100)
        if get_speed() == 0:
            device_click_circle(590, 754, 25)
def warp_to_ano():
    set_filter('Ano')
    anomaly = choose_anomaly()
    print()
    print(anomaly)
    # sometimes the interface times out and i have to reopen it
    device_click_filter_block()
    warp_to(preferredOrbit, anomaly[2], anomaly[3], anomaly[4], anomaly[5])
    time.sleep(3)
    farm_tracker(anomaly)
    time.sleep(7)
    wait_warp()

    # swap to PvE
def update_and_checkup_for_combat():
    device_update_cs()
    set_filter('PvE')

    # check hp
    repair(85)

    # players, hull dmg?
    return danger_handling_combat()
def danger_handling_combat():
    if get_hp()[2] < 90:
        print('hull critical')
        combat_return(0)
        quit()
    if get_cap() < 10:
        print('capacitor critical')
        for i in range(3):
            flee(1)
        wait_for_cap()
        warp_to_ano()
        combat()
        return 1
    if get_filter_icon('all_ships.png'):
        print('player detected')
        for i in range(3):
            combat_return(1)
        wait_warp()
        warp_to_ano()
        combat()
        return 1
    return 0
def danger_handling_farming():
    if get_filter_icon('all_ships.png'):
        print('player detected')
        for i in range(3):
            flee(4)
        wait_warp()
        warp_to_ano()
        combat()
        return 1
    return 0


# STATES
def combat_start_from_station():
    undock_and_modules()
    set_pi_planet_for_autopilot()
    activate_autopilot()
    wait_end_navigation()
    warp_to_ano()
    combat()
def combat_start_from_system():
    update_modules()
    warp_to_ano()
    combat()

def combat_from_system():
    return
def loot():
    print('looting')
    # swap to container view

    # turn on prop module
    for module in ModuleList:
        if module[1] == 'prop':
            print('activating prop')
            activate_module(module)

    set_filter('PvE')
    # scroll up
    device_swipe_from_circle(1406, 132, 20, 110, 1)

    # find and click wreck icon in filter bar
    x, y, w, h = 1547, 86, 18, 445
    wreck_icon = cv.imread('assets\\wreck.png')
    crop_img = CS_cv[y:y + h, x:x + w]
    result = cv.matchTemplate(crop_img, wreck_icon, cv.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    if max_val > 0.95:
        device_click_circle(max_loc[0] + x + 5, max_loc[1] + y + 7, 15)
        while 1:

            # behavior
            device_update_cs()
            repair(100)
            danger_handling_farming()
            if get_npc_count():
                combat()
                return

            if get_cargo() > 95:
                print('cargo full')
                combat_return(0)
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

    # maybe i shouldnt directly engage a potential enemy? it saves me like 6 secs every
    # fight but seems akward, orbit is okay
    target_action(1, 4)

    while 1:
        print('combat cycle')
        if update_and_checkup_for_combat() == 1:
            return
        activate_filter_window()
        current_npc_count = get_npc_count()
        print(0)
        # update targets
        # todo: lock closer targets
        if time.time() - tmp_lock > 0:
            if 1:
                # press_lock_button():
                tmp_lock = time.time() + 7
                tmp_weapon = time.time() + 10

        # no enemies
        if not current_npc_count:
            time.sleep(2)
            device_update_cs()
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
                        tmp_weapon = time.time() + 10

        print(3)
        # activate standard modules, behavior
        if current_npc_count != last_npc_count:
            target_action(1, 4)
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
def combat_return(get_ganked):
    return

# STARTS
def main():
    interface_show_player()
    combat_start_from_station()
def custom():
    print('hi')

read_config_file()
read_config_file_uni()
if get_start() == 'main':
    main()
if get_start() == 'custom':
    custom()
