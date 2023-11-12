from bot import *
from games import *

# set_current_account()
def run():
    # set_current_account()
    # set_admin_mode()
    # check_status_files_exist()
    while True:
        run_job(db_next_job())
        if in_time_zone(20, 23):
        #     war_prep(cwl=True)
        #     goto(pycharm)
        #     admin.war_donations_remaining = -1
            wait(60 * 3)


def check_status_files_exist():
    for account in accounts:
        for type in ["builders", "gold", "time"]:
            file = f"temp/tracker/{type}{account.number}.png"
            if not Path(file).is_file():
                print("Creating status file:", file)
                update_images(account, create=True)
    file = "temp/tracker/status.png"
    if not Path(file).is_file():
        print("Creating main status file.")
        update_image()


def run_old():
    print_info()
    time.sleep(15)

    # print("------1")
    global current_account
    next_sweep = datetime.now() + (datetime.min - datetime.now()) % sweep_period
    db_update(admin, "sweep", next_sweep)
    db_update(account_1, "message", datetime.now() + timedelta(minutes=120))
    set_current_account()
    set_admin_mode()
    reset_times()
    for account in accounts:
        if admin.mode in ["cwl", "battle_day"]:
            account.set_mode(resource_update=False, attacks_left_update=True)
        else:
            account.set_mode(resource_update=False, attacks_left_update=False)

        print(account, account.mode)
        db_update(account, account.mode, datetime.now() + timedelta(minutes=-20))
        if account.th < 5:
            db_update(account, "coin", datetime.now() + timedelta(hours=24))
            db_update(account, "research", datetime.now() + timedelta(hours=24))
    if admin.games:
        db_update(admin, "games", datetime.now())

    while admin.auto:
        run_job(db_next_job())

def wait(minutes):
    for x in range(minutes):
        print(f"Waiting: {x} of {minutes} minutes")
        time.sleep(60)

def rapid_attack(account):
    start()
    change_accounts(1, "main")
    count = 0
    while count < 20:
        attack(account, account.army_troops)
        time.sleep(60)
        count += 1
    end()

def rapid_trophy_loss(account):
    start()
    change_accounts(1, "main")
    count = 0
    while count < 50:
        lose_trophies(1, troops=["super_barb", ])
        time.sleep(1)
        count += 1
    end()


def test2(account):
    screens = dir_to_list('attacks2')
    # print(screens)

    count = 0
    max_count = 50
    for screen in screens:
        if count < max_count:
            count += 1
            image = cv2.imread("images/" + screen + ".png", 1)
            image_bw = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            target_locs = find_many_img(MINES, image_bw, confidence=0.7)
            center = (image.shape[1] // 2, image.shape[0] // 2)
            result = get_drop_points(account, image, center, target_locs)
            # print(result)
            # show(result, 10000, screen, 0.7)

def info_grab():
    for account in accounts:
        change_accounts_fast(account)
        if account == account_1:
            war_get_status_image()
        get_resources()
        if account.th > 5:
            donate(account)
            coin()
        account.update_resources()
        account.next_update()
        clock()
        get_resources()

def go():
    account = account_1
    account.mode = "attack"
    admin.mode = ""
    attack(account, account.army_troops)

def build_focus():
    for account in [account_2, account_3]:
        change_accounts_fast(account)
        build(account, "main")

def check_resources():
    app()
    print(current_resources())
    app()

def update_build_times():
    for account in accounts:
        account.update_build_time("main")
    print_info()

# invite_many(300)
# wait(15)

# print(len(carts))

# set_current_account()
# j_attack_b.run(account_6)
# goto(main)

# get_super_troop(super_barb)

# for account in accounts:
#     remaining_time_for_th(account)
# update_image()

# initial_entries(accounts)
# db_update(jon, "attack_b", datetime.now() + timedelta(minutes=0))
# db_update(micah, "attack_b", datetime.now() + timedelta(minutes=0))
# db_update(daen, "attack_b", datetime.now() + timedelta(minutes=0))
# bob.update_resources()

def reset_job_time(job):
    for account in accounts:
        db_update(account, job, datetime.now())

def show_image_of_region(region):
    app()
    image = get_screenshot(region)
    show(image)
    app()

def highlight_next_build():
    for x in range(1,7):
        file = f"temp/tracker/time{x}.png"
        i = cv2.imread(file, 0)
        result_text = build_time.read_screen(i)
        result = text_to_time_2(result_text)
        print(x, result_text, result)
        # show(i)
        if x == 1:
            shortest_time = result
            shortest_time_account = 1
        elif result < shortest_time:
            shortest_time = result
            shortest_time_account = x
    print(shortest_time_account, shortest_time)
    return shortest_time_account


# app()
# time.sleep(0.2)
# print(i_army_tab.find_detail(show_image=True))
# app()

# goto(troops_tab)

# invite()

# goto(l_clan)
# set_current_account()
# set_admin_mode()
# daz.mode = "donate"
# j_donate.run(daz)

# war_prep()

# goto(find_a_match)

# log_thrower.start_train(1, bad_daz)

# count = troops_count_flex(army_tab, ARMY_EXISTING, just_troops, show_image=False, show_image_numbers=False)
# print_count("Troops", count)

def seconds_to_half_hour():
    now = datetime.now()
    result = (now.replace(minute=30 * (now.minute//30), second=0, microsecond=0) + timedelta(minutes=30) - now).seconds
    return result



def run_simple():
    while True:
        for account in [daen, micah, bob, daz, bad_daz]:
            j_attack.run(account)
            j_lose_trophies.run(account)
            j_donate.run(account)
        goto(pycharm)
        print_info()
        j_attack_b.run(daen)
        time.sleep(seconds_to_half_hour())

def th_checker(loops=5):
    goto(find_a_match)
    zoom_out()
    for _ in range(loops):
        img = create_double_screen()
        th = "TH:" + str(get_th_level(img, show_result=False))
        cv2.rectangle(img, (5, 5, 150, 50), (25, 25, 25), -1)
        cv2.putText(img, th, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        time_string = str(datetime.now().hour) + " " + str(datetime.now().minute) + " " + str(datetime.now().second)
        cv2.imwrite(f'images/attack_screens/attack {time_string}.png', img)
        next_village()
        time.sleep(2)
        print("Current Location:", current_location)

    goto(pycharm)

def th_checker_2():
    files = dir_to_list("attack_screens")
    print(files)
    for file in files:
        filename = "images/" + file+".png"
        print(filename)
        screen_0 = cv2.imread(filename, 0)
        screen_1 = cv2.imread(filename, 1)
        max_result = 0
        max_townhall = None
        for town_hall in town_halls:
            result = cv2.matchTemplate(screen_0, town_hall.image, method)
            min_val, val, min_loc, loc = cv2.minMaxLoc(result)
            if val > max_result:
                max_result = val
                max_townhall = town_hall
        max_result = round(max_result, 2)
        print(max_townhall, max_result)

        show(screen_1, label=max_townhall.name + ": " + str(max_result))


run()

# j_donate.run(daz)


# print("Army:\n", objects_to_str(daz.convert_attack_to_troops(daz.army_troops)))
# print("Siege:\n", objects_to_str(daz.siege_troops))

# daz.update_troops_to_build()
# print(daz.troops_to_build)


goto(pycharm)

