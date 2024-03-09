from account import *
from lose_trophies import *
from donate import *
from people import *
from image_utilities import *
# from yolo import *

def return_account(number):
    return next((x for x in accounts if x.number == number), None)

# === 3. ATTACK ===

def attack_b_multi(account, count=5):
    for x in range(count):
        attack_b(account)
    get_war_elixir()
    goto(main)

def attack_b(account):
    global current_location
    goto(builder)
    result = goto(attacking_b)
    if result != attacking_b:
        print("Couldn't get to attack screen")
        return

    time.sleep(0.5)
    attack_b_get_screen()
    loc_th = th_b()
    if loc_th is None:
        loc_th = (1000,500)
        print("Failed to find TH - used default of 1000,500")
    a, b = objects_b(loc_th)
    for troop, n, loop in account.army_troops_b:
        result = place_b(troop, a, b, n, loop)
        if result == "No spots":
            print("Attack b - no spots")
            break

    # check_all_troops_used(a, b)
    still_going, count = True, 0
    while still_going and count < 90:
        if i_two_stars.find():
            # i_surrender_b.click()
            i_end_battle_b.click()
            time.sleep(0.5)
        if i_surrender_b_okay.find():
            i_surrender_b_okay.click()
            still_going = False
        if i_return_home_b.find():
            still_going = False
        count += 1
        if count % 10 == 0: print(count)

    if still_going:
        i_surrender_b.click()
        i_end_battle_b.click()
        time.sleep(0.5)
        i_surrender_b_okay.click()
    i_return_home_b.click()
    clicked, count = False, 0
    while not clicked and count < 3:
        if i_star_bonus_okay.find():
            i_star_bonus_okay.click()
            clicked = True
        time.sleep(1)
        count += 1
    current_location = loc(builder)
    if i_star_bonus_okay.find():
        i_star_bonus_okay.click()

    # goto(builder)
    return

def get_war_elixir():
    goto(builder)
    zoom_out()
    found, count = False, 0
    while not found and count < 4:
        hold_key("s", 0.05)
        for cart in carts:
            found = cart.find()
            print("Cart find:", cart.find_detail())
            if found:
                cart.click()
                break
        count += 1
    if not found:
        print("Couldn't find the elixir cart anywhere.")
        return
    time.sleep(0.5)
    i_collect_elixir.click()
    time.sleep(0.5)
    pag.press("esc")
    # i_red_cross_elixir_cart.click()

def check_all_troops_used(a, b):
    print("Check all troops used")
    for x in [i_barb,i_machine]:
    # for x in [i_barb, i_bomber, i_giant, i_pekka, i_cannon, i_machine]:
        place_b(x, a, b, 5, 1)
    return

def place_b(troop, a, b, n, loops=1):
    print("Place b:", troop, troop.find_detail(show_image=False))
    if not troop.find(): return
    troop.click()
    spots = get_spots(a,b,n)
    if spots is None:
        return "No spots"
    for _ in range(loops):
        for spot in spots:
            # print("Place b:", spot)
            if LIMITS[0] < spot[0] < LIMITS[2] and LIMITS[1] < spot[1] < LIMITS[3]:
                pag.click(spot)
                time.sleep(0.4)
        time.sleep(0.5)

def get_time_attack():
    # print("Get time until attack is ready")
    goto(army_tab)
    result = time_to_army_ready()

    if result:
        result = datetime.now() + max(timedelta(minutes=result), timedelta(minutes=2))
    else:
        result = datetime.now() + timedelta(minutes=20)
    return result

def update_attack_time(account):
    goto(army_tab)
    result = army_time.read(region=ARMY_TIME, show_image=False)
    print("Update attack time:", result)
    if text_to_time_2(result) is not None:
        db_update(account, "attack", text_to_time_2(result) + timedelta(minutes=1))

def attack(account, data, siege_required=True, attack_regardless=False, print_time=False):
    db_update(account, "attack", datetime.now() + timedelta(minutes=5))
    account.set_mode(resource_update=True)
    if account.mode != "attack": return
    if not attack_regardless:
        if not account.attacking:
            # print(f"{account} not attacking")
            db_update(account, "attack", datetime.now() + timedelta(hours=2))
            return
    goto(main)

    # Attack Prep
    army_ready = attack_prep(account, siege_required=account.requires_siege)
    if not army_ready:
        print("attack: Troops not ready")
        update_attack_time(account)
        return

    # Find a match
    goto(find_a_match)
    zoom_out()
    match_found = False
    war_goals = account.war_goals()
    while not match_found:
        assessment = assess_village(account, data, war_goals, print_time=print_time)
        if assessment[0] == "Good to go":
            break
        print("Assessment:", assessment)
        if assessment == "Not on attack screen": return
        next_village()
        war_goals = [int(war_goals[0] * 0.98), int(war_goals[1] * 0.98),int(war_goals[2] * 0.98),]
        print("New gold objective:", war_goals)

    # Launch attack
    image = assessment[1]
    launch_attack_new(account, data)

    # launch_attack(account, data, image)

    # Finish attack
    finish_attack(account, data)

    # Donations
    if account.request_type is None:
        castle_troops_change(account.clan_troops_army)
        account.request_type = "Army troops"
    else:
        request(account)

    time.sleep(.2)
    return

def finish_attack(account, data):
    global current_location
    # wait_cv2("return_home", max_time=80)
    i_return_home.wait(80)
    three_stars = i_3_stars.find()
    print("Three stars:", three_stars)
    # if three_stars: share_latest_attack()
    i_return_home.click()
    goto(main)
    # print("Three stars:", three_stars)
    army_prep(account, account.troops_to_build, army_or_total="total", extra=True)
    time = text_to_time_2(army_time.read(region=ARMY_TIME, show_image=False))
    print("Finish attack (time):", time)
    db_update(account, "attack", time)
    account.update_attacking()

def convert_attack_to_troops(data):
    troops_required = data['initial_troops'] + data['final_troops']
    for x, no in data['troop_group']:
        troops_required += [x] * no * data['troop_groups']
    troops_required += [lightening] * data['lightening']

    return troops_required


def attack_prep(account, siege_required=True):
    goto(army_tab)

    account.update_troops_to_build()
    # army_prep(account, account.troops_to_build, army_or_total="total")
    sufficient_troops, actual_troops = army_prep(account, account.troops_to_build, include_castle=True, army_or_total="army")
    if not sufficient_troops: return sufficient_troops

    if siege_required and actual_troops and account.th > 8:
        if blimp in account.clan_troops_army:
            pass
            # if blimp not in actual_troops.keys() or actual_troops[blimp] == 0:
            #     print("No blimps")
            #     if blimp not in actual_troops.keys(): print("Not in key")
            #     if actual_troops[blimp] == 0: print("Count is zero")
            #     sufficient_troops = False
            #     # Donations
            #     if account.request_type is None:
            #         castle_troops_change(account.clan_troops_army)
            #         account.request_type = "Army troops"
            #     else:
            #         request(account)
        elif log_thrower not in actual_troops.keys() or actual_troops[log_thrower] == 0:
            print("No log throwers")
            sufficient_troops = False
            # Donations
            if account.request_type is None:
                castle_troops_change(account.clan_troops_army)
                account.request_type = "Army troops"
            else:
                request(account)
        # db_update(return_account(1), "donate", datetime.now())

    print("Attack prep - sufficient troops", sufficient_troops)
    return sufficient_troops

# def troop_create(troop, count):
#     print("Troop create: ", troop)
#     troop.start_train(count)

def check_towers(towers, img, return_image=False):
    found = False
    for tower in towers:
        val, loc, rect = find_cv2_image(tower, img)
        if val > 0.65:
            found = True
            cv2.rectangle(img, rect, (0,255,255), 2)
    if return_image:
        return found, img
    else:
        return found


def assess_village(account, data, war_goals, print_time=False):
    print_time = True
    start_time = datetime.now()
    global DP
    print("Assess village")
    time.sleep(0.5)
    # zoom_out()

    if print_time: print("A", datetime.now() - start_time)
    if not i_end_battle.wait(dur=3):
        print("Not on attack screen")
        return "Not on attack screen"

    # Resource Check
    if print_time: print("B", datetime.now() - start_time)
    resources = available_resources()
    required = war_goals
    print("Assess village (resources vs required):", resources, required)
    if resources[0] < required[0] or resources[1] < required[1] or resources[2] < required[2]:
        return "Insufficient resources"

    # Advanced Town Hall
    if print_time: print("C", datetime.now() - start_time)
    img = create_double_screen()
    if img is None: print("Returned None image")
    if resources[1] > 900000:
        return "Good to go", img
    # show(img, scale=0.5)

    # pag.screenshot("attacks/attack.png")
    th = get_th_level(img)
    print("Town hall:", th)
    if th == -1:
        print("TH not identified:", th)
        th = "TH:" + str(get_th_level(img, show_result=False))
        cv2.rectangle(img, (5, 5, 150, 50), (25, 25, 25), -1)
        cv2.putText(img, th, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        time_string = str(datetime.now().hour) + " " + str(datetime.now().minute) + " " + str(datetime.now().second)
        cv2.imwrite(f'images/attack_screens/attack {time_string}.png', img)

        if account == bad_daz:
            return "Town hall not identified"
    elif account.th > 5 and th > account.th and resources[0] < 900000:
        print("TH too high:", th)
        return "Town hall too high"

    # Not on attack screen
    if not i_attack_screen_resources.wait(8): return "Not on attack screen"

    # Aggressive defences
    # if check_towers(data['towers_to_avoid'], img) and resources[0] < 900000: return "Aggressive defence"

    # Barb drop spot
    DP = ram_drop_point(img)
    if DP is None:
        DP = STANDARD_DP2

    # show(img, scale=0.5)
    return "Good to go", img

def next_village():
    print()
    print("Next village")
    time.sleep(0.5)
    i_next_attack.wait(dur=5)
    i_next_attack.click()
    if not i_end_battle.wait(dur=5): return "Not on attack screen"

def drop_point(r, image):
    range_y = 70
    range_x = int(range_y * 4/3)
    x, y, w, h = r
    center_x = x + w//2
    center_y = y + w//2
    town_center_h, town_center_w = image.shape
    town_center_x = town_center_w // 2
    town_center_y = town_center_h // 2
    if center_x > town_center_x:
        dp_x = center_x + range_x
    else:
        dp_x = center_x - range_x
    if center_y > town_center_y:
        dp_y = center_y + range_y
    else:
        dp_y = center_y - range_y
    dp = (dp_x, dp_y)
    image = cv2.circle(image, dp, 3, (255,255,255), 3)
    # show(image)
    return dp

# def launch_attack(account, data, image):
#     print("Attack - initial troops:", objects_to_str(data['initial_troops']))
#     pag.scroll(300)
#     pag.scroll(300)
#
#     standard_pace = True
#
#     if data['name'] == 'barbs':
#         if DP is None: return
#         dp = DP
#         if DP[1] > 700:
#             for _ in range(3): pag.scroll(-300)
#             pag.scroll(-300)
#             pag.scroll(-300)
#             dp[1] -= 350
#     else:
#         dp = STANDARD_DP
#
#     if data['name'] == "golems":
#         dp = top
#         dp2 = left
#     else:
#         dp2 = None
#
#     print("Launch attack: bombing")
#     earth_quake()
#
#     # if data['bomb']: bomb(data['bomb_target'], image)
#     # if data['bomb_target2'] is not None: bomb(data['bomb_target2'], image)
#     troop_pause = data['troop_pause']
#
#     # if account.th < 9:
#     #     place_clan()
#     print("Launch attack: initial troops")
#     print("Attack - initial troops 6:", objects_to_str(data['initial_troops']))
#
#     for x in data['initial_troops']:
#         place(x, 1, dp)
#
#     print("Launch attack: main troops")
#     for x in range(data['troop_groups']):
#         for troop, n in data['troop_group']:
#             if not dp2:
#                 place(troop, n, dp, troop_pause=troop_pause)
#             else:
#                 place_line(troop, n, dp, dp2)
#         # try:
#         #     damage = read_text(DAMAGE, WHITE,True)
#         # except:
#         #     damage = 0
#         # try:
#         #     if int(damage) > 60:
#         #         standard_pace = False
#         # except:
#         #     pass
#         # print("launch_attack Damage:", damage)
#         if standard_pace: time.sleep(3)
#     if standard_pace: time.sleep(10)
#
#     print("Launch attack: final troops")
#     for x in data['final_troops']:
#         place(x, 1, dp)
#     i_return_home.wait(30)
#     i_return_home.click()
#     # wait_cv2("return_home")

def earth_quake():
    step_x, step_y = 80, 160
    base_x, base_y = 900, 100
    hit_codes = [(0,0), (-1, 1), (1, 1), (-2, 2), (0, 2), (2, 2), (-3, 3), (-1, 3), (1, 3), (3, 3), (-2, 4), (0, 4), (2, 4), (0, 5)]
    hits = []
    for x, y in hit_codes:
        hit_loc = (base_x + step_x * x, base_y + step_y * y)
        hits.append(hit_loc)
    quake.i_attack.click()
    for x, y in hits:
        pag.click(x, y)
        time.sleep(0.1)

def place(troop, count_total, dp=[400,400], troop_pause=0):
    out_of_bounds = True
    if LIMITS[0] < dp[0] < LIMITS[2] and LIMITS[1] < dp[1] < LIMITS[3]: out_of_bounds = False
    if out_of_bounds: return

    dp1 = dp
    val, loc, rect = find(troop.i_attack.image, get_screenshot(TROOP_ZONE))
    print("Place troops:", troop, val, loc, ". Drop point:", dp1)
    if val > 0.63:
        click(troop.i_attack.image, TROOP_ZONE)
        time.sleep(.2)
        count = 0
        pause_dur = 0.2
        while count < count_total:
            pag.click(dp1)
            time.sleep(troop_pause)
            time.sleep(pause_dur)
            count += 1
        if troop == warden:
            time.sleep(0.1)
            print("Activate warden")
            i_warden_activate.click()


def launch_attack_new(account, data):
    dp = DP
    if DP[1] > 700:
        for _ in range(3): pag.scroll(-300)
        dp[1] -= 350

    print("Attack - new")
    pag.scroll(300)
    pag.scroll(300)

    for d in data:
        print("Attack - new", d)
        if d[0] == "place":
            place(d[1], d[2], dp, troop_pause=d[3])
            time.sleep(d[3])
        if d[0] == "ability":
            d[1].activate_image.click()
        if d[0] == "earthquake":
            earth_quake()
        if d[0] == "pause":
            time.sleep(d[1])
        if d[0] == 'rage_th':
            for town_hall in town_halls:
                if town_hall.level >= 12:
                    val, loc, rect = town_hall.find_detail()
                    print("Rage TH", town_hall, val)
                    if val > town_hall.threshold:
                        click(rage.i_attack.image, TROOP_ZONE)
                        pag.click(loc)
                        click(invisibility.i_attack.image, TROOP_ZONE)
                        pag.click(loc)
                        break



def place_line(troop, count_total, dp1, dp2, troop_pause=0):
    if troop in TROOP_ATTACK_EXT: troop = troop + "_attack"
    troop = "troops/" + troop
    val, loc, rect = find_cv2(troop, TROOP_ZONE)
    print("Place troops:", troop, val, loc)
    if val > 0.63:
        click_cv2(troop, TROOP_ZONE)
        time.sleep(.1)
        print("Place line", top, left)
        for count in range(count_total):
            prop = round((count + 1) / (count_total + 1),2)
            prop2 = (1 - prop)
            x = int(dp1[0] * prop + dp2[0] * prop2)
            y = int(dp1[1] * prop + dp2[1] * prop2)
            # print(troop, dp1, dp2, count, prop, prop2, x, y)
            pag.click(x,y)
            time.sleep(troop_pause)

def has_spells():
    print("Has spells")
    return lightening.i_army.has_colour()
    #     find_many("troops/lightening", TROOP_ZONE, 0.5)
    # for x in lightening_buttons:
    #     if check_colour_rect(x):
    #         print("Has spells - True")
    #         return True, x
    # print("Has spells - False")
    # return False, None

def bomb_mult(coords, count):
    for x in range(count):
        pag.click(pag.center(coords))

def kill_tower(rect, yolo_code):
    for _ in range(3):
        time.sleep(0.3)
        pag.click(rect)

    enlarged_rect = [rect[0] - 50, rect[1] - 50, rect[0] + 50, rect[1] + 50]
    screen = get_screenshot(region=enlarged_rect, colour=1)
    show(screen, label="kill tower")

    killed, count = False, 0
    # while not killed and count < 5:
    #     screen = get_screenshot(region=enlarged_rect, colour=1)
    #     results = find_targets([yolo_code], screen, enlarged_rect[0], enlarged_rect[1])
    #     if len(results) == 0:
    #         killed = True
    #     else:
    #         pag.click(rect)
    #     if lightening.i_attack.colour() < 600:
    #         return
    #     count += 1


# def bomb(tower_to_bomb, image):
#     if tower_to_bomb not in [air_defence]:
#         print("Only bombing air defence atm")
#         return
#     if not lightening.i_attack.find(fast=False, show_image=False):
#         print("No spells at all")
#         return
#     if lightening.i_attack.colour() < 600:
#         print("No spells left")
#         return
#
#     WAR_ZONE = (600, 0, 800, 700)

    # screen = get_screenshot(region=WAR_ZONE, colour=1)
    # results = find_targets([tower_to_bomb.yolo_code], screen, WAR_ZONE[0], WAR_ZONE[1])
    # results = find_targets([tower_to_bomb.yolo_code], image, 0, 0)
    # if len(results) > 0:
    #     lightening.i_attack.click()
    #     for result in results:
    #         kill_tower(result, tower_to_bomb.yolo_code)
    #         if lightening.i_attack.colour() < 600:
    #             print("No spells left")
    #             return
    # for _ in range(3): pag.scroll(300)


def bomb_old(tower_to_bomb):
    if lightening.i_army.colour() < 600:
        print("No spells left")
        return
    if not lightening.i_army.find():
        print("No spells at all")
        return
    lightening.i_army.click()
    for tower in tower_to_bomb.images:
        count = 0
        if count < 4:
            hits = 3
            if tower_to_bomb == EAGLE:    hits = 6
            if tower_to_bomb == INFERNOS: hits = 5
            val, loc, rect = tower.find_detail()
            print("Bomb:", val, loc, rect)
            enlarged_rect = [rect[0] - 2, rect[1] - 2, rect[2] + 4, rect[3] + 4]
            if val > 0.80 and rect[0] > 390 and rect[1] > 100:
                bomb_mult(rect, hits)



def bomb_old_2(tower_to_bomb):
    targets = tower_to_bomb.images
    if lightening.i_army.colour() < 600:
        print("No spells left")
        return
    if not lightening.i_army.find():
        print("No spells at all")
        return
    lightening.i_army.click()
    print("Bomb (initial):")
    for x in targets:
        count = 0
        if count < 4:
            val, loc, rect = find_cv2(x)
            if val > 0.65 and loc[1] < 728 and 300 < loc[1] < 1500:
                print("Bomb - Found target")
                hits = 3
                if targets == EAGLE:    hits = 6
                if targets == INFERNOS: hits = 5
                enlarged_rect = [rect[0] - 2, rect[1] - 2, rect[2] + 4, rect[3] + 4]
                bomb_mult(rect, hits)
                time.sleep(1.5)
                for _ in range(2):
                    time.sleep(2)
                    val, loc, rect = find_cv2(x, enlarged_rect)
                    if val > 0.7:
                        print("Bomb - One more")
                        bomb_mult(rect, 1)
                count += 1
            else:
                print(f"Did not find {x}. Val:", val)
        if lightening.i_army.colour() < 600: return
    return



# def share_latest_attack():
#     print("Share latest attack")
#     goto(main)
#     i_mail.click()
#     time.sleep(0.5)
#     if not i_attack_log.find():
#         print(i_attack_log.find_detail())
#         print("Couldn't find attack log tab")
#         i_red_cross.click()
#         return
#     i_attack_log.click()
#     rects = i_share_replay.find_many(show_image=False)
#     rects = sorted(rects, key=lambda x: x[1])
#     if len(rects) > 0:
#         rect = rects[0]
#         time.sleep(0.25)
#         region = (rect[0] + 180, rect[1] + 20, 150, 80)
#         screen = get_screenshot(region)
#         result = i_3_stars_2.find_screen(screen)
#         print("3 Stars:", result)
#         if not result:
#             i_red_cross.click()
#             return
#
#         click_rect(rects[0])
#         time.sleep(0.3)
#         i_share_replay_message.click()
#         pag.write("Bot attack")
#
#         i_share_replay_send.click()
#     time.sleep(0.7)
#     i_red_cross.click()

# def log(var, account, no):
#     time = datetime.now().strftime('%d %b %I:%M%p')
#     no = f"{no:,}"
#     line = f"{time}: Account: {account.number}. {var.title()}: {no}"
#     with open(f"log{account.number}.txt", 'r+') as f:
#         content = f.read()
#         f.seek(0, 0)
#         f.write(line.rstrip('\r\n') + '\n' + content)
#
def max2(list):
    try:
        return max(list)
    except:
        return 0

def calc_score_sub(defences):
    wizard = [item[1] for item in defences if item[0] == "Wizard"]
    inferno = [item[1] for item in defences if item[0] == "Inferno"]
    cross = [item[1] for item in defences if item[0] == "Cross"]
    eagle = [item[1] for item in defences if item[0] == "Eagle"]
    th = [item[1] for item in defences if item[0] == "TH"]
    result = max2(wizard) + max2(inferno) + max2(cross) + max2(eagle) + max2(th)
    print("TH:", max2(th), "Result", result)
    return result

def calc_score(img):
    img_orig = img.copy()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    defences = []
    for name, templates, score, type in TOWERS:
        rects = find_many_img(templates, img, 0.63)
        for x in rects: cv2.rectangle(img_orig, x, (255,255,255), 1)
        if len(rects) > 0:
            defences.append((type, score))
    result = calc_score_sub(defences)
    print("Calc score:", result)
    return result

def available_resources():
    i_end_battle.wait()
    time.sleep(.5)

    screen = get_screenshot(AVAILABLE_GOLD)
    gold = available_resource_set.read_screen(screen, return_number=True, show_image=False)
    if gold > 2000000: gold = gold // 10
    print("Available resources (gold):", gold)

    return [gold, 0, 0]
