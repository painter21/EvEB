# only works on 960x540

from numpy import random
from universal_small_res import *

last_farm_site, start_farm_time, last_inventory_value = '', time.time(), 0

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

# TASKS
def wait_for_cap():
    print('waiting for cap')
    for module in ModuleList:
        deactivate_module(module)
    while 1:
        if get_capacitor() > 60:
            return
        troubleshoot_filter_window()
        if get_player_thread():
            for i in range(3):
                flee(4)
                print('player detected')
            playsound('assets\\sounds\\bell.wav')
            wait_warp()
            warp_to_ano()
            combat()
            return 1
        repair(100)
        time.sleep(3)
def work_on_container():
    waiting_time = 10
    click_rectangle(1210, 67, 314, 88)
    click_rectangle(903, 168, 301, 91)
    while 1:
        for i in range(waiting_time):
            update_cs()
            time.sleep(0.1)
            if CS_image[772][600][1] > 85:
                count = 0
                while 1:
                    click_rectangle(454, 748, 261, 67)
                    update_cs()
                    if CS_image[772][600][1] < 85:
                        break
                    if count > 20:
                        playsound('assets\\sounds\\bell.wav')
                    count += 1
                    break
                return 0
            if danger_handling_farming() == 1:
                return 1
            time.sleep(0.9)
        waiting_time *= 2
        print('increased waiting time to', waiting_time)
        if waiting_time > 20:
            return 0
        repair(100)
        if get_speed() == 0:
            click_circle(590, 754, 25)
def warp_to_ano():
    set_filter('Ano')
    anomaly = choose_anomaly()
    if anomaly == 'scout':
        warp_to(0, anomaly[2], anomaly[3], anomaly[4], anomaly[5])
        solve_scouts()
    print()
    print(anomaly)
    # sometimes the interface times out and i have to reopen it
    device_click_rectangle(1243, 265, 275, 254)
    warp_to(preferredOrbit, anomaly[2], anomaly[3], anomaly[4], anomaly[5])
    time.sleep(3)
    farm_tracker(anomaly)
    time.sleep(7)
    wait_warp()

    # swap to PvE


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
def loot():
    print('looting')
    # swap to container view

    # turn on prop module
    for module in ModuleList:
        if module[1] == 'prop':
            print('activating prop')
            activate_module(module)

    swap_filter('PvE')
    # scroll up
    swipe_from_circle(1406, 132, 20, 110, 1)

    # find and click wreck icon in filter bar
    x, y, w, h = 1547, 86, 18, 445
    wreck_icon = cv.imread('assets\\wreck.png')
    crop_img = CS_cv[y:y + h, x:x + w]
    result = cv.matchTemplate(crop_img, wreck_icon, cv.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    if max_val > 0.95:
        click_circle(max_loc[0] + x + 5, max_loc[1] + y + 7, 15)
        while 1:

            # behavior
            update_cs()
            repair(100)
            danger_handling_farming()
            if get_npc_count():
                combat()
                return

            if get_cargo() > 95:
                print('cargo full')
                go_home()
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

    orbit_enemy(0)
    # maybe i shouldnt directly engage a potential enemy? it saves me like 6 secs every
    # fight but seems akward, orbit is okay
    engage_enemy(0)

    while 1:
        print('combat cycle')
        if update_and_checkup_for_combat() == 1:
            return
        troubleshoot_filter_window()
        current_npc_count = get_npc_count()
        print(0)
        # update targets
        # todo: lock closer targets
        if time.time() - tmp_lock > 0:
            if press_lock_button():
                tmp_lock = time.time() + 7
                tmp_weapon = time.time() + 10

        # no enemies
        if not current_npc_count:
            time.sleep(2)
            update_cs()
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
                        # this orbit call should not be necessary, but sometimes it somehow misses orbit
                        orbit_enemy(0)
                        tmp_weapon = time.time() + 10

        print(3)
        # activate standard modules, behavior
        if current_npc_count != last_npc_count:
            orbit_enemy(0)
            engage_enemy(0)
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

# STARTS
def main():
    interface_show_player()
    combat_start_from_station()
def custom():
    print('hi')

if get_start() == 'main':
    main()
if get_start() == 'custom':
    custom()
