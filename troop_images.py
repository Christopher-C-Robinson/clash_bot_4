from donate import *
from loc_constant_regions import *
from image_utilities import *
from people import *
import os
import shutil

train_directory = troop_directory + "/train/"
train_files = os.listdir(train_directory)
new_directory = troop_directory + "/new/"
new_files = os.listdir(new_directory)

def delete_army_troops(region):
    goto(army_tab)
    time.sleep(0.2)
    found = True
    no_to_delete = 1
    while found:
        i_army_edit.click()
        time.sleep(0.3)
        if not i_remove_troops_army.click_region(region, show_image=False):
            print("Not found:", i_remove_troops_army, i_remove_troops_army.find_detail())
            found = False
            time.sleep(0.2)
            i_army_okay.click()
            i_army_tab_cancel.click()
            time.sleep(0.1)
        else:
            for x in range(no_to_delete):
                i_remove_troops_army.click_region(region)
                no_to_delete = min(8, 2 * no_to_delete)
            time.sleep(0.1)
            i_army_okay.click()
            time.sleep(0.1)
            i_army_okay2.click()

def delete_castle_request_troops():
    goto(l_donation_request_selector)
    found = True
    while found:
        if not i_remove_troops_castle.click_region(CASTLE_REQUEST_AREA_1):
            found = False

# def wait_for_colour(region):
#     found, count = False, 0
#     while not found and count < 1000:
#         result = colour_fancy(region)
#         print(result)
#         if result > 28: return
#         time.sleep(0.3)

def wait_for_clock():
    goto(army_tab)
    count = 0
    while count < 1000:
        result = i_army_clock.find()
        print(result)
        if not result: return
        time.sleep(0.3)

def create_image_library(troop, account_1, attack_required=True):
    global current_location
    # load_troops()
    file = f"{troop.name}_"
    # base_image = troop.i_train.image[:, 10:105]
    set_current_account()
    change_accounts_fast(account_1)
    delete_army_troops(ARMY_EXISTING_NOT_SIEGE)
    delete_army_troops(SPELLS_EXISTING)
    delete_army_troops(CASTLE_TROOPS)
    # Training
    print("\nTraining")
    troop.start_train(1, account_1)
    time.sleep(0.5)
    get_screenshot_troop(TRAINING_RANGE_FIRST_TROOP, file + "training")
    # Army
    print("\nArmy")
    goto(army_tab)
    wait_for_clock()
    time.sleep(4)
    result, loc = get_image_variable_size(troop, type="army", region=ARMY_SPELLS_EXISTING)
    if not result:
        print("Failure:", troop, "Army")
    # Attack
    print("\nAttack")
    if attack_required:
        goto(find_a_match)
        result, loc = get_image_variable_size(troop, type="attack")
        if not result:
            print("Failure:", troop, "Attack")
    print("\nCastle")
    goto(l_donation_request_selector)
    delete_castle_request_troops()
    castle_slide(troop.castle_slide)
    time.sleep(0.3)
    result, loc = get_image_variable_size(troop, "castle", region=CASTLE_REQUEST_AREA_2)
    if result:
        pag.click(loc)
        time.sleep(0.3)
        i_castle_confirm.click()
        time.sleep(0.3)
        i_castle_send.click()
        time.sleep(0.3)
        # current_location = main
        change_current_location(main)
        # goto(army_tab)
        time.sleep(0.3)
    else:
        print("Failure:", troop, "Castle")
    # Donate 1
    print("\nDonate 1")
    print(current_location)
    time.sleep(0.2)
    goto(chat)
    result, loc = get_image_variable_size(troop, type="donate1", region=CHAT_AREA)
    if not result:
        print("Failure:", troop, "Donate 1")
    # Donate 2
    print("\nDonate 2")
    goto(l_donate)
    result, loc = get_image_variable_size(troop, type="donate2", region=DONATE_AREA)
    if not result:
        print("Failure:", troop, "Donate 2")
    determine_required_troop_types(troop)



# def create_troop_image(troop):
#     print(troop)
#     file = f"{troop.name}_"
#     change_accounts_fast(bad_daz)
#     goto(l_donate)
#     adj_image = cv2.resize(troop.i_army.image, (0, 0), fx=0.87, fy=0.87)
#     screen = get_screenshot()
#     result = cv2.matchTemplate(screen, adj_image, method)
#     min_val, val, min_loc, loc = cv2.minMaxLoc(result)
#     if val > 0.8:
#         region = (loc[0] - 10, loc[1], 80, 35)
#         get_screenshot_troop(region, file + "donate2")
#     else:
#         print("Failure:", troop, "Donate 2")
#         return

# def create_image_libraries(troops_to_create):
#     change_accounts_fast(bad_daz)
#     troop_delete_backlog()
#     for troop in troops_to_create:
#         create_image_library(troop)

def find_image_multiple(loc, troop):
    base_image = troop.i_train.image[:, 10:105]
    goto(loc)
    screen = get_screenshot()
    goto(pycharm)
    for scale in range(65, 105, 1):
        adj_image = cv2.resize(base_image, (0,0), fx=scale/100, fy=scale/100)
        result = cv2.matchTemplate(screen, adj_image, method)
        min_val, val, min_loc, loc = cv2.minMaxLoc(result)
        print(scale, val, loc)

# def copy_train_file(troop):
#     source = "images/troops_temp/" + f"{troop.name}_train.png"
#     destination = "images/troops/" + f"{troop.name}_train.png"
#     shutil.copy(source, destination)

def get_image_variable_size(troop, type, region=None):
    x1, x2, y1, y2 = -10, 110, 0, 65
    if type == "donate1": x1, x2, y1, y2 = -10, 90, 15, 35
    image = troop.i_train.image[:, 10:105]
    file = f"{troop.name}_"
    if region:
        screen = get_screenshot(region)
    else:
        screen = get_screenshot()
    max_val = 0
    max_scale = None
    max_loc = None
    results = []
    for scale in range(50, 109, 3):
        adj_image = cv2.resize(image, (0, 0), fx=scale / 100, fy=scale / 100)
        result = cv2.matchTemplate(screen, adj_image, method)
        min_val, val, min_loc, loc = cv2.minMaxLoc(result)
        if val > max_val:
            max_val = val
            max_loc = loc
            max_scale = scale
        results.append((scale, round(val,2)))
    print(f"Scale: {max_scale}, Val:{round(max_val, 2)}, Loc:{max_loc}")
    if max_val > 0.67:
        if region:
            image_region = (max_loc[0] + x1 + region[0], max_loc[1] + region[1] + y1, x2, y2)
        else:
            image_region = (max_loc[0] + x1, max_loc[1] + y1, x2, y2)
        print("Success", max_loc, image_region)
        get_screenshot_troop(image_region, file + type)
        return True, (image_region[0] + 5, image_region[1] + 5)
    else:
        print("Not saved", troop, type)
        for result in results:
            print(result)
        return False, max_loc

def determine_required_troop_types(troop):
    required_types = ["training", "donate1", "donate2", "attack", "castle", "army"]
    for image_type in ["training", "donate1", "donate2", "attack", "castle", "army"]:
        current_file = f"{troop.name}_{image_type}.png"
        if current_file in new_files:
            required_types.remove(image_type)
    if len(required_types) == 0:
        print("All images exist:", troop)
    else:
        print("Required image types:", troop, required_types)
    return required_types

def update_troop_files(action=True, account_number=0):
    count = account_number
    print("In train directory:", train_files)
    for troop in troops:
        if f"{troop.name}_train.png" in train_files:
            required_types = ["training", "donate1", "donate2", "attack", "castle", "army"]
            for image_type in ["training", "donate1", "donate2", "attack", "castle", "army"]:
                # print("Start:", troop, image_type)
                current_file = f"{troop.name}_{image_type}.png"
                if current_file in new_files:
                    required_types.remove(image_type)
                    # print("Removing", image_type, "Left:", required_types)
                else:
                    pass
                    # print("Couldn't find:", current_file)
            # print("Required images:", troop, required_types)
            if len(required_types) > 0:
                attack_required = True
                if "attack" not in required_types:
                    attack_required = False
                print("Work on:", troop, attack_required, required_types)
                if action:
                    # set_current_account()
                    create_image_library(troop, accounts[count], attack_required=attack_required)
                    count += 1
                    if count > 3:
                        goto(pycharm)
                        wait(2)
                        # time.sleep(5 * 60)
                        count = 0
    goto(pycharm)


# create_image_library(freeze, bad_daz, attack_required=True)


# print(headhunter.slide)

# time.sleep(5)
# update_troop_files(action=False, account_number=0)
# update_troop_files(action=True, account_number=1)

print(edrag.slide)

goto(pycharm)