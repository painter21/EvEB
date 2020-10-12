# only works on 960x540

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
            Path_to_script = tmp[1]
            set_path_to_script(Path_to_script)
        tmp = file.readline()

if 1:
    last_npc_icon_x, last_npc_icon_y = 0, 0

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
    base_level = 0
    ano_list = get_list_anomaly()
    new_ano_list = []
    for ano in ano_list:
        if ano[0] == 'base':
            base_level = ano[0]
        else:
            new_ano_list.append(ano)
    file = open('ano_pref.txt')
    tmp = file.readline()
    while tmp != '':
        tmp = str(tmp).split()
        for ano in new_ano_list:
            if ano[0] == tmp[1] and str(ano[1]) == tmp[0]:
                return ano
        tmp = file.readline()
    # todo: should swap system
    return ano_list[0]
def get_npc_icon_current_loc():
    w = 5
    for off in range(3):
        pix_not_red = 0
        for i in range(w):
            if get_cs_cv()[last_npc_icon_y + off - 1][last_npc_icon_x + i][0] < 110 or \
                    get_cs_cv()[last_npc_icon_y + off - 1][last_npc_icon_x + i][1] > 50 or \
                    get_cs_cv()[last_npc_icon_y + off - 1][last_npc_icon_x + i][2] > 70:
                pix_not_red += 1
        if pix_not_red < 1:
            return 1
    return 0
def get_npc_count():
    # only returns 0,1 correctly, more = 2

    # updates the location, if needed
    global last_npc_icon_x, last_npc_icon_y
    if get_npc_icon_current_loc() == 0:
        tmp = get_filter_icon('npc')
        if tmp == 0:
            return 0
        else:
            last_npc_icon_x, last_npc_icon_y = tmp

    # check for 1 enemy
    h, x_off, y_off = 9, 13, 7
    pix_not_right = 0
    for i in range(h):
        if int(get_cs_cv()[last_npc_icon_y + i + y_off][last_npc_icon_x + x_off][0]) + \
                get_cs_cv()[last_npc_icon_y + i + y_off][last_npc_icon_x + x_off][1] + \
                get_cs_cv()[last_npc_icon_y + i + y_off][last_npc_icon_x + x_off][2] < 400:
            pix_not_right += 1
    if pix_not_right < 3:
        return 1
    return 2


# TASKS
def warp_and_hide(maximus_dist):
    # todo
    set_filter('esc')
    warp_randomly(maximus_dist, 1)
    for module in ModuleList:
        if module[1] == 'esc':
            activate_module(module)
        if module[1] == 'prop':
            deactivate_module(module)
def get_list_anomaly():
    # todo: it is way too inaccurate
    # click filter element to expand filter

    #filter swap should not be nessessary, only warp to ano calls it anyways
    time.sleep(0.5)
    device_update_cs()
    list_ano = []


    # create a list of all anomaly locations (on screen)
    x, y, w, h = 729, 51, 14, 475
    img_ano = cv.imread(Path_to_script + 'assets\\filter_icons\\ano_left.png')

    # show_image(img_ano, 1)
    crop_img = get_cs_cv()[y:y + h, x:x + w]
    crop_img = image_remove_dark(crop_img, 175)
    # show_image(crop_img, 1)
    result = cv.matchTemplate(crop_img, img_ano, cv.TM_CCORR_NORMED)
    threshold = 0.8
    loc = np.where(result >= threshold)
    # black magic do not touch
    previous_point_y = -10
    for pt in zip(*loc[::-1]):
        # ignore double results
        if pt[1] > previous_point_y + 10:
            previous_point_y = pt[1]
            # add_rectangle(pt[0] + x, pt[1] + y, 0, 0)

            # icon offset, size of text field
            y_text, x_text = pt[1] - 12 + y, pt[0] + 65 + x
            filter_list_nr = int((y_text - 40)/52)
            if filter_list_nr > 0:
                text_img = get_cs_cv()[y_text:y_text + 40, x_text:x_text + 120]
                text_img = image_remove_dark(text_img, 200)
                raw_text = tess.image_to_string(text_img)
                # show_image(text_img, 1)
                icon_img = text_img[5:15, 0:7]
                # template gen
                # remove darker pixels, seems to be a bad idea
                # cv.imwrite('test.png', icon_img)

                highest_result = 0
                lvl = 0
                for file in os.listdir(Path_to_script + 'assets\\base_level\\small\\'):
                    lvl_icon = cv.imread(Path_to_script + 'assets\\base_level\\small\\' + file)
                    result = cv.matchTemplate(icon_img, lvl_icon, cv.TM_CCORR_NORMED)
                    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
                    if highest_result < max_val:
                        highest_result = max_val
                        lvl = int(file[:-4])
                # print(lvl, raw_text.strip())
                # show_image(icon_img, 1)

                if 'Scout' in raw_text or 'nquis' in raw_text:
                    print('found scout')
                    playsound(Path_to_script + 'assets\\sounds\\bell.wav')
                    device_click_filter_block()
                    save_screenshot()
                else:
                    if 'mall' in raw_text:
                        list_ano.append(['small', lvl, filter_list_nr])
                    else:
                        if 'edium' in raw_text:
                            list_ano.append(['medium', lvl, filter_list_nr])
                        else:
                            if 'arge' in raw_text:
                                list_ano.append(['large', lvl, filter_list_nr])
                            else:
                                if 'Bas' in raw_text:
                                    list_ano.append(['base', lvl, filter_list_nr])
                                else:
                                    list_ano.append(['unknown', lvl, filter_list_nr])
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
    loot_green = [48, 94, 87]
    waiting_time = time.time()
    filter_action(1, 2, 5)
    x, y = 362, 457
    checkpoint = 0
    while time.time() < waiting_time + 50:
        device_update_cs()
        danger_handling_farming()
        if compare_colors(loot_green, get_cs_cv()[y][x]) < 15:
            device_click_circle(x, y, 15)
            # wreck need a sec to disappear
            time.sleep(2)
            return

        # re-click if if takes longer
        if checkpoint == 0 and time.time() > waiting_time + 24:
            filter_action(1, 2, 5)
            checkpoint = 1

        time.sleep(2)
def warp_to_ano():
    set_filter('Ano')
    device_click_filter_block()
    time.sleep(2)
    anomaly = choose_anomaly()
    print()
    print(anomaly)
    # sometimes the interface times out and i have to reopen it
    device_click_filter_block()
    warp_to(anomaly[2], preferredOrbit, 0)
    set_filter('PvE')
    time.sleep(3)
    time.sleep(7)
    wait_warp()

    # swap to PvE
def danger_handling_combat():
    # check hp
    repair(85)
    if get_hp()[2] < 90:
        print('hull critical')
        combat_return(0)
        quit()
    if get_cap() < 10:
        print('capacitor critical')
        for i in range(3):
            warp_and_hide(1)
        wait_for_cap()
        warp_to_ano()
        combat()
        return 1
    if get_filter_icon('all_ships.png'):
        print('player detected')
        # todo: player handling ratting
        activate_autopilot()
        time.sleep(4)
        activate_the_modules('esc')
        time.sleep(5)
        wait_warp()
        warp_to_ano()
        combat()
        return 1
    return 0
def danger_handling_farming():
    # todo player handling
    if get_filter_icon('all_ships.png'):
        print('player detected')
        activate_autopilot()
        time.sleep(4)
        activate_the_modules('esc')
        time.sleep(5)
        wait_warp()
        warp_to_ano()
        combat()
        return 1
    return 0


# STATES
def combat_start_from_station():
    undock_and_modules()
    set_pi_planet_for_autopilot(get_planet())
    device_update_cs()
    activate_autopilot()
    wait_end_navigation(10)
    playsound(Path_to_script + 'assets\\sounds\\bell.wav')
    warp_to_ano()
    combat()
def combat_start_from_system():
    update_modules()
    warp_to_ano()
    combat()

def loot():
    device_update_cs()
    print('looting')
    # swap to container view
    # init
    if 1:
        # turn on prop module
        activate_the_modules('prop')

        # find and click wreck icon in filter bar
        tmp = get_filter_icon('wreck')
        if tmp == 0:
            if get_cargo() > 90:
                combat_return(0)
            else:
                warp_to_ano()
                combat()
                return
        x, y = tmp
        device_click_circle(x, y, 10)

    while 1:
        device_update_cs()
        # check for rats respawn late
        if get_npc_count() > 0:
            combat()

        # repair and check for players
        danger_handling_farming()

        if get_cargo() == 100:
            print('cargo full')
            set_home()
            combat_return(0)
            return

        tmp = get_filter_icon('wreck')
        if tmp == 0:
            if get_cargo() > 75:
                set_home()
                combat_return(0)
            else:
                print('site done')
                warp_to_ano()
                combat()
                return
        work_on_container()
def combat():
    # todo: lock delay for no dmg split
    print('combat')
    # set_filter('PvE')

    activate_the_modules('prop')

    tmp_weapon = time.time()
    tmp_cd = time.time() + 30
    last_npc_count = 0

    while 1:
        # check hp, cap and other players
        device_update_cs()
        danger_handling_combat()

        # start of wave/enter combat
        tmp = get_npc_count()
        if tmp == 0:
            loot()
        if last_npc_count < tmp:
            target_action(1, 1)
            target_action(2, 1)
            time.sleep(1)
            device_update_cs()
        last_npc_count = tmp

        # get locked 1 is not really that reliable, lots of false negative
        if get_is_locked(2) or get_npc_count() == 1:

            # weapons
            if tmp_weapon < time.time():
                if activate_the_modules('drone'):
                    activate_the_modules('weapon')
                    tmp_weapon = time.time() + 10

            # cd items
            if tmp_cd < time.time():
                if activate_the_modules('cd'):
                    tmp_cd = time.time() + 90
                    # 0815 ewar
                    activate_the_modules('ewar')

            # todo: improve ewar?

        # lock second one?
        if get_is_locked(2) == 0 and get_tar_cross():
            target_action(2, 1)

        time.sleep(2)
    # todo react to close enemys, nos, web, etc

def combat_return(got_ganked):
    # activate autopilot and run (maybe i got ganked?)
    activate_autopilot()
    if get_eco_mode():
        device_toggle_eco_mode()
    time.sleep(3)
    for module in get_module_list():
        if module[1] == 'esc':
            activate_module(module)
        if module[1] == 'prop':
            deactivate_module(module)
    device_click_rectangle(246, 269, 77, 73)
    if got_ganked == 1:
        print('got ganked')
        ding_when_ganked()
        save_screenshot()
    time.sleep(2)

    print('checking if dead')
    device_update_cs()
    if get_is_capsule() or get_is_in_station():
        absolutely_professional_database = open('E:\\Eve_Echoes\\Bot\\professional_database.txt', 'a')
        absolutely_professional_database.write(
            get_name() + ' died at:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1347517370)) + '\n\n')
        absolutely_professional_database.close()
        quit()
    else:
        print('going home')
        # wait until autopilot gone
        wait_end_navigation(20)

        print('arriving')
        # dump ressources
        dump_items()
        farm_tracker(got_ganked)
        # repeat?
    if get_repeat() == 0:
        playsound(Path_to_script + 'assets\\sounds\\bell.wav')
        quit()
    combat_start_from_station()
    return

# STARTS
def main():
    interface_show_player()
    combat_start_from_station()
def custom():
    combat_start_from_system()
    # combat_start_from_system()

read_config_file()
config_uni()
if get_start() == 'main':
    main()
if get_start() == 'custom':
    custom()
