
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
    expected_ano_list_size = 0
    top_to_bottom = 0
    safe_ano_list = 0
    site_ano_list = 0
    new_ano_spawns = []
    spawn_data = [0, 0, 0, 0, 0]
    ano_margin_score = 500000

# anomalies are saved as following: [size, code, filter_list_nbr, level, type(base or not)]

# simple small tasks
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
    for ano1 in ano_list:
        lowest_score = 10000000000
        best_ano = 0
        score = compare_ano_code(ano1[1], ano[1])
        if score < lowest_score:
            best_ano = ano1
            lowest_score = score
    return ano_list.index(best_ano), lowest_score
def update_safe_ano_list(new_ano_list):
    global safe_ano_list
    global new_ano_spawns

    if safe_ano_list == 0:
        # just started out, mark all anos as to do
        for ano in new_ano_list:
            ano[4] = 1
        safe_ano_list = new_ano_list
        return

    new_ano_list = get_list_anomaly()
    for ano in new_ano_list:
        best_match = find_best_match(ano, safe_ano_list)
        if best_match[1] < ano_margin_score:
            # we have a match, update the type in new_ano_list
            new_ano_list[new_ano_list.index(ano)][4] = safe_ano_list[best_match[0]][4]
        else:
            # newly spawned ano, should compare type and list number
            # todo
            return

    new_ano_spawns = []
    # check: find old anomalies
    # check: note spawn time stats, if sufficient
    # todo: mark new ones with spawn timer/ base_bool
    # check: clear new ano spawns
    return
def check_for_new_anos():
    print('\tupdate_site_ano_list')
    global site_ano_list

    new_ano_list = get_list_anomaly()
    if site_ano_list == 0:
        site_ano_list = new_ano_list

    # every anomaly in the new list will be matched with the old list and the new_ano_spawns.
    # if it cant be found, it must be a new spawn

    # todo: maybe remove paired ano from site_ano_list to avoid processing time
    for ano in new_ano_list:
        best_match = find_best_match(ano, site_ano_list)
        if best_match[1] > ano_margin_score:
            best_match = find_best_match(ano, new_ano_spawns)
            if best_match[1] < ano_margin_score:
                # old spawn, update filter_list_nbr
                print('\t\t new spawned ano ', new_ano_spawns[best_match[0]][0], ano[2])
                new_ano_spawns[best_match[0]][2] = ano[2]

            else:
                # must be a new spawn

                # the current discovery time is considered the spawn time, check if its similar to other spawns
                # theese can be found in the spawn_data list, 0;1 min-> index 0, 2;3 min->index1 and so on
                spawn_time = int((datetime.datetime.now().minute % 10) / 2)
                # check for enough spawns and add data
                spawn_data[spawn_time] += 1
                if sum(spawn_data) > 4:
                    # we do have enough spawn data

                    max_value = max(spawn_data)
                    max_index = spawn_data.index(max_value)

                    if max_index == spawn_time:
                        # will get preferred clear
                        ano[4] = 1

                new_ano_spawns.append(ano)
                print('\t\tnew spawn: ' + ano[0], ano[4])
    return

def return_to_safespot_and_restart():
    activate_autopilot(1)
    device_update_cs()
    check_if_blank_screen()
    time.sleep(20)
    get_list_anomaly()
    activate_autopilot(1)
    wait_until_ship_stops()
    main()
def wait_until_ship_stops():
    while 1:
        if get_speed() < 20:
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
            return_to_safespot_and_restart()
    if get_cap() < 10:
        # i had an issue, where the cap was at 70% and it delivered 5%, i will recheck it
        device_update_cs()
        if get_cap() < 10:
            print('capacitor critical')
            return_to_safespot_and_restart()
            main()
    '''if get_filter_icon('all_ships'):
        activate_autopilot(1)
        quit()'''
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

    save_screenshot('start')

    global weapon_module
    global expected_ano_list_size
    last_hp = get_hp()
    tmp_weapon = time.time()
    tmp_ano_check = time.time()
    tmp_cd = time.time() - 90
    tmp_ewar = time.time()
    tmp_prop = time.time() - 100
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
            deactivate_the_modules('prop')
            tmp_prop = time.time() + 8

        # start of wave/enter combat
        # the new wave recognition works great, maybe burn away for 20s and then lock all?
        # the target cross appears slightly bevore a wave spawns and is a good indicator for target handling
        tmp = get_npc_count()
        if get_tar_cross():

            # a new wave can be detected by the number of enemys. are tere more then bevore? new wave
            time.sleep(1)
            device_update_cs()
            print('npc-count: ', tmp)
            if last_npc_count < tmp:

                # get to distance
                wavecount += 1
                print("\tnew wave", wavecount)
                target_action(1, 2)
                time.sleep(1)
                activate_the_modules('prop')
                if ano_version != 'small' and wavecount > 2:
                    tmp_prop = time.time() + 42

                # start shooting something
                target_action(1, 4)
                time.sleep(6)
                target_action(1, 4)

                # hopefully 12 secomnds were enough for fast enemys to get close
                click_tar_cross_location()
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
                if not get_is_locked(2):
                    click_tar_cross_location()
        last_npc_count = tmp
        # since it is a catch, i don't have to check all the time, so there is a timer
        if tmp_weapon < time.time():
            activate_the_modules('weapon', 1)
            activate_the_modules('drone', 1)
            tmp_weapon = time.time() + 20

            if tmp_cd + 90 < time.time():
                activate_the_modules('cd')
                tmp_cd = time.time()

        print('\t check if enemy is hitting me and activate ewar if he does')
        # the enemy should never hit me, unless they get close, activate counter measures
        new_hp = get_hp()
        if tmp_ewar + 10 < time.time() and (last_hp[0] > new_hp[0] + 10 or last_hp[1] > new_hp[1] + 10 or last_hp[2] > new_hp[2] + 10):
            activate_the_modules('ewar', 1)
            activate_the_modules('prop')
            tmp_prop = time.time() + 42
            last_hp = new_hp
            tmp_ewar = time.time()

        print('\tcheck anoms')
        if tmp_ano_check + 120 < time.time():
            tmp_ano_check = time.time()
            new_list_size = get_filter_list_size()
            if expected_ano_list_size < new_list_size:
                expected_ano_list_size = new_list_size
                save_screenshot()
                get_list_anomaly(just_visible=1, anom_icon_must_be_clicked=0)
            time.sleep(2)
            device_click_filter_block_reset()
            time.sleep(1)

        print('\tcheck if done')
        if not get_filter_icon('npc'):
            time.sleep(5)
            device_update_cs()
            if not get_filter_icon('npc'):

                # fly home and check anoms for a new spawn
                return_to_safespot_and_restart()

        time.sleep(2)

def preparation():
    print('preparation')

    # getting main weapon module for easy activation/ -check
    global weapon_module
    weapon_module = None
    for module in get_module_list():
        if module[1] == 'weapon':
            weapon_module = module
    if weapon_module is None:
        print('weapon no found')
        quit()

    # reading amount of available anoms
    global expected_ano_list_size
    if expected_ano_list_size == 0:
        expected_ano_list_size = get_filter_list_size()

def main():
    # todo: maybe remove prep if it is not the first try
    print('starting bot...')
    # lobby

    # anything critical?
    if get_hp()[2] < 90:
        print('hp critical, please repair')
    if get_local_count() > 1 or get_cap() < 10:
        activate_autopilot(1)
        print('cap or system unsafe, waiting for clear')
        time.sleep(3)
        activate_autopilot(1)
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
        global expected_ano_list_size
        read_config_file()
        print(top_to_bottom)
        ano_list = get_list_anomaly(anom_icon_must_be_clicked=0)
        global safe_ano_list
        safe_ano_list = ano_list
        ano_list_size = len(ano_list)
        ano_version = "small"
        if top_to_bottom:
            for i in range(ano_list_size):
                if i != 0:
                    if ano_list[i][0] == 'scout' or ano_list[i][0] == 'inquisitor' or ano_list[i][0] == 'deadspace':
                        print('skipping special anomaly')
                    else:
                        device_click_filter_block()
                        warp_in_system(i+1, 40, 0)
                        ano_version = ano_list[i][0]
                        break
        else:
            for i in range(ano_list_size):
                ano_nbr = ano_list_size - i - 1
                if ano_nbr != 0:
                    if ano_list[ano_nbr][0] == 'scout' or ano_list[ano_nbr][0] == 'inquisitor' or ano_list[ano_nbr][0] == 'deadspace':
                        print('skipping special anomaly')
                    else:
                        device_click_filter_block()
                        warp_in_system(ano_nbr + 1, 40, 0)
                        ano_version = ano_list[ano_nbr][0]
                        break
        log(str(datetime.datetime.utcnow()+datetime.timedelta(hours=2)), 'E:\Eve_Echoes\Bot\_Paul\\ratting\\log.txt')
        #
        preparation()
        wait_until_ship_stops()
        time.sleep(5)
        combat(ano_version)
    return
def custom():
    print(int((datetime.datetime.now().minute % 10) / 2))
    return

read_config_file()
config_uni()
update_modules()
if get_start() == 'main':
    main()
if get_start() == 'custom':
    custom()
