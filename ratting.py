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
    print('\tmining_from_station()')

if 1:
    last_npc_icon_x, last_npc_icon_y = 0, 0
    last_wallet_balance = 0
    time_farming = time.time()

# INTERNAL
def farm_tracker(inv_value):
    print('\tfarm_tracker()')
    # should be opened in station
    global last_wallet_balance, time_stamp_farming
    current_balance = get_wallet_balance()
    if last_wallet_balance == 0:
        last_wallet_balance = current_balance
        return

    print('\t\twallet difference: ' + str(current_balance - last_wallet_balance))
    print('\t\tinventory value: ' + str(inv_value))
    value = current_balance - last_wallet_balance + inv_value
    last_wallet_balance = current_balance

    count = time.time() - time_stamp_farming
    time_stamp_farming = time.time()
    string = get_name() + ': ' + str(datetime.datetime.utcnow()+datetime.timedelta(hours=2)) + \
             '\n' + str(value/1000) + ' kISK\n' + str(int(count/60)) + 'm ' + str(int(count - int(count/60)*60)) + 's\n\n'
    absolutely_professional_database = open('E:\\Eve_Echoes\\Bot\\professional_database.txt', 'a')
    absolutely_professional_database.write(string)
    absolutely_professional_database.close()
def choose_anomaly():
    print('\tchoose_anomaly()')
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
    print('\t\tget_npc_icon_current_loc()')
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
    print('\t\tget_npc_count()')
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
def warp_and_hide(got_ganked):
    print('\twarp_and_hide()')
    # escape
    escape_autopilot()

    # set autopilot to other system if ganked, should be done during warp
    wait_end_navigation(1)
    toggle_planet()
    set_pi_planet_for_autopilot(get_planet())

    # wait, if re-gank, swap system
    for i in range(150):
        device_update_cs()
        if get_filter_icon('all_ships'):
            escape_autopilot()
            set_home()
            wait_end_navigation(5)
            if get_filter_icon('all_ships.png'):
                combat_return(1)
            break
        time.sleep(2)

    # if clear, toggles back the planet, why should the bot leave the system if noone was dangerous
    if got_ganked == 0:
        toggle_planet()
    set_pi_planet_for_autopilot(get_planet())
    warp_to_ano()
    combat()
def get_list_anomaly():
    print('\t\tget_list_anomaly()')
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
            filter_list_nr = int((y_text + 12)/52)
            if filter_list_nr > 1:
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
    print('\t\twait_and_watch_out()')
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
    print(' wait_for_cap()')
    activate_filter_window()
    for module in ModuleList:
        deactivate_module(module)
    while 1:
        if get_cap() > 60:
            return
        wait_and_watch_out(4)
def work_on_container():
    print('\twork_on_container()')
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
    print(' warp_to_ano()')
    set_filter('Ano', 0)
    device_click_filter_block()
    time.sleep(2)
    anomaly = choose_anomaly()
    print()
    print(anomaly)
    # sometimes the interface times out and i have to reopen it
    device_click_filter_block()
    tmp = warp_in_system(anomaly[2], preferredOrbit, 0)
    if tmp == 1:
        warp_and_hide()
    if tmp == 2:
        escape_autopilot()

    # swap to PvE
def danger_handling_combat():
    print('\t\tdanger_handling_combat()')
    # check hp
    repair(85)
    if get_hp()[2] < 90:
        combat_return(0)
        quit()
    if get_cap() < 10:
        print('capacitor critical')
        activate_autopilot(0)
        wait_for_cap()
        warp_to_ano()
        combat()
        quit()
    if get_filter_icon('all_ships'):
        warp_and_hide(1)
        return 1
    return 0
def danger_handling_farming():
    print('\t\tdanger_handling_farming()')
    # todo player handling
    if get_filter_icon('all_ships'):
        print('player detected')
        escape_autopilot()
        warp_to_ano()
        combat()
        return 1
    return 0


# STATES
def combat_start_from_station():
    print(' combat_start_from_station()')
    undock_and_modules()
    set_pi_planet_for_autopilot(get_planet())
    device_update_cs()
    activate_autopilot(0)
    wait_end_navigation(10)

    # sometimes te speed meter screws up
    stop = 1
    while stop:
        speed_x, speed_y = 460, 495
        print('speed-o-meter value: ', get_cs_cv()[speed_y][speed_x][2])
        if get_cs_cv()[speed_y][speed_x][2] > 130:
            stop = 0
        else:
            toggle_planet()
            set_pi_planet_for_autopilot(get_planet())
            activate_autopilot(0)
            wait_end_navigation(10)

    activate_filter_window()
    set_pi_planet_for_autopilot(get_planet())
    warp_to_ano()
    combat()
def combat_start_from_system():
    print(' combat_start_from_system()')
    update_modules()
    time.sleep(2)
    set_pi_planet_for_autopilot(get_planet())
    device_update_cs()
    warp_to_ano()
    combat()

# todo: loot border is on 10%
def loot():
    print(' loot()')
    device_update_cs()
    # swap to container view
    # init
    if 1:
        # turn on prop module
        activate_the_modules('prop')

        # find and click wreck icon in filter bar
        tmp = get_filter_icon('wreck')
        if tmp == 0:
            if get_cargo() > 10:
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
            combat_return(0)
            return

        tmp = get_filter_icon('wreck')
        if tmp == 0:
            if get_cargo() > 10:
                set_home()
                combat_return(0)
            else:
                print('site done')
                warp_to_ano()
                combat()
                return
        work_on_container()
def combat():
    print(' combat()')
    # todo: lock delay for no dmg split
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
            target_action(1, 4)
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
    print(' combat_retur()')
    # activate autopilot and run (maybe i got ganked?)
    escape_autopilot()
    if got_ganked == 1:
        print('got ganked')
        ding_when_ganked()
        save_screenshot()
    set_home()
    activate_autopilot(0)
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

        # click on close
        device_click_circle(926, 30, 10)
        time.sleep(2)

        print('arriving')
        # dump ressources
        farm_tracker(dump_items())
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
    time.sleep(3)
    device_update_cs()
    update_modules()
    combat()

read_config_file()
config_uni()
farm_tracker(0)
if get_start() == 'main':
    main()
if get_start() == 'custom':
    custom()
