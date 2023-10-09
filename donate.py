# from account import *
from attacks import *
from sql import *
from account import *
# from war import *

def add_to_dict(dict, key, amount):
    if key in dict:
        dict[key] += amount
    else:
        dict[key] = amount
    return dict

def empty_count():
    count = {}
    for troop in troops:
        count[troop] = 0
    return count

def print_count(label, count):
    string = label + ": "
    for key in count:
        if count[key] > 0:
            string += f"{key}:{count[key]}. "
    print(string)

def subtract_dictionaries(dict_1, dict_2):
    return {key: dict_2[key] - dict_1.get(key, 0) for key in dict_2.keys()}


def get_requestor_name(y):
    name_region = (100, y - 200, 200, 150)
    screen = get_screenshot(name_region)
    max_val = 0.5
    max_member = None
    for x in members:
        val, loc, rect = find(x.i_chat, screen)
        if val > max_val:
            max_val = val
            max_member = x
    return max_member

def donate_get_required_troops(account):
    goto(chat)
    required_troops = []
    donate_buttons = i_donate.find_many()
    for x, y, w, h in donate_buttons:
        region = (138, y - 150, 560, 120)
        screen = get_screenshot(region)
        # show(screen)
        for troop in troops:
            if troop.type == "siege" and not account.has_siege: continue
            if troop.i_donate1 is None or troop.i_donate1.image is None: continue
            if troop.currently_training: continue
            show_image = False
            if troop == minion: show_image = False
            val, loc, rect = find(troop.i_donate1.image, screen, text=troop.name, show_image=show_image)
            if val > 0.65:
                # print("Required troop:", troop)
                if troop not in required_troops:
                    required_troops.append(troop)
                if troop.donation_count == 0: troop.donation_count = 1
    # print("Donate (get troops):", troop_str(required_troops))
    return required_troops

def donate_train_required_troops(account, required_troops):
    time.sleep(0.2)
    time_required = 20 * 60
    # print("Donate - train required troops")
    for troop in required_troops:
        # print("Donate - train required troops:", troop.name.capitalize())
        if troop.type == "siege":
            if not account.has_siege: continue
        if troop.i_training.find(fast=True):
            print("Already training:", troop.name)
            troop.currently_training = True
        else:
            troop.start_train(count=1, account=account)
            if troop == required_troops[0]:
                move_to_queue_start(troop)
                time_required = troop.training_time
    return time_required

def donate_give_required_troops(required_troops):
    goto(chat)
    end_time = datetime.now() + timedelta(minutes=3)
    requests = find_many("donate", DONATE_BUTTONS, 0.8)
    while datetime.now() < end_time and len(required_troops) > 0:
        # print("Donate - give", troop_str(required_troops))
        for x in requests:
            click_rect(x)
            time.sleep(0.4)
            # print("Required troops", troop_str(required_troops))
            for x in required_troops:
                if x.i_donate2.find() and x.i_donate2.check_colour():
                    x.i_donate2.image.click()
                    pag.move(755,322)
                    time.sleep(0.1)
                    x.donations += 1
                    x.currently_training = False
                    required_troops.remove(x)
            i_donate_cross.click()
            time.sleep(10)

def check_troop_colour_donate(troop):
    val, loc, rect = troop.i_donate2.find_detail(fast=True)
    rect_adj = [rect[0] + DONATE_AREA[0], rect[1] + DONATE_AREA[1], rect[2], rect[3], ]
    colour = check_colour_rect(rect_adj, show_image=False, text=troop.name)
    return colour

# def donate_go_up():
#     goto(chat)
#     val, loc, rect = i_more_donates.find_detail()
#     if val > i_more_donates.threshold:
#         rect_adj = [rect[0] + DONATE_BUTTONS[0], rect[1] + DONATE_BUTTONS[1], rect[2], rect[3], ]
#         click_rect(rect_adj)
#         time.sleep(0.5)

# def message():
#     donator = donating_account()
#     if donator == account_1: message = "The bot is on, request dragons, edrags, super barbs and log rollers"
#     elif donator == account_2: message = "The bot is on, request dragons, edrags and super barbs"
#     elif donator == account_3: message = "The bot is on, request dragons, edrags and super barbs"
#     elif donator == account_4: message = "The bot is on, request dragons"
#     else: return
#     print("Clan message:", donator, message)
#     message_send(message)

# def message_send(text):
#     goto(chat)
#     if not i_new_message.click(): return
#     time.sleep(0.1)
#     pag.write(text)
#     pag.press('enter')
#     time.sleep(2)

def print_training():
    for troop in troops:
        if troop.currently_training: print("Currently training:", troop.name)

def donate(account):
    # donate_go_up()
    donate_basic(account)
    if not account.donating:
        db_update(account, "donate", datetime.now() + timedelta(days=1))
        return
    required_troops = donate_get_required_troops(account)
    print("Required troops")
    print(objects_to_str(required_troops))
    queue_up_troops(account, extra_troops=required_troops)
    for account_x in accounts:
        if account_x.number > account.number and not account_x.has_siege and not account_x.mode == "donate" and admin.war_donations_remaining == 0:
            db_update(account_x, "donate", datetime.now() + timedelta(minutes=30))

    # db_update(account, "donate", datetime.now() + timedelta(minutes=20))

def queue_up_troops(account, extra_troops=[]):
    for troop in extra_troops:
        troop.donations += 1
    account.update_troops_to_build()
    army_prep(account, account.troops_to_build, army_or_total="total")
    if account.has_siege:
        siege_prep(account)

def print_total_donations():
    print("\nTOTAL DONATIONS")
    for troop in troops:
        if troop.donations > 0:
            print(f" - {troop.name}s: {troop.donations}")

def donate_basic(account):
    # print("Donate")
    goto(chat)
    # i_accept.click()
    donate_buttons = i_donate.find_many()
    # print("Donate request buttoms:", donate_buttons)
    start_time = datetime.now()
    for x, y, w, h in donate_buttons:
        pag.click(x + w/2, y + h/2)
        region = (160, y - 150, 560, 120)
        time.sleep(0.3)
        for troop in troops:
            if troop.donate_bool:
                screen = get_screenshot(DONATE_AREA, colour=0)
                show_image = False
                if troop == super_barb: show_image = False
                val, loc, rect = find(troop.i_donate2.image, screen, troop.name, show_image=show_image)
                # print("Donate basic:", troop.name, round(val,2), datetime.now() - start_time)
                if val > 0.65:
                    count = 0
                    screen = get_screenshot(DONATE_AREA, colour=1)
                    image_colour = screen[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]
                    colour = check_colour_screen(image_colour)
                    # if not colour and account == account_1 and troop == log_thrower:
                    #     new_attack_time = datetime.now() + timedelta(hours=1)
                    #     for account in accounts:
                    #         db_update(account, "attack", new_attack_time + timedelta(minutes=account.number * 5))
                    #     print("No log-rollers - resetting attack times")
                    # print(troop.name, val, colour)
                    while colour and count < 10:
                        # print("Donate - clicking:", troop.name)
                        click(troop.i_donate2.image, DONATE_AREA)
                        troop.donations += 1
                        time.sleep(0.1)
                        count += 1
                        if troop.type == "siege": count += 10
                        image_colour = get_screenshot(DONATE_AREA, colour=1)[rect[1]:rect[1] + rect[3], rect[0]:rect[0] + rect[2]]
                        colour = check_colour_screen(image_colour)

        i_donate_cross.click()
        # print("Donate:", datetime.now() - start_time)
        time.sleep(0.2)

def check_colour_screen(image):
    spots = [(1 / 4, 1 / 4), (1 / 4, 3 / 4), (3 / 4, 1 / 4), (3 / 4, 3 / 4), (7 / 8, 1 / 8), (0.95, 0.05)]
    count = 0
    y, x, channels = image.shape
    for s_x, s_y in spots:
        pixel = image[int(y * s_y)][int(x * s_x)]
        blue, green, red = int(pixel[0]), int(pixel[1]), int(pixel[2])
        if abs(blue - green) > 5 or abs(blue - red) > 5: count += 1
        # print("Check colour screen", blue, green, red, count)
    colour = False
    if count > 1: colour = True
    # print("Check colour", colour)
    return colour

def siege_prep(account):
    if not account.has_siege: return
    required_counter = Counter(account.siege_troops)
    actual_counter = troops_count_flex(army_tab, ARMY_EXISTING, siege_troops)
    actual_counter = troops_count_flex(siege_tab, TRAINING_RANGE_SIEGE, siege_troops, actual_counter)
    print_count("Required", required_counter)
    print_count("Actual", actual_counter)
    for x in required_counter:
        if x.type == "siege":
            try: actual = actual_counter[x]
            except: actual = 0
            required = required_counter[x]
            if required > actual:
                x.start_train(required - actual, account=account)

def army_prep(account, required_army, army_or_total="army", include_castle=False, include_backlog=True, troops_only=False, extra=False):
    # print("Army prep")

    troops_to_build = []

    # Get required troops
    required_counter = Counter(required_army)

    # Get actual troops
    actual_army_counter, actual_total_counter = full_count(account, include_castle=include_castle)
    # print("Actual", actual_army_counter)
    # print("Actual (total)", actual_total_counter)
    if actual_army_counter == "Still training":
        print("Still training")
        return False, None
    if army_or_total == "army": actual_troops = actual_army_counter
    else: actual_troops = actual_total_counter

    print_count("Actual", actual_troops)

    # Create needed troops
    print_count("Required", required_counter)
    sufficient_troops = True
    sufficient_spells = True
    for x in required_counter:
        if x.type == "siege" and not account.has_siege: continue
        if x and x.type != "hero":
            try: actual = actual_troops[x]
            except: actual = 0
            required = required_counter[x]
            text = ""
            if actual < required:
                text = f"Need more of these - make {required - actual} more"
                # print("Army prep:", x, required, actual, text)
                if x.type == "troop": sufficient_troops = False
                if x.type == "spell": sufficient_spells = False
            troops_to_build += [x] * (required - actual)
    # print("Army prep - troops to build:", troop_str(troops_to_build))

    if not sufficient_troops:
        # Delete unneeded troops
        backlog_deleted = False
        for x in troops:
            if x.type == "spell" or x.type == "siege": continue
            try: actual = actual_troops[x]
            except: actual = 0
            required = required_counter[x]
            if actual > required:
                print("Attack prep - delete unneeded troops:", x.name, required, actual)
                if not backlog_deleted: troop_delete_backlog()
                backlog_deleted = True
                x.delete(actual - required)

    if not sufficient_spells:
        # Delete unneeded spells
        for x in troops:
            if x.type == "troop" or x.type == "siege": continue
            try: actual = actual_troops[x]
            except: actual = 0
            required = required_counter[x]
            if actual > required:
                # print("Attack prep - delete unneeded spells", x.name, required, actual)
                x.delete(actual - required)

    restock(troops_to_build, account, extra=extra)

    return sufficient_troops, actual_troops

def troops_count_flex(tab, region, troops, count_dict={}, show_image=False, show_image_numbers=False):
    goto(tab)
    screen = get_screenshot(region)
    print_count("Troops count flew", count_dict)
    for troop in troops:
        if troop.i_army is None:
            print("Troops count flex: couldn't find file:", troop.name)
            continue
        if tab == army_tab:
            result, loc = troop.i_army.find_screen(screen, return_location=True, show_image=show_image)
            # if troop.name == "super_barb":
                # print("Super Barb:", result)
                # show(troop.i_army.image)
            if result:
                x = max(loc[0] - 30, 0)
                numbers_image = screen[0: 75, x: x + 130]
                result = troop_numbers.read_screen(numbers_image, return_number=True, show_image=show_image_numbers)
                # print(troop, result)
                if result > 200: result = int(result / 10)
                add_to_dict(count_dict, troop, result)
        else:
            rectangles = troop.i_training.find_screen_many(screen, show_image=show_image)
            for loc in rectangles:
                x = max(loc[0] - 30, 0)
                numbers_image = screen[0: 70, x: x + 130]
                # show(numbers_image)
                result = troop_numbers.read_screen(numbers_image, return_number=True, show_image=show_image_numbers)
                # print("Troop count flex", result)
                if result > 200: result = int(result / 10)
                add_to_dict(count_dict, troop, result)
                # print(count_dict)

    return count_dict

def full_count(account, include_castle=True):
    # print("Full count - start")
    count = empty_count()
    if still_training(account, just_troops=True): return "Still training", "Still training"
    count = troops_count_flex(army_tab, ARMY_EXISTING, just_troops, count)
    if account.th >= 5:
        count = troops_count_flex(army_tab, SPELLS_EXISTING, spells, count)
        count = troops_count_flex(army_tab, ARMY_EXISTING, siege_troops, count)
    if include_castle:
        count = troops_count_flex(army_tab, CASTLE_TROOPS, siege_troops, count)
    count_no_backlog = count.copy()
    count = troops_count_flex(troops_tab, TRAINING_RANGE, just_troops, count)
    if account.th >= 5:
        count = troops_count_flex(spells_tab, TRAINING_RANGE, spells, count)
    if account.has_siege:
        count = troops_count_flex(siege_tab, TRAINING_RANGE_SIEGE, siege_troops, count)
    count_with_backlog = count
    return count_no_backlog, count_with_backlog

def still_training(account, just_troops=False):
    if account.has_siege: tabs = [troops_tab, spells_tab, siege_tab]
    else: tabs = [troops_tab, spells_tab]
    if just_troops: tabs = [troops_tab]
    for tab in tabs:
        goto(tab)
        if i_army_clock.find(show_image=False): return True
    return False

def army_count(account):
    if still_training(account, just_troops=True): return "Still training"
    count = empty_count()
    count = troops_count_flex(army_tab, ARMY_EXISTING, just_troops, count)
    count = troops_count_flex(army_tab, SPELLS_EXISTING, spells, count)
    count = troops_count_flex(army_tab, ARMY_EXISTING, siege_troops, count)
    count = troops_count_flex(army_tab, CASTLE_TROOPS, siege_troops, count)
    print_count("Army count:", count)
    return count

def troop_delete_backlog():
    print("Delete Backlog")
    goto(troops_tab)
    remaining_troops = True
    while remaining_troops:
        val, loc, rect = i_remove_troops.find_detail()
        # print("Troop delete backlog:", val)
        center = pag.center(rect)
        if val > 0.75:
            for x in range(5): pag.click(center)
        else:
            remaining_troops = False

def siege_in_castle(account):
    for siege in [ram, log_thrower]:
        if siege.in_castle(): return siege

def restock(required_troops, account, extra=True):
    count = Counter(required_troops)
    extra_troops = []
    if extra:
        extra_troops = count.most_common()
    # print("Extra:", extra)

    for x in count:
        # if count[x] == 0: continue
        if x.type == "siege" and not account.has_siege: continue
        x.start_train(count[x], account=account)

    if extra and len(extra_troops) > 0:
        troop = extra_troops[0][0]
        number = extra_troops[0][1]
        troop.start_train(number, account=account)

# === 2. REQUEST ===
def request(account):
    # print("Request")
    goto(army_tab)
    val, loc, rect = i_army_request.find_detail()
    print("Request: 'request' val", val)
    if val > 0.7:
        if i_army_request.check_colour():
            i_army_request.click()
            time.sleep(1)
            if not i_castle_send.click():
                print("Request - couldn't find request button")
        else:
            print("Request - Check colour failed")
    else:
        print("Request - couldn't find request", val)

    job_time = datetime.now()
    db_update(account.donations_from, "donate", job_time, use_account_number=True)


castle_slide_pos = 1
def castle_slide(position):
    global castle_slide_pos
    distance = position - castle_slide_pos
    if distance == 0: return
    for x in range(abs(distance)):
        if distance > 0: castle_slide_right()
        else: castle_slide_left()
    castle_slide_pos = position

def castle_slide_right():
    pag.moveTo(1420, 500, 0.3)
    pag.dragTo(450, 500, 1.0, button="left")

def castle_slide_left():
    pag.moveTo(450, 500, 0.3)
    pag.dragTo(1420, 500, 1.0, button="left")

def convert_list_to_troop_count(list):
    count = empty_count()
    for troop in list:
        add_to_dict(count, troop, 1)
    return count

def castle_troops_change(required_troops):
    global castle_slide_pos
    castle_slide_pos = 1
    goto(army_tab)
    if not i_army_request.find():
        print("Not ready for request")
        return
    to_delete, to_add = calc_castle_troops_to_change(required_troops)

    castle_troops_remove(to_delete)
    castle_troops_add(to_add)

def calc_castle_troops_to_change(required_castle_troops):
    required = convert_list_to_troop_count(required_castle_troops)
    existing = castle_troops_existing()
    print_count("Castle Troops - Required", required)
    print_count("Castle Troops - Existing", existing)
    to_delete = subtract_dictionaries(required, existing)
    to_add = subtract_dictionaries(existing, required)
    print_count("Delete", to_delete)
    print_count("Add", to_add)
    return to_delete, to_add

def valid_troop_for_castle_removal(troop):
    if troop.type == "troop":
        return True
    if troop.type == "siege" and troop != log_thrower:
        return True
    if troop.type == "spell" and troop != lightening:
        return True
    return False

def castle_troops_remove(troops_to_remove):
    goto(army_tab)
    time.sleep(.2)
    # Return if there are no troops to remove
    no_of_troops_to_remove = 0
    for troop in troops_to_remove:
        if valid_troop_for_castle_removal(troop):
            no_of_troops_to_remove += troops_to_remove[troop]
    if no_of_troops_to_remove == 0:
        return

    i_army_edit.click()
    time.sleep(.2)

    for troop in troops_to_remove:
        if not valid_troop_for_castle_removal(troop): continue
        number_of_troops = troops_to_remove[troop]
        if number_of_troops > 0:
            print("Removing:", troop)
            for x in range(number_of_troops):
                troop.i_army.click_region(CASTLE_TROOPS)
                time.sleep(0.05)
    i_army_okay.click()
    time.sleep(0.1)
    i_army_okay2.click()

    return True

def castle_troops_add(to_add):
    if i_army_tab_cancel.find():
        i_army_tab_cancel.click()
    i_army_request.click()
    time.sleep(0.2)
    i_army_donate_edit.click()

    # Remove the previous troops
    remaining_troops, count = True, 0
    while remaining_troops and count < 20:
        if i_remove_troops.find():
            i_remove_troops.click()
        else:
            remaining_troops = False

    for troop in to_add:
        if to_add[troop] > 0:
            castle_slide(troop.castle_slide)
            time.sleep(0.3)
            print("Castle", troop, troop.i_castle.find_detail(fast=False))
            for _ in range(to_add[troop]):
                troop.i_castle.click_region(CASTLE_REQUEST_AREA_2)
            time.sleep(.2)
    multi_click([i_castle_confirm, i_castle_send])

def castle_troops_existing():
    goto(army_tab)
    count = empty_count()
    count = troops_count_flex(army_tab, CASTLE_TROOPS, troops, count, show_image=False)
    print_count("Existing", count)
    return count




# def castle_troops_current():
#     screen = get_screenshot(CASTLE_TROOPS)
#     current_troops = []
#     for troop in [super_barb, dragon, bloon, lightening, freeze]:
#         result, loc = troop.i_army.find_screen(screen, return_location=True)
#         if result:
#             x = max(loc[0] - 30, 0)
#             numbers_image = screen[0: 50, x: x + 130]
#             result = troop_numbers.read_screen(numbers_image, return_number=True)
#             for x in range(result):
#                 current_troops.append(troop)
#     return current_troops
#
# def castle_troops_delete(troops_to_delete):
#     print(len(troops_to_delete))
#     if len(troops_to_delete) == 0: return
#     # Delete existing
#     i_army_edit.click()
#     for troop in troops_to_delete:
#         troop.i_army.click_region(CASTLE_TROOPS)
#     i_army_okay.click()
#     time.sleep(0.2)
#     i_surrender_okay.click()


# change_castle_troops([super_barb] * 7 + [lightening])
# castle_troops_change([dragon, bloon, bloon, bloon, freeze])

# goto(army_tab)
# i_army_request.click()
# time.sleep(0.1)
# i_army_donate_edit.click()
# time.sleep(5)
# castle_troops_change([dragon, bloon, bloon, bloon])

# goto(army_tab)
# goto(pycharm)

