
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
        if tmp[0] == 'toptobottom':
            global top_to_bottom
            top_to_bottom = int(tmp[1])
        tmp = file.readline()

if 1:
    last_npc_icon_x, last_npc_icon_y = 0, 0
    last_wallet_balance = 0
    time_farming = time.time()
    weapon_module = None
    drone_module = None
    top_to_bottom = 0
    safe_ano_list = []
    site_ano_list = []
    new_ano_spawns = []
    spawn_data = [0, 0, 0, 0, 0]
    ano_margin_score = 800000
    cycle = 0
    ano_spawned_in_warp_to_time = -2

# anomalies are saved as following: [size, code, filter_list_nbr, level, type(base or not)]

# simple small tasks

# todo: unstable functions
def check_filter_menu_and_close():
    print('\t\t\tcheck_filter_menu_ad_close')
    # we basically look for radical changes that stay for 40 px
    start_x, start_y, height = 543, 96, 345
    image = get_cs_cv()
    color_margin = 10
    streak_length = 0
    long_streaks = 0
    previous_color = image[start_y][start_x]
    add_rectangle(start_x-2, start_y, 0, height, stroke_width=1)
    for i in range(height):
        # check if there is a split
        pixel = image[start_y + i][start_x]
        highest_difference = 0
        for color_index in range(len(pixel)):
            difference = abs(int(pixel[color_index]) - previous_color[color_index])
            highest_difference = max(difference, highest_difference)

        if highest_difference > color_margin or i == height - 1:
            print('\t\t\tbreak at', i, image[start_y + i - 1][start_x], pixel)
            add_point(start_x-1, start_y + i - 1)
            if streak_length > 40:
                long_streaks += 1
            streak_length = 0
        else:
            streak_length += 1

        previous_color = pixel

    show_image()
    if long_streaks > 2:
        device_click_filter_block_reset()
def read_data():
    print('\t\tread_data')
    global spawn_data
    global safe_ano_list
    file = open('data.txt')
    tmp = file.readline().strip()
    first_line = 1
    while tmp != '':
        tmp = str(tmp).split()
        if first_line:
            first_line = 0
            for index in range(len(tmp)):
                spawn_data[index] = int(tmp[index])
            print('\t\t\t old spawn_data: ' + str(tmp))
        else:
            # create an artificial ano:
            code = []
            for i in range(len(tmp)):
                code.append(int(tmp[i]))
            artificial_ano = ['artificial', code, 0, 0, 9]

            # match ano
            best_match = find_best_match(artificial_ano, safe_ano_list)
            if best_match[1] < ano_margin_score:

                # set it as base anomaly
                safe_ano_list[best_match[0]][4] = 1
                print('\t\t\t old base_ano: ' + best_match[0])

        tmp = file.readline()
    return
def write_data(mode=0):
    print('\t\twrite_data')
    # first line will be the spawn chart, all other lines the code of base_anomalies
    link = 'data.txt'
    to_write = ''
    for data in spawn_data:
        to_write += str(data) + ' '

    if mode == 0:
        for ano in safe_ano_list:
            if ano[4] > 2:
                to_write += '\n'
                for data in ano[1]:
                    to_write += str(data) + ' '
    else:
        previous_file = open('data.txt')
        next(previous_file)
        for line in previous_file:
            to_write += '\n' + line.rstrip()
    txt_file = open(link, 'w')
    txt_file.write(to_write)
    txt_file.close()
    return
def choose_anomaly():
    global safe_ano_list

    print('choose anomaly')
    # check if there is a preferred anomaly
    safe_ano_list_copy = safe_ano_list.copy()
    # start from bottom
    safe_ano_list_copy.reverse()
    # print_ano_list(safe_ano_list_copy, 'safe_ano_list_copy')
    print_ano_list(safe_ano_list, 'safe_ano_list')

    highest_priority_ano = 0
    for ano in safe_ano_list_copy:
        if highest_priority_ano == 0:
            # print('set ano to ', ano)
            highest_priority_ano = ano
        if ano[4] > highest_priority_ano[4]:
            highest_priority_ano = ano

    if highest_priority_ano[4] > 0:
        return highest_priority_ano
    if highest_priority_ano[4] < 0:
        return 0

    # highest priority must be 0
    print('only low priority anos available')
    okay_index = -1
    for index in range(len(safe_ano_list)):
        if safe_ano_list[index][4] == 0:
            safe_ano_list[index][4] = 1
            okay_index = index
    safe_ano_list[0][4] = -1
    if okay_index == -1:
        return 0
    return safe_ano_list[okay_index]
def set_auto_pilot_sequence():
    while 1:
        ding_when_ganked()
    '''activate_autopilot(1)
    time.sleep(1)
    # click filter
    device_click_rectangle(179, 505, 45, 32)
    time.sleep(1)
    device_click_rectangle(232, 426, 158, 45)
    time.sleep(1)
    device_click_rectangle(181, 210, 40, 41)
    time.sleep(2)
    device_click_circle(197, 178, 9)
    time.sleep(3)
    activate_autopilot(1)'''


def print_ano_list(ano_list, header='some_ano_list'):
    print('\nS' + header)
    print('size, nbr, type')
    for ano in ano_list:
        print(ano[0], ano[2], ano[4])
        # print(ano[1])
    print()
def compare_ano_code(code1, code2):
    sum_code1 = 0
    sum_code2 = 0
    for i in range(len(code1)):
        sum_code1 += code1[i]
        sum_code2 += code2[i]
    factor_code2 = sum_code1 / sum_code2
    difference_score = 0
    for i in range(len(code1)):
        difference_score += abs(code1[i] - code2[i] * factor_code2) ** 2
    return difference_score
def find_best_match(ano, ano_list):
    lowest_score = 10000000000
    best_ano = ano_list[0]
    for ano1 in ano_list:
        score = int(compare_ano_code(ano1[1], ano[1]))
        # print(score)
        if score < lowest_score:
            best_ano = ano1
            lowest_score = score
    print(ano[2], ano_list.index(best_ano), lowest_score)
    return ano_list.index(best_ano), lowest_score
def update_safe_ano_list():
    print('\tupdate_safe_ano_list')
    ding_when_ganked()
    global cycle
    global safe_ano_list
    global new_ano_spawns
    global ano_spawned_in_warp_to_time
    new_ano_list = get_list_anomaly()
    cycle += 1

    if not safe_ano_list:
        # just started out
        safe_ano_list = new_ano_list
        for ano in safe_ano_list:
            if ano[0] == 'unknown':
                ano[4] = -1
        read_data()
        link = 'current_ano_list.txt'
        to_write = ''
        for ano in new_ano_list:
            to_write += str(ano[0] + str(ano[4])) + '\n'
        txt_file = open(link, 'w')
        txt_file.write(to_write)
        txt_file.close()
        print('\t\tjust started out')
        return

    unknown_anos = []
    for ano in new_ano_list:
        # first, check all anos in the new_ano_list if they are known from bevore
        best_match = find_best_match(ano, safe_ano_list)
        if best_match[1] < ano_margin_score:
            # we have a match, update the type in new_ano_list
            ano[4] = safe_ano_list[best_match[0]][4]
            # if the name was not readable, take te one from the last read
            if ano[0] == 'unknown':
                ano[0] = safe_ano_list[best_match[0]][0]
            print('\t\tknown', safe_ano_list[best_match[0]][2], '->', ano[2])

        else:
            # unknown, newly spawned ano, should compare type and list number
            # did you just warp back due to the spawn?
            if ano_spawned_in_warp_to_time != -2:
                print('\t\tunknown, but recent', ano[2])
                if max(spawn_data) > 3:
                    # data is useable
                    ano[4] = spawn_data[ano_spawned_in_warp_to_time]

            else:
                if len(new_ano_spawns) == 0:
                    # the ano(s) mst have spawned in the warp to safe
                    save_screenshot()
                    spawn_time = int((datetime.datetime.now().minute % 10) / 2)
                    spawn_data[spawn_time] += 1
                    max_value = max(spawn_data)
                    if max_value > 3:
                        # data is useable
                        print('\t\tunknown, but recent', ano[2])
                        new_ano_list[new_ano_list.index(ano)][4] = spawn_data[spawn_time]
                else:
                    unknown_anos.append(ano)

    # if there is noting to do, there is nothing to do
    if len(unknown_anos) == 0:
        print('\t\tno unknown anomalies')
    else:

        # check if there is another unknown ano, polluting the solution, should not happen
        if len(unknown_anos) != len(new_ano_spawns):
            print('\t\tspawned anomaly list incomplete')
            # give a rough estimate of worth
            combined_preference = 0
            for spawned_aom in new_ano_spawns:
                combined_preference += spawned_aom[4]
            combined_preference = int(combined_preference / len(unknown_anos))
            for ano in new_ano_list:
                for unknown_ano in unknown_anos:
                    if ano[1] == unknown_ano[1]:
                        ano[4] = combined_preference

        else:
            for ano_index in range(len(new_ano_list)):
                for spawned_ano in new_ano_spawns:
                    if spawned_ano[2] == new_ano_list[ano_index][2]:
                        # ano is in the same place as a newly spawned ano before warp, lists are complete, must be same
                        new_ano_list[ano_index][4] = spawned_ano[4]
                        if new_ano_list[ano_index][0] == 'unknown':
                            new_ano_list[ano_index][0] = spawned_ano[0]
                        print('\t\tspawned', spawned_ano[2], '->', new_ano_list[ano_index][2])

    link = 'current_ano_list.txt'
    to_write = ''
    for ano in new_ano_list:
        to_write += str(ano[0] + str(ano[4])) + '\n'
    txt_file = open(link, 'w')
    txt_file.write(to_write)
    txt_file.close()

    safe_ano_list = new_ano_list
    new_ano_spawns = []
    ano_spawned_in_warp_to_time = -2
    write_data()
def check_for_new_anos():
    print('\tupdate_site_ano_list')
    global site_ano_list

    new_ano_list = get_list_anomaly()
    if not site_ano_list:
        save_screenshot('start_site')

        if len(new_ano_list) > len(safe_ano_list):
            save_screenshot()
            global ano_spawned_in_warp_to_time
            ano_spawned_in_warp_to_time = int((datetime.datetime.now().minute % 10) / 2)
            print('spawn_time :', ano_spawned_in_warp_to_time)
            return_to_safespot_and_restart(ano_list_just_tested=1)
        else:
            print('\t\tsite_ano_list empty, set')
            site_ano_list = new_ano_list
        return

    # every anomaly in the new list will be matched with the old list and the new_ano_spawns.
    # if it cant be found, it must be a new spawn

    # todo: maybe remove paired ano from site_ano_list to avoid processing time
    something_changed = 0
    for ano in new_ano_list:

        # check if ano is unknown. the site_ano list also contains previous spawns
        best_match = find_best_match(ano, site_ano_list)
        if best_match[1] > ano_margin_score:

            # check if it is the current ano (is the code flat in the end?)
            last_code_amplitude = ano[1][-1]
            code_flat = 1
            for i in range(1, 9):
                if last_code_amplitude - ano[1][-i] < 50:
                    last_code_amplitude = ano[1][-i]
                else:
                    code_flat = 0
                    break
            if code_flat:
                print('\t\t\tcode flat, ignore ', ano[2])
                print(ano[1])
            else:

                print('\t\tnumber ', ano[2], 'seems to be new', datetime.datetime.now().minute % 10)
                something_changed = 1

                # must be a new spawn
                # the current discovery time is considered the spawn time, check if its similar to other spawns
                # these can be found in the spawn_data list, 0;1 min-> index 0, 2;3 min->index 1 and so on
                spawn_time = int((datetime.datetime.now().minute % 10) / 2)
                # check for enough spawns and add data

                if sum(spawn_data) > 4:
                    # we do have enough spawn data
                    ano[4] = spawn_data[spawn_time]

                if ano[0] == 'unknown':
                    ano[4] = -1
                    spawn_data[spawn_time] += 1
                else:
                    if ano[0] == 'scout' or ano[0] == 'inquisitor' or ano[0] == 'deadspace':
                        ding_when_ganked()
                        ano[4] = -1
                        log(ano[0] + ', ' + datetime.datetime.now(), 'log.txt')
                        spawn_data[spawn_time] += 10
                    else:
                        spawn_data[spawn_time] += 1

                new_ano_spawns.append(ano)
                print('\t\tnew spawn: ' + ano[0], ano[4])
                # update list indicies of all anos in new_ano_spawn
    if something_changed:
        print('\t\tspawn_data: ', spawn_data)
        write_data(1)
        save_screenshot()
        for index_ano_spawns in range(len(new_ano_spawns)):
            best_match = find_best_match(new_ano_spawns[index_ano_spawns], new_ano_list)
            new_ano_spawns[index_ano_spawns][2] = new_ano_list[best_match[0]][2]

        site_ano_list = new_ano_list
    return

def return_to_safespot_and_restart(ano_list_just_tested=0):
    print('\t\treturn_to_safespot_and_restart')
    activate_autopilot(1)
    if not ano_list_just_tested:
        check_for_new_anos()
    device_update_cs()
    check_if_blank_screen()
    time.sleep(10)
    if get_autopilot_active() == 0:
        activate_autopilot(1)
    if get_npc_count() > 0:
        print('EMERGENCY COMBAT')
        ding_when_ganked()
        emergency_combat()
    activate_autopilot(1)
    wait_until_ship_stops()
    main()
def wait_until_ship_stops():
    while 1:
        if get_speed() < 50:
            return 1
        time.sleep(1)
        device_update_cs()
def danger_handling_combat():
    print('\t\tdanger_handling_combat()')
    # check hp
    check_if_blank_screen()
    repair(85)
    if get_hp()[1] < 30:
        device_update_cs()
        if get_hp()[1] < 30:
            ding_when_ganked()
            # todo: emergency combat mode (if the ships cant warp off)
            return_to_safespot_and_restart()
    if get_cap() < 10:
        # i had an issue, where the cap was at 70% and it delivered 5%, i will recheck it
        device_update_cs()
        if get_cap() < 10:
            print('capacitor critical')
            return_to_safespot_and_restart()
            main()
    if get_local_count() > 1:
        return_to_safespot_and_restart()
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
    # check if there is a second number next to the 1
    there_is_a_second_number = 0
    for i in range(h):
        if int(get_cs_cv()[last_npc_icon_y + 5 + y_off][last_npc_icon_x + x_off + h + 2][0]) + \
                get_cs_cv()[last_npc_icon_y + 5 + y_off][last_npc_icon_x + x_off + h + 2][1] + \
                get_cs_cv()[last_npc_icon_y + 5 + y_off][last_npc_icon_x + x_off + h + 2][2] > 400:
            # there is a second number
            return 2

    for i in range(h):
        if int(get_cs_cv()[last_npc_icon_y + i + y_off][last_npc_icon_x + x_off][0]) + \
                get_cs_cv()[last_npc_icon_y + i + y_off][last_npc_icon_x + x_off][1] + \
                get_cs_cv()[last_npc_icon_y + i + y_off][last_npc_icon_x + x_off][2] < 400:
            pix_not_right += 1
    if pix_not_right < 3:
        return 1
    return 2
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

def combat(ano_version="small"):
    print("combat", ano_version)
    # overview set to anoms/npc with click on anom to count anoms/see npc icon
    # is in site, kills something, hoping for the rest to autosort, autokills the rest, each wave, reset.
    # keeps warpdrive alive depending on anom/wave
    # check hp, local, cap, reset if new wave, anoms

    global site_ano_list
    site_ano_list = []
    global weapon_module
    global ano_spawned_in_warp_to_time

    tmp_weapon = time.time()
    tmp_ano_check = datetime.datetime.now().minute % 10
    tmp_cd = time.time() - 90
    tmp_prop = time.time() - 100
    tmp_ewar = time.time()
    last_hp = get_hp()

    wavecount = 0
    last_npc_count = 0
    time.sleep(3)

    while 1:
        # check hp, cap and other players
        print("\tcheck basics")
        device_update_cs()
        close_select_target_popup()
        danger_handling_combat()
        if tmp_prop < time.time():
            deactivate_the_modules('prop',)
            tmp_prop = time.time() + 8

        # start of wave/enter combat
        # the new wave recognition works great, maybe burn away for 20s and then lock all?
        # the target cross appears slightly bevore a wave spawns and is a good indicator for target handling
        tmp_npc_count = get_npc_count()
        if get_tar_cross():

            # a new wave can be detected by the number of enemys. are tere more then bevore? new wave
            time.sleep(1)
            device_update_cs()
            print('npc-count: ', tmp_npc_count)
            if last_npc_count < tmp_npc_count:

                # get to distance
                wavecount += 1
                print("\tnew wave", wavecount)
                device_click_filter_block_reset()
                target_action(1, 2)
                time.sleep(1)
                activate_the_modules('prop')
                if ano_version != 'small' and wavecount > 2:
                    tmp_prop = time.time() + 42

                # start shooting something
                target_action(1, 4)
                if wavecount == 1:
                    time_min_now = datetime.datetime.now().minute % 10
                    print('\tcheck anoms ', time_min_now)
                    check_for_new_anos()
                    tmp_ano_check = time_min_now
                    time.sleep(2)
                    device_click_filter_block_reset()
                    time.sleep(3)
                else:
                    time.sleep(12)
                # hopefully 12 secomnds were enough for fast enemys to get close
                click_tar_cross_location()
                time.sleep(2)
                target_action(1, 4)

                time.sleep(4)
                device_update_cs()
                activate_the_modules('weapon', 1)
                activate_the_modules('laser', 1)
                if tmp_cd + 90 < time.time():
                    activate_the_modules('cd')
                    tmp_cd = time.time()

                time.sleep(10)
                last_hp = get_hp()
            else:
                print("\told wave")
                #  if it is an old wave, check if there are still enough targets and if weapons are running
                if not get_is_locked(2) or not get_is_locked(3):
                    click_tar_cross_location()
        last_npc_count = tmp_npc_count
        # since it is a catch, i don't have to check all the time, so there is a timer
        if tmp_weapon < time.time():
            activate_the_modules('weapon', 1)
            tmp_weapon = time.time() + 20

            if tmp_cd + 90 < time.time():
                activate_the_modules('cd')
                tmp_cd = time.time()

        print('\t check if enemy is hitting me and activate ewar if he does')
        # the enemy should never hit me, unless they get close, activate counter measures
        new_hp = get_hp()
        if tmp_ewar + 10 < time.time() and (
                last_hp[0] > new_hp[0] + 10 or last_hp[1] > new_hp[1] + 10 or last_hp[2] > new_hp[2] + 10) or new_hp[1] < 85:
            activate_the_modules('ewar', 1)
            activate_the_modules('prop')
            tmp_prop = time.time() + 42
            tmp_ewar = time.time()
            last_hp = new_hp

        time_min_now = datetime.datetime.now().minute % 10
        print('anos? ', time_min_now, tmp_ano_check, tmp_npc_count)
        if (time_min_now > tmp_ano_check + 1 or time_min_now < 8 and time_min_now + 10 > tmp_ano_check + 1 and tmp_ano_check > 7) and tmp_npc_count > 1:
            print('\tcheck anoms ', time_min_now)
            tmp_ano_check = time_min_now
            check_for_new_anos()

        print('\tcheck if done')
        if not get_filter_icon('npc'):
            time.sleep(5)
            device_update_cs()
            if not get_filter_icon('npc'):

                # fly home and check anoms for a new spawn
                log('finished ' + ano_version + ' ' + str(datetime.datetime.now()), 'log.txt')
                return_to_safespot_and_restart()

        time.sleep(2)
def emergency_combat():
    target_action(1, 4)
    activate_the_modules('battery')
    activate_the_modules('prop')
    while get_npc_count() > 0:
        device_update_cs()
        if get_tar_cross():
            click_tar_cross_location()
        activate_the_modules('ar_regen')
        deactivate_the_modules('prop')
        time.sleep(5)

def preparation():
    print('preparation')

    # getting main weapon module for easy activation/ -check
    global weapon_module
    weapon_module = None
    for module in get_module_list():
        if module[1] == 'weapon':
            weapon_module = module
    if weapon_module is None:
        print('weapon not found')
        quit()

    global drone_module
    for module in get_module_list():
        if module[1] == 'drone':
            drone_module = module
            break
    if drone_module is None:
        print('drone not found')
        quit()

    '''
    # reading amount of available anoms
    global expected_ano_list_size
    if expected_ano_list_size == 0:
        expected_ano_list_size = get_filter_list_size()
    '''

def main():
    # todo: maybe remove prep if it is not the first try
    print('starting bot...')
    # lobby

    # check autopilot
    if get_autopilot():
        if get_autopilot_active():
            activate_autopilot(1)
    else:
        set_auto_pilot_sequence()

    # anything critical?
    if get_hp()[2] < 90:
        print('hp critical, please repair')
    if get_local_count() > 1 or get_cap() < 10:
        print('cap or system unsafe, waiting for clear')
        device_update_cs()
        while get_local_count() > 1 or get_cap() < 10:
            time.sleep(5)
            device_update_cs()

    # already in site?
    if get_filter_icon('npc'):
        preparation()
        combat()
    else:
        # if not, warp to last anom, make prep during warp and start combat
        read_config_file()
        print(top_to_bottom)
        update_safe_ano_list()
        ano = choose_anomaly()

        if ano == 0:
            print('no good ano available')
            time.sleep(60)
            main()

        index = safe_ano_list.index(ano)
        time.sleep(5)
        warp_in_system(index + 1, 40, 0)
        log(str(datetime.datetime.utcnow()+datetime.timedelta(hours=2)), 'E:\Eve_Echoes\Bot\_Paul\\ratting\\log.txt')
        preparation()

        time.sleep(5)
        device_update_cs()
        wait_until_ship_stops()
        combat(ano[0])
    return
def custom():
    set_auto_pilot_sequence()

read_config_file()
config_uni()
update_modules()
if get_start() == 'main':
    main()
if get_start() == 'custom':
    custom()
