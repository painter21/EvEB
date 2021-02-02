from universal_small_res import *
Path_to_script = ''
# variables
if 1:
    current_system = 'Start'
    next_system = ""
    solar_map = []
    searching_path = []
    ignore_inquis = 1
    ignore_scouts = 1
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
def read_path_file():
    print('\tread_path_file()')
    file = open('path.txt')
    tmp = file.readline().split()
    while len(tmp) != 0:
        if len(tmp) > 1:
            tmp[1] = int(tmp[1])
        searching_path.append(tmp)
        tmp = file.readline().split()
    print(searching_path)
    file.close()


# todo: read map, write map
def wait_jump():
    time.sleep(7)
    device_update_cs()
    if get_speed() == 0:
        return 1
    for i in range(30):
        device_update_cs()
        if get_gate_cloak():
            time.sleep(7)
            device_update_cs()
            return 0
        else:
            time.sleep(3)
    device_update_cs()
    if get_is_in_station() == 1:
        main()
    return 0
def filter_stargate_warp(target_nbr, current_system_index=0):

    gate_is_close = 0
    if current_system_index > 1:
        if searching_path[current_system_index][0] == searching_path[current_system_index - 2][0]:
            gate_is_close = 1

    for i in range(3):
        if gate_is_close:
            filter_action(target_nbr, 2, 5)
        else:
            filter_action(target_nbr, 1, 2)

        print("should call wait jump")
        if wait_jump() == 0:
            return

    for i in range(3):
        if gate_is_close:
            filter_action(target_nbr, 1, 2)
        else:
            filter_action(target_nbr, 2, 5)
        if wait_jump() == 0:
            return
    return
def click_gate_icon():
    # get stargate list: search the stargate icon and click on it
    current_stargate_icon_location = get_filter_icon("stargate")
    if current_stargate_icon_location == 0:
        ding_when_ganked()
        print('stargate icon not found, loaded too slowly, something else? (L.47 jumping)')
        quit()
    device_click_rectangle(current_stargate_icon_location[0] + 1, current_stargate_icon_location[1] + 1, 9, 13)
    device_update_cs()


# maybe later useful
def get_gates():
    # todo: swap filter?

    click_gate_icon()

    # read all Gate Texts:
    list_gate = []
    x_start_filter_text = 793
    x_estimated_text_size, y_estimated_text_size = 120, 25
    for pixel_found in get_filter_pos():
        text_img = get_cs_cv()[
                   pixel_found[1]:pixel_found[1] + y_estimated_text_size,
                   x_start_filter_text:x_start_filter_text + x_estimated_text_size]
        raw_text = tess.image_to_string(text_img)
        raw_text = ''.join([i for i in raw_text.strip() if not i.isdigit()])
        if len(raw_text) < 2:
            text_img = image_remove_dark(text_img, 200)
            raw_text = tess.image_to_string(text_img)
            raw_text = raw_text.strip().replace("\n", "")
            raw_text = ''.join([i for i in raw_text if not i.isdigit()])
        print(raw_text)
        list_gate.append(raw_text)
    return list_gate
def write_map(string):
    file = open(path + '\\map.txt', 'a')
    file.write(string)
    file.close()

def main():
    read_path_file()
    if get_is_in_station():
        undock_and_modules(expected_modules=0)
        time.sleep(5)
    activate_filter_window()
    set_filter('Nav', 1, 0)
    time.sleep(5)
    for i in range(len(searching_path)):
        print("\tcheck anomalies")
        # check anomalies
        device_update_cs()
        get_list_anomaly()
        print("\twarp to next system")
        # warp to next path system
        print("\t\tnext system", searching_path[i])
        if len(searching_path[i]) == 2:
            click_gate_icon()
            filter_stargate_warp(searching_path[i][1], i)
        else:
            gate_list = get_gates()
            # comparing strings and looking for best one
            best_gate_nbr = 1
            best_gate_score = -10
            for gate_count in range(len(gate_list)):
                if (tmp_score := compare_strings(gate_list[gate_count], searching_path[i][0])) > best_gate_score:
                    best_gate_nbr = gate_count + 1
                    best_gate_score = tmp_score
                print('\t', searching_path[i][0], gate_list[gate_count], tmp_score)
            if best_gate_score < -30:
                ding_when_ganked()
                print(searching_path[i], gate_list[best_gate_nbr], best_gate_score)
                time.sleep(5)
            time.sleep(1)
            filter_stargate_warp(best_gate_nbr, i)
        print('\n\nexpected system: ', searching_path[i])
        print('found gatecloak, scanning new system')
    set_home()
    time.sleep(5)
    device_update_cs()
    activate_autopilot(force_click=1)

    time.sleep(5)
    device_update_cs()
    if get_speed() < 20:
        activate_autopilot()
    for i in range(500):
        device_update_cs()
        if get_is_in_station():
            main()
        get_list_anomaly()
        time.sleep(20)
    ding_when_ganked()
def custom():
    set_home()
    time.sleep(5)
    device_update_cs()
    activate_autopilot(force_click=1)


read_config_file()
config_uni()
if get_start() == 'main':
    main()
if get_start() == 'custom':
    custom()
