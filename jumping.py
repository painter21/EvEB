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
                    if 'aunt' in raw_text:
                        list_ano.append(['haunted', lvl, filter_list_nr])
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

# STARTS
def main():
    return
def custom():
    device_update_cs()
    get_list_anomaly()


read_config_file()
config_uni()
if get_start() == 'main':
    main()
if get_start() == 'custom':
    custom()
