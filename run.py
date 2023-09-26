from bot import *
from games import *

# set_current_account()
def run():
    # set_current_account()
    check_status_files_exist()
    while True:
        run_job(db_next_job())

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

# set_current_account()
# set_admin_mode()
# j_donate.run(daz)

# war_prep()

for image in images:


# run()
goto(pycharm)

