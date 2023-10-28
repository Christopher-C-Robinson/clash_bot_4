from attacks_logic import *
from images import *
from admin import *

donations_senior = {
    45: [super_minion, super_minion, super_minion, minion, minion, super_barb],
    40: [super_minion, super_minion, super_minion, minion, minion],
    35: [super_minion, super_minion, minion, minion, minion, super_barb],
    33: [super_minion, super_minion, minion, minion, super_barb],
    28: [super_minion, super_minion, minion, minion],
    23: [super_minion, minion, minion, minion, super_barb],
    21: [super_minion, minion, minion, super_barb],
    16: [super_minion, minion, minion],
    11: [minion, minion, minion, super_barb],
    9: [minion, minion, super_barb],
    7: [minion, super_barb],
    6: [minion, minion, minion],
    5: [super_barb, ],
    4: [minion, minion],
    2: [minion, ],
    1: [archer, ],
}

donations_junior = {
    30: [edrag, ],
    25: [dragon, bloon],
    20: [dragon],
    15: [bloon, bloon, bloon],
    10: [bloon, bloon],
    5: [bloon],
    4: [minion, minion],
    2: [minion, ],
    1: [archer, ],
}

troops1 = ["edrag"] * 8 + ["dragon"] * 2 + ["lightening"] * 11
troops2 = ["dragon"] * 12 + ["balloon"] + ["lightening"] * 11
data = [(1, troops1), (2, troops2)]



def remove_clan_troops():
    goto(army_tab)
    i_army_edit.click()
    for x in range(9):
        super_barb.i_army.click_region(CASTLE_TROOPS, show_image=False)
    i_army_okay.click()
    time.sleep(0.2)
    i_army_okay2.click()
    time.sleep(0.2)

def war_prep(cwl=False):
    set_current_account()
    for account in [bad_daz, daz, bob, daen]:
        if cwl:
            troops = account.cwl_troops
        else:
            troops = account.war_troops
            troops_2 = troops + troops
        change_accounts_fast(account)
        goto(army_tab)
        remove_clan_troops()
        troop_delete_backlog()
        if cwl:
            army_prep(account, troops, army_or_total="total")
        else:
            army_prep(account, troops, army_or_total="army")
            army_prep(account, troops_2, army_or_total="total")
        castle_troops_change(account.clan_troops_war)

    change_accounts_fast(account_1)
    goto(pycharm)
    wait(1)
    for x in range(3):
        wait(6)
        donate_basic(account_1)
        goto(pycharm)

    army_prep(account_1, account_1.war_troops)

def has_barbs(dict):
    try:
        if dict[super_barb] > 0: return True
    except:
        pass


def train_war_troops(account, cwl=False):
    if account.mode != "war_troops": return
    clan_troops = troops_count_flex(army_tab, CASTLE_TROOPS, siege_troops)
    if has_barbs(clan_troops): remove_clan_troops()

    if admin.mode == "cwl":
        army_prep(account, account.cwl_troops, army_or_total="total")
    else:
        # Layer 1
        army_prep(account, account.war_troops, army_or_total="army")
        # Layer 2
        actual = troops_count_flex(troops_tab, TRAINING_RANGE, just_troops)
        print_count("Existing Layer 2", actual)
        if has_barbs(actual): troop_delete_backlog()

        expected = convert_list_to_troop_count(account.war_troops)
        required = subtract_dictionaries(actual, expected)
        for troop in required:
            if troop.type == "spell": required[troop] = 0
        restock(required, account)

    castle_troops_change(account.clan_troops_war)

def war_get_status_image():
    print("War get status image")
    goto(main)
    time.sleep(0.1)
    goto_war_screen()
    time.sleep(2)
    get_screenshot(WAR_BANNER, filename=f"tracker/war_banner")
    get_screenshot(WAR_INFO, filename=f"tracker/war_info")
    print("Saved war banner")

def set_admin_mode():
    # change_accounts_fast(account_1)
    war_get_status_image()

    status = "no war"
    war_banner = cv2.imread(f'temp/tracker/war_banner.png', 0)
    war_info = cv2.imread(f'temp/tracker/war_info.png', 0)
    # less_than_an_hour()
    if i_war_preparation.find_screen(war_banner, show_image=False):
        status = "preparation"
    elif i_war_battle_day.find_screen(war_banner) or i_war_battle_day.find_screen(war_banner):
        status = "battle_day"
    if i_season_info.find_screen(war_info, show_image=False):
        status = "cwl"
        # if i_cwl_last_day.find(): status = "battle_day"
    elif i_clan_wars.find(fast=False): status = "no war"
    # elif i_clan_wars_2.find(fast=False): status = "no war"
    admin.mode = status
    print("Set admin mode:", admin.mode)
    if status in ["preparation", "cwl"]:
        cwl = True
        if status == "preparation": cwl = False
        remaining = count_remaining_donations(cwl=cwl)
        print("Remaining donations:", remaining)
        admin.war_donations_remaining = remaining
    for x in range(2):
        if i_return_home_3.find():
            i_return_home_3.click()
            time.sleep(0.1)

def less_than_an_hour():
    result = war_time.read(region=WAR_BANNER, show_image=False)
    print("Text:", result)
    print("Time:", text_to_time_2(result, return_duration=True))
    try:
        result = text_to_time_2(result, return_duration=True) < timedelta(minutes=59)
    except:
        return timedelta(hours=24)
    admin.less_than_one_hour = result
    # print("Admin - less than one hour", admin.less_than_one_hour)
    return result


def donate_war(account):
    print("Donate war. Admin mode:", admin.mode)
    if admin.mode in ["battle_day", "no_war", ""]: return
    if admin.mode == "no war": return
    # print(f"'{admin.mode}' is not equal to 'no war'")
    if not account.cwl_donations_left: return
    if admin.war_donations_remaining == 0: return
    print("Donate war - count check:", admin.war_donations_remaining)
    if admin.mode == "cwl": result = war_donations(cwl=True)
    else: result = war_donations(cwl=False)
    if result in [20, 40]: result = 0
    for account in accounts:
        admin.war_donations_remaining = result
        account.set_mode(resource_update=False)
        queue_up_troops(account)


def get_required_troops(required, total):
    if total >= 35: dict = donations_senior
    else: dict = donations_junior

    try:
        return dict[required]
    except:
        return []

def print_troop_count(troops):
    troops.sort(key=lambda x: x.name)
    troops_counter = Counter(troops)
    string = ''
    for t in troops_counter:
        string += f"{t}s: {troops_counter[t]}, "
    print("Troops:", string[:-2])


# print_troop_count(get_required_troops(5, 35))

def count_remaining_donations(cwl=False):
    if admin.war_donations_remaining == 0: return 0
    result = goto_war_castle(cwl=cwl)
    if not result: return
    remaining_total = 0
    still_moving, count = True, 0
    required_troops = []
    while still_moving and count < 50:
        remaining, total = remaining_donations()
        required_troops += get_required_troops(remaining, total)
        print(remaining, total)
        remaining_total += remaining

        if i_war_right.colour() < 800: still_moving = False
        i_war_right.click()
        # pag.moveTo(1400,800)
        time.sleep(0.1)
        count += 1
    if count < 20 and remaining_total == 0: remaining_total = -1
    print("REMAINING DONATIONS:", remaining_total)
    admin.war_donations_remaining = remaining_total
    if admin.war_donations_remaining == 0: duration = timedelta(hours=2)
    else: duration = timedelta(minutes=2)
    print("War donation duration:", duration)
    for account in accounts:
        db_update(account, "donate_war", datetime.now() + duration)

    # i_return_home_3.click()
    return remaining_total

def war_donations(cwl=False):
    if admin.war_donations_remaining == 0: return 0

    if cwl: print("War donations for CWL")
    else: print("War donations")
    result = goto_war_castle(cwl=cwl)
    if not result: return

    remaining_total = 0
    still_moving, count = True, 0
    while still_moving and count < 50:
        remaining, total = remaining_donations()
        # remaining_total += remaining
        donation_list = []
        if remaining >= 45: donation_list = [lava_hound] + [super_barb] * 3
        elif remaining >= 40: donation_list = [lava_hound] + [super_barb] * 2
        elif remaining >= 35: donation_list = [lava_hound] + [super_barb]
        elif remaining >= 30: donation_list = [lava_hound]
        elif remaining >= 20: donation_list = [dragon]
        elif remaining >= 10: donation_list = [bloon] * 2
        elif remaining >= 5: donation_list = [bloon]
        elif remaining > 1: donation_list = [archer]
        donate_war_troops(donation_list)
        # print("Pre:", remaining, total)
        remaining, total = remaining_donations()
        print(remaining, total)
        remaining_total += remaining

        if i_war_right.colour() < 800: still_moving = False
        i_war_right.click()
        time.sleep(0.1)
        count += 1

    if count < 20 and remaining_total == 0: remaining_total = -1
    print("REMAINING DONATIONS:", remaining_total)
    admin.war_donations_remaining = remaining_total
    i_return_home_3.click()
    return remaining_total

def goto_war_screen():
    if i_return_home_3.find():
        return
    print("Goto war screen")
    goto(main)
    # print(current_location, main)
    # if current_location != main: return
    print("Got to main")
    found, count = False, 0

    while not found and count < 50:
        print("Goto war screen:", count, found)
        for image in [i_war, i_war_cwl]:
            if image.find():
                image.click()
                found = True
            else:
                print("Goto war screen:", image, image.find_detail())
        if i_return_home_3.find():
            found = True
        # print(i_war.find_detail(fast=False, show_image=True))
        time.sleep(0.1)
        count += 1
        # if x % 10 == 0: print(x)
    print("Finished goto war screen")

def goto_cwl_prep():
    print("Go to cwl prep")
    prep_found = False
    start_time = datetime.now()
    for x in range(5):
        if i_cwl_prep.find(fast=False):
            i_cwl_prep.click()
            prep_found = True
            break
        else:
            print("Prep find:", i_cwl_prep.find_detail())
        # if i_cwl_prep_2.find(fast=False):
        #     prep_found = True
        #     break
        time.sleep(0.1)
        if x % 3 == 0:
            print("Prep find (time required):", x, datetime.now() - start_time)
    if prep_found:
        return prep_found
    else:
        for x in range(20):
            if i_cwl_prep.find(fast=False):
                i_cwl_prep.click()
                print("Clicked prep")
                prep_found = True
                break
            # if i_cwl_prep_2.find(fast=False):
            #     i_cwl_prep_2.click()
            #     print("Clicked prep 2")
            #     prep_found = True
            #     break
            time.sleep(0.1)
    return prep_found

def goto_war_castle(cwl):
    print("Goto war castle")
    goto(main)
    goto_war_screen()

    if cwl:
        result = goto_cwl_prep()
        if not result: return result

    found, count = False, 0
    while not found and count < 5:
        if click_war_castle():
            print("Clicked Castle")
            found = True
        if not found:
            time.sleep(1)
        count += 1
    if not found: return False

    time.sleep(0.2)
    still_moving, count = True, 0
    while still_moving and count < 40:
        i_war_left.click()
        left_colour = i_war_left.colour()
        if left_colour < 700:
            print("CWL Donations - couldn't find left colour", left_colour)
            still_moving = False
        # time.sleep(0.1)
        count += 1
    return True

def click_war_castle():
    found = False
    # Fast loop
    for castle in war_castles:
        if castle.find(fast=True, show_image=False):
            castle.click()
            return True
        else:
            print(castle, castle.find_detail())
    # Slow loop
    for castle in war_castles:
        if castle.find(fast=False, show_image=False):
            castle.click()
            return True
        else:
            print(castle, castle.find_detail())

    return found

def remaining_donations():
    result = war_donation_count.read(WAR_DONATION_COUNT, show_image=False)
    # print("Remaining donations (pre):", result)
    # result = result.replace("b", "")
    # print("Remaining donations (post):", result)
    x_pos = result.find("x")
    try:
        received = int(result[0:x_pos])
        total = int(result[x_pos+1:])
    except:
        return 0,0
    return total - received, total

def donate_war_troop(troop):
    if not i_war_donate_reinforcements.find(fast=False):
        i_war_donate.click()
        time.sleep(0.1)
    troop.i_donate2.click_region(WAR_DONATION_AREA)

def donate_war_troops(troops):
    # print("Donate war troops")
    for x in troops:
        print(x)

    if i_war_request.find(): return

    if not i_war_donate_reinforcements.find(fast=False):
        if i_war_donate.colour() > 600:
            i_war_donate.click()
            time.sleep(0.1)
    for troop in troops:
        # print("Donate war troops", troop, troop.i_donate2.find_detail(), troop.i_donate2.colour())
        if troop.i_donate2.colour() > 300:
            troop.i_donate2.click_region(WAR_DONATION_AREA, show_image=False)
    time.sleep(0.1)



def war_status():
    set_admin_mode()
    print("War status:", admin.mode)
    if admin.mode in ["searching", "no war"]:
        i_return_home_3.click()
        return

    if admin.mode == "cwl":
        for account in war_participants:
            change_accounts_fast(account)
            if i_attacks_available.find():
                account.attacks_left = True
            else:
                account.attacks_left = False
            print(account, "attacks_left", account.attacks_left)
            change_accounts_fast(account)
            remaining = war_donations(cwl=True)
            print("REMAINING DONATIONS:", remaining)
            if remaining == 0:
                for a in accounts: a.cwl_donations_left = False
            else:
                for a in accounts: a.cwl_donations_left = True
            account.update_attacking()
            account.set_mode()
            queue_up_troops(account)
    elif admin.mode == "preparation":
        change_accounts_fast(account_1)
        if admin.war_donations_remaining != 0:

            remaining = war_donations(cwl=False)
            print("REMAINING DONATIONS:", remaining)
            admin.war_donations_remaining = remaining
    elif admin.mode == "battle_day":
        for account in war_participants:
            change_accounts_fast(account)
            if i_attacks_available.find():
                account.attacks_left = True
            else:
                account.attacks_left = False
            account.set_mode()
            queue_up_troops(account)
    else:
        for account in war_participants:
            account.cwl_donations_left = False
            account.set_mode()
            queue_up_troops(account)

    for account in accounts:
        if account not in war_participants:
            account.set_mode()
            queue_up_troops(account)


# def war_donations_ad_hoc():
#     print("War donations ad hoc")
#     goto(main)
#     i_war.click()
#     time.sleep(0.1)
#     if not i_war_preparation.find():
#         time.sleep(1)
#         if not i_war_preparation.find():
#             print("Couldn't find war preparation")
#             goto(main)
#             return 0
#     time.sleep(2)
#
#     for x in range(5):
#         found = click_war_castle()
#         if found: break
#         time.sleep(1)
#
#     if not found:
#         print("Couldn't find castle - war donation ad hoc")
#         goto(main)
#         return
#
#     still_moving, count = True, 0
#     while still_moving and count < 5:
#         i_war_left.click()
#         pag.moveTo(300,800)
#         if i_war_left.colour() < 800: still_moving = False
#         time.sleep(0.1)
#         count += 1
#
#     still_moving, count = True, 0
#     while still_moving and count < 35:
#         remaining, total = remaining_donations()
#         if remaining > 0:
#             # donations = [(edrag, 30, 50), (dragon, 20, 29), (ice_golem, 15, 19), (bloon, 10,14), (super_barb, 5, 9), (wizard, 4, 4), (archer, 1, 4)]
#             # for troop, min, max in donations:
#             #     if rem
#             if remaining >= 30:
#                 war_donations_donate_troop(edrag)
#                 remaining, total = remaining_donations()
#             elif remaining >= 20:
#                 war_donations_donate_troop(dragon)
#                 remaining, total = remaining_donations()
#             elif remaining >= 15:
#                 war_donations_donate_troop(ice_golem)
#                 remaining, total = remaining_donations()
#             elif remaining >= 10:
#                 war_donations_donate_troop(bloon)
#                 remaining, total = remaining_donations()
#             elif remaining >= 5:
#                 war_donations_donate_troop(super_barb)
#                 remaining, total = remaining_donations()
#             elif remaining >= 4:
#                 war_donations_donate_troop(wizard)
#                 remaining = remaining_donations()
#             elif remaining >= 1:
#                 war_donations_donate_troop(archer)
#                 war_donations_donate_troop(archer)
#                 war_donations_donate_troop(archer)
#                 war_donations_donate_troop(archer)
#
#         i_war_right.click()
#         pag.moveTo(1300,800)
#         if i_war_right.colour() < 800: still_moving = False
#         time.sleep(0.1)
#         count += 1
#     pag.press("esc")
#     return remaining
