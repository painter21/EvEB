# only works on 960x540
from universal_small_res import *
Path_to_script = ''
def read_config_file():
    print('\tread_config_file()')
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
    file.close()

start_program_time = time.time()
inv_dump_time = time.time()
time_farming = time.time()
total_cargo = 0

# INTERFACE HELPER
def lock_asteroid(ast2):
    if ast2[1] > 260:
        device_click_filter_block()
        time.sleep(1)
    device_click_rectangle(ast2[1], ast2[2], ast2[3], ast2[4])
    time.sleep(0.5)
    # device_update_cs()
    # add_rectangle(ast2[1], ast2[2], ast2[3], ast2[4])
    # add_rectangle(ast2[1] - 185, min(320, ast2[2]), ast2[3], ast2[4])
    # show_image()
    device_click_rectangle(ast2[1] - 185, min(320, ast2[2]), ast2[3], ast2[4])
def approach_and_start_harvest():
    # return 0: all fine, return 1: found no asteroid
    print('\tapproach_and_start_harvest')
    target_action(1, 2, 8)
    activate_the_modules('prop')
    the_module = None
    for module in get_module_list():
        if module[1] == 'harvest':
            the_module = module
            break

    for i in range(20):
        activate_module(the_module)
        wait_and_watch_out(4)
        if get_module_is_active(the_module):
            activate_the_modules('harvest')
            deactivate_the_modules('prop')
            return 0
        wait_and_watch_out(10)
    deactivate_the_modules('prop')
    log('approach and start harvest cap')
    return 1
def image_read_asteroid(image1):
    print('\t\timage_read_asteroid()')
    min_value = 10000
    best_match = ''
    for asteroid_file in os.listdir(Path_to_script + 'assets\\asteroids\\'):
        image2 = cv.imread(Path_to_script + 'assets\\asteroids\\' + asteroid_file)
        value = image_compare_text(image1, image2)
        if value < min_value:
            min_value = value
            best_match = asteroid_file
    return best_match[:-4]
def get_list_asteroid():
    print('\tget_list_asteroid()')
    # swap_filter('ining')
    # click filter element to expand filter
    device_click_filter_block()
    time.sleep(0.3)
    device_update_cs()

    wait_and_watch_out()
    list_ast = []

    # create a list of all anomaly locations (on screen)
    x, y, w, h = 731, 49, 10, 474
    img_ast = cv.imread(Path_to_script + 'assets\\ast.png')
    crop_img = get_cs_cv()[y:y + h, x:x + w]
    crop_img = image_remove_dark(crop_img, 250)
    result = cv.matchTemplate(crop_img, img_ast, cv.TM_CCORR_NORMED)
    threshold = 0.92
    loc = np.where(result >= threshold)
    # black magic do not touch
    previous_point_y = -10
    for pt in zip(*loc[::-1]):
        # ignore double results
        if pt[1] > previous_point_y + 10:
            previous_point_y = pt[1]

            # print(get_cs_cv()[y + pt[1] + 1][x + pt[0] + 10][0])
            if get_cs_cv()[y + pt[1] + 1][x + pt[0] + 10][0] < 80:
                # icon offset, size of text field
                y_text, x_text = pt[1] - 12 + y, pt[0] + 59 + x
                crop_img = get_cs_cv()[y_text:y_text + 33, x_text:x_text + 117]

                # template gen
                # remove darker pixels, seems to be a bad idea
                # crop_img = remove_bright_pix(crop_img, 75)
                # cv.imwrite('test.png', crop_img)
                # cv.imshow('.', crop_img)
                # cv.waitKey()

                list_ast.append([image_read_asteroid(crop_img), x_text - 40, y_text - 4, 150, 35])
    # show_image()
    return list_ast
# TASKS
def wait_and_watch_out(sec=0):
    print('\twait_and_watch_out')
    device_update_cs()
    if get_filter_icon('all_ships') != 0 or get_criminal() != 0:
        if get_bait() == 1:
            subprocess.call(["D:\Program Files\AutoHotkey\AutoHotkey.exe",
                             "E:\\Eve_Echoes\\Bot\\ahk_scripts\\call_paul.ahk"])
            playsound(Path_to_script + 'assets\\sounds\\bell.wav')
            print('trap card activated')
            device_toggle_eco_mode()
            time.sleep(3)
            mining_return(1)
            quit()
        mining_return(1)
        quit()
    for i in range(int(sec/2)):
        time.sleep(2)
        device_update_cs()
        if get_filter_icon('all_ships') != 0 or get_criminal() != 0:
            if get_bait() == 1:
                subprocess.call(["D:\Program Files\AutoHotkey\AutoHotkey.exe",
                                 "E:\\Eve_Echoes\\Bot\\ahk_scripts\\call_paul.ahk"])
                playsound(Path_to_script + 'assets\\sounds\\bell.wav')
                print('trap card activated')
                device_toggle_eco_mode()
                time.sleep(3)
                mining_return(1)
                quit()
            mining_return(1)
            quit()
def farm_tracker():
    print('\tfarm_tracker')
    # intended to be called when dumping cargo
    # t5med = 653k with frig in end
    global time_farming
    global total_cargo
    if (cargo := get_cargo()) > 0:
        if cargo*60 / (time.time() - time_farming) > 10:
            print('farming_ something is off', cargo*60 / (time.time() - time_farming))
            return
        total_cargo += cargo
        count = time.time() - time_farming
        total_time = time.time() - start_program_time
        string = get_name() + ': ' + str(datetime.datetime.utcnow()+datetime.timedelta(hours=2)) + '\n' + \
                 str(int(total_time / 3600)) + 'h ' + str(int((total_time - int(total_time / 3600)*3600) / 60)) + 'm ' + str(int(total_time - int(total_time / 60) * 60)) + 's;' + \
                 str(int(count/60)) + 'm ' + str(int(count - int(count/60)*60)) + 's\n' + \
                 str(cargo) + '% ' + str(total_cargo) + '%\n\n'
        absolutely_professional_database = open('E:\\Eve_Echoes\\Bot\\professional_database.txt', 'a')
        absolutely_professional_database.write(string)
        absolutely_professional_database.close()

    time_farming = time.time()
def warp_in_system_handling(target_nbr, distance, should_set_home, desired_filter):
    tmp = warp_in_system(target_nbr, distance, should_set_home, desired_filter)
    if tmp == 1:
        mining_return(1)
    if tmp == 2:
        warp_in_system_handling(target_nbr, distance, should_set_home, desired_filter)
    # 0 is fine
def loot():
    device_update_cs()
    # sometimes, ancient thing spawns, slow down
    loot_green = [48, 94, 87]
    x, y = 362, 457
    tmp = get_filter_icon('wreck')
    if tmp == 0:
        return
    device_click_rectangle(tmp[0] + 1, tmp[1] + 1, 1, 1)
    wait_and_watch_out(2)

    while tmp != 0:
        filter_action(1, 2, 5)

        not_stop = 1
        catch_time = 0
        while not_stop and catch_time < 30:
            wait_and_watch_out(2)
            device_update_cs()
            catch_time += 2
            if compare_colors(loot_green, get_cs_cv()[y][x]) < 15:
                device_click_circle(x, y, 15)
                wait_and_watch_out(4)
                not_stop = 0
        device_update_cs()
        tmp = get_filter_icon('wreck')


# STATES
def mining_from_station():
    print('\tmining_from_station()')
    if start_program_time + 10800 < time.time():
        os.system(
            "start cmd /c E:\Eve_Echoes\Bot\EveB\\venv\Scripts\python.exe E:\Eve_Echoes\Bot\EveB\mining.py & pause")
        quit()
    undock_and_modules()
    activate_filter_window()
    time.sleep(1)

    set_filter('esc', 0)

    time.sleep(3)
    if get_filter_list_size() < 2:
        set_home()
        activate_autopilot()
        time.sleep(300)
        mining_from_station()
        quit()

    if get_name() == 'bronson':
        warp_in_system_handling(1, 0, 1, 'ining')
    else:
        if get_name() == 'kort':
            warp_in_system_handling(3, 0, 1, 'ining')
        else:
            warp_in_system_handling(randint(1, 4), 0, 1, 'ining')

    while mine():
        set_filter('esc', 0)

        time.sleep(3)
        if get_name() == 'bronson':
            warp_in_system_handling(1, 0, 1, 'ining')
        else:
            if get_name() == 'kort':
                warp_in_system_handling(3, 0, 1, 'ining')
            else:
                warp_in_system_handling(randint(1, 4), 0, 1, 'ining')

    belt_handling()
    mining_return(0)
def mine():
    # returns 0: everything all right, 1: asteroid belt empty, not in asteroid belt
    print('\tlock_multiple_good_asteroids()')
    set_filter('inin', 0)
    count = 0

    # CATCH: is the miner in asteroid belt?
    asteroid_icon = get_filter_icon('asteroid')
    if asteroid_icon == 0:
        return 1
    device_click_rectangle(asteroid_icon[0] + 1, asteroid_icon[1] + 1, 1, 1)

    # find first asteroid
    if 1:
        print('\t\t:find first asteroid')
        ast_list = get_list_asteroid()
        file = open(Path_to_script + 'assets\\ore_pref.txt')
        tmp = file.readline().strip()
        while tmp != '':
            for ast2 in ast_list:
                if ast2[0] == tmp:

                    # lock asteroid
                    lock_asteroid(ast2)
                    wait_and_watch_out(2)
                    if not get_is_locked(1):
                        lock_asteroid(ast2)
                    count += 1
                    break

            if count == 1:
                break
            tmp = file.readline().strip()
        file.close()

        if count == 0:
            # swipe down
            device_click_filter_block()
            wait_and_watch_out()
            time.sleep(0.5)
            device_swipe_from_circle(822, 493, 20, 400, 3)

            # second try, should never get here
            ast_list = get_list_asteroid()
            file = open(Path_to_script + 'assets\\ore_pref.txt')
            tmp = file.readline().strip()
            while tmp != '':
                for ast2 in ast_list:
                    if ast2[0] == tmp:

                        # lock asteroid
                        lock_asteroid(ast2)
                        wait_and_watch_out(2)
                        if not get_is_locked(1):
                            lock_asteroid(ast2)
                        count += 1
                        break

                if count == 1:
                    break
                tmp = file.readline().strip()
            file.close()
            if count == 0:
                return 1
        device_update_cs()
        wait_and_watch_out()

    # approach first asteroid and establish mining
    approach_and_start_harvest()

    # wait for ship to slow down
    second_wait = 0
    while 1:
        wait_and_watch_out(6)
        if get_speed() < 10:
            if second_wait:
                break
            second_wait = 1


    # lock all good asteroids in belt
    if 1:
        print('\t\t:lock the rest')
        # reset list
        device_click_rectangle(asteroid_icon[0] + 1, asteroid_icon[1] + 1, 1, 1)

        ast_list = get_list_asteroid()
        file = open(Path_to_script + 'assets\\ore_pref.txt')
        tmp = file.readline().strip()
        while tmp != '':
            for ast2 in ast_list:
                if ast2[0] == tmp:

                    lock_asteroid(ast2)
                    count += 1

            if count == 6:
                break
            tmp = file.readline().strip()
        file.close()

        if count < 6:
            current = count
            wait_and_watch_out(4)
            # swipe down
            device_click_filter_block()
            wait_and_watch_out()
            time.sleep(0.5)
            device_swipe_from_circle(822, 493, 20, 400, 3)

            # second part of belt
            ast_list = get_list_asteroid()
            file = open(Path_to_script + 'assets\\ore_pref.txt')
            tmp = file.readline().strip()
            while tmp != '':
                for ast2 in ast_list:
                    if ast2[0] == tmp:

                        # lock asteroid
                        lock_asteroid(ast2)
                        count += 1

                if count == 6:
                    break
                tmp = file.readline().strip()
            # sometimes, it does not find anything on the second page and te menue stays open, this is to prevent that
            if count == current:
                device_click_rectangle(465, 431, 32, 5)
            file.close()
        return 0
# todo
def belt_handling():
    time_screen_freeze = time.time()
    last_cargo = 0
    while 1:
        print(' mining_in_belt()')
        wait_and_watch_out()

        # check if time is up
        if get_cargo() > 95 or time.time() - time_farming > 30 * 60.:
            loot()
            deactivate_the_modules('harvest')
            return

        if time_screen_freeze + 180 < time.time():
            time_screen_freeze = time.time()
            if get_cargo() == last_cargo:
                # does the screen react?  open and close inventory
                device_click_rectangle(5, 61, 83, 26)
                for i in range(5):
                    time.sleep(1.5)
                    device_update_cs()
                    if get_inventory_open():
                        does_react = 1
                        break
                    if i == 4:
                        hard_reset()

            close_pop_ups()

        # check if mining equipment is busy/ easily activated
        miners_active = 1
        for module in get_module_list():
            if module[1] == 'harvest' and miners_active:
                if not get_module_is_active(module):
                    if not get_is_locked(1):
                        miners_active = 0
                        break
                    wait_and_watch_out(4)
                    if not get_module_is_active(module):
                        activate_module(module)
                        wait_and_watch_out(2)
                        if not get_module_is_active(module):
                            miners_active = 0
                            break

        wait_and_watch_out()

        if not miners_active:
            loot()
            if get_cargo() > 85:
                return
            if get_is_locked(1) or get_is_locked(2):
                if approach_and_start_harvest():
                    print('something went wrong, no target asteroid?')
            else:
                loot()
                return
        else:
            wait_and_watch_out(10)
def mining_return(got_ganked):
    print(' mining_return()')
    # activate autopilot and run (maybe i got ganked?)
    if got_ganked == 1:
        print('got ganked')
        escape_autopilot()
        ding_when_ganked()
        save_screenshot()
    else:
        return_autopilot()
    device_update_cs()

    # catch notification window
    for i in range(10):
        if get_is_in_station() == 0:
            close_pop_ups()
        else:
            break
        time.sleep(2)

    print('arriving')
    # dump ressources
    farm_tracker()
    global inv_dump_time
    if inv_dump_time > time.time() + 10000:
        inv_dump_time = time.time()
        dump_both()
    else:
        if get_cargo() > 0:
            dump_ore()
    # repeat?
    if get_repeat() == 0:
        playsound(Path_to_script + 'assets\\sounds\\bell.wav')
        quit()
    if got_ganked == 1:
        print('waiting ' + str(safety_time) + 's')
        time.sleep(get_safety_time())

    for i in range(10):
        if get_is_in_station() == 0:
            close_pop_ups()
        else:
            break
        time.sleep(2)

    mining_from_station()
def test_esc():
    set_filter('ing', 0)
    device_toggle_eco_mode()
    wait_and_watch_out(200)
    device_toggle_eco_mode()
    mining_return(0)
    print(' test_esc()')

def mining_from_station_in_null():
    print(' mining_from_station_in_null()')
    # set destination
    set_pi_planet_for_autopilot(get_planet())
    # wait until autopilot gone
    wait_end_navigation(20)
    print('undocking')
    device_click_rectangle(817, 165, 111, 26)
    time.sleep(15)

    print('calibrating')
    device_update_cs()
    activate_filter_window()
    time.sleep(1)
    update_modules()

    print('going to system')
    device_update_cs()
    # activate autopilot
    activate_autopilot(0)
    # wait until autopilot gone
    wait_end_navigation(20)

    print('todo')
    # todo

# STARTS
def main():
    mining_from_station()
def custom():
    update_modules()
    the_module = None
    for module in get_module_list():
        if module[1] == 'prop':
            the_module = module
    while 1:
        time.sleep(2)
        device_update_cs()
        deactivate_module(the_module)


read_config_file()
config_uni()
if get_start() == 'main':
    main()
if get_start() == 'custom':
    custom()
