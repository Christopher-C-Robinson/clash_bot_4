import datetime

from build import *
from war import *
from research import *
from games import *
from jobs import *

method = cv2.TM_CCOEFF_NORMED



# =============
# === CLOCK ===
# =============

def clock():
    goto(builder)
    val, loc, rect = find_cv2('clock')
    # print(val)
    if val > 0.65:
        print("Clock found")
        click_cv2('clock')
        click_cv2('free_boost')
        click_cv2('boost')
        return True
    return False

# ====================
# === 6. RESOURCES ===
# ====================

def get_resources(village):
    if village == "main": images = resource_images_main
    else: images = resource_images_builder
    zoom_out()
    for x in images:
        x.click()

def get_trader_info(account):
    goto(main)
    time.sleep(0.1)
    hold_key("a", 0.5)
    hold_key("w", 0.5)
    if i_trader.click():
        i_raid_medals.click()
        pag.moveTo(1000,900)
        pag.dragTo(1000,280, .2)
        time.sleep(0.3)
        get_screenshot(CLOCK_POTION, filename=f"tracker/trader_clock_potion{account.number}")
        get_screenshot(RESEARCH_POTION, filename=f"tracker/trader_research_potion{account.number}")
        pag.press("space")

def sweep_old():
    return
    for account in [account_4]:
        change_accounts_fast(account)
        goto(main)
        get_resources("main")
        goto(builder)
        get_resources("builder")
        goto(main)



def sweep_full(fast=False):
    start_time = datetime.now()
    for account in accounts:
        if fast:
            change_accounts_fast(account)
        else:
            change_accounts(account.number)
        if account.number == 1:
            set_admin_mode()
            i_return_home_3.click()
            goto(main)
        get_resources()
        # get_trader_info(account)
        if account.th > 5:
            if not fast: donate(account)
        if not fast:
            account.update_resources()
            # check_completion(account)
        if account.building and not fast:
            build(account, "main")
        else:
            account.update_build_time("main")
        # check_trophies(account)
        account.update_lab_time()
        if account.building_b:
            account.update_build_time("builder")
            pag.click(BOTTOM_LEFT)
        clock()
        get_resources()
        # if account.th > 6 and not fast and account.attacking_b:
        #     attack_b(account)
        #     goto(builder)
        #     time.sleep(0.1)
        get_screenshot(REMAINING_ATTACKS, filename=f"tracker/remaining_attacks{account.number}")
        goto(main)
        if account.th > 5:
            coin()
        print("Timer:", account, datetime.now() - start_time)
    create_combined_builders_image(accounts)
    # war_status()

# === DATABASE ===
def db(db_str):
    con = sqlite3.connect('data.db')
    c = con.cursor()
    # print(db_str)
    c.execute(db_str)
    output = c.fetchall()
    con.commit()
    con.close()
    return output

def db_next_job():
    db_str = "SELECT * FROM jobs ORDER BY time"
    result = db(db_str)
    current_jobs = []
    for job_info in result:
        account, job, job_time = job_info
        job_time = string_to_time(job_time)
        if job_time <= datetime.now():
            current_jobs.append(job_info)
    current_jobs.sort(key=lambda tup: tup[0])
    if len(current_jobs) > 0:
        return current_jobs[0]
    else:
        return result[0]

def db_next_job_old():
    db_str = "SELECT * FROM jobs ORDER BY time"
    return db(db_str)[0]

# ============
# === JOBS ===
# ============

def run_job(job):
    sweep_period = timedelta(minutes=120)
    print()
    print("Job:", job)
    account_number, job, job_time = job
    if job in ["build_b", ]:
        db_update(account_number, job, datetime.now() + timedelta(hours=2), use_account_number=True)
        return

    account = get_account(account_number)
    if account is None:
        db_update(account_number, job, datetime.now() + timedelta(days=2), use_account_number=True)
        return
    # account = accounts[account - 1]
    job_time = string_to_time(job_time)
    job_object = get_job(job)
    if time_to_string(job_time) == "Now":
        if job_object: job_object.run(account)

        elif job == "games":
            if not admin.games:
                db_update(admin, "games", datetime.now() + timedelta(days=27))
                return
            next_games = datetime.now() + timedelta(minutes=10)
            db_update(admin, "games", next_games)
            run_games()
        else:
            job_time = datetime.now() + timedelta(hours=24)
            db_update(account, job, job_time)
            print(f"Job type '{job}' not coded yet.")
        try:
            if account != admin:
                account.set_mode()
        except:
            print("Run job - couldn't set mode. Account:", account)
    else:
        if admin.inviting and account.number <= 3:
            change_accounts_fast(account)

            print("Inviting", account, account.number)
            try:    no_of_loops = min(49 - admin.no_of_members, 5)
            except: no_of_loops = 1
            if no_of_loops >= 1:
                for x in range(no_of_loops):
                    invite()
        update_image()
        rest_time = job_time - datetime.now()
        if admin.watch:
            watch(rest_time.seconds)
        else:
            print("Rest time:", rest_time)
            goto(pycharm)
            print_info()
            if rest_time > timedelta(): # Check that the rest_time calc is positive
                time.sleep(rest_time.seconds)

def watch(dur=5):
    account = donating_account()
    if not account: account = bad_daz
    start = datetime.now()
    change_accounts_fast(account)
    goto(main)
    val, loc, rect = i_open_chat.find_detail(fast=False)
    x_adj, y_adj = 20, 10
    offsets = [(-x_adj, -y_adj), (0,-y_adj), (x_adj,-y_adj), (x_adj,0), (x_adj,y_adj), (0,y_adj), (-x_adj,y_adj), (-x_adj,0) ]
    x, y = loc
    x_pos, y_pos = x, y

    while datetime.now() < start + timedelta(seconds=dur):
        for x_offset, y_offset in offsets:
            delay = abs((x_pos - x - x_offset + y_pos - y - y_offset) / 100)
            x_pos, y_pos = x + x_offset, y + y_offset
            pag.moveTo(x_pos, y_pos, delay)
        request_made = i_chat_flag.find()
        if request_made:
            j_donate.run(account)
            goto(main)
        if i_reload_game.find():
            i_reload_game.click()

def db_view_next():
    db_str = "SELECT * FROM next ORDER BY account"
    output = db(db_str)
    for account in [1,2,3]:
        for village in ["main", "builder"]:
            building = ["none", "none", "none", "none"]
            time = ""
            for account_r, village_r, currency_r, building_r, cost, comment in output:
                if account == account_r and village == village_r:
                    if currency_r == "elixir1":
                        building[0] = building_r
                        time = string_to_time(comment)
                        time = time_to_string(time)
                    if currency_r == "dark": building[1] = building_r
                    if currency_r == "gold": building[2] = building_r
                    if currency_r == "elixir": building[3] = building_r
            spacer = ""
            if village == "main": spacer = "   "
            print(f"Account {account} ({village}) {spacer} {building} {time}")

# def print_info_old():
#     db_view()
#     update_info()
#     for key in info:
#         if key == "gold":
#             text = ""
#             resources_all = info[key]
#             text += '['
#             for resources in resources_all:
#                 if resources:
#                     text += "["
#                     text += str(round(resources[0] / 1000000, 1)) + "m, "
#                     text += str(round(resources[1] / 1000000, 1)) + "m, "
#                     text += str(round(resources[2] / 1000, 0)) + "k, "
#                     text += "], "
#                 else:
#                     text += "Unknown, "
#             text += '], '
#             print("resources:", text)
#     db_view_next()

def update_info():
    for var in ["build", "build_b", "clock", "coin", "lose_trophies"]:
        results = db_get(var, 5)
        for result in results:
            if result:
                account, job, time = result
                info[var][account-1] = time_to_string(string_to_time(time))

def get_times(accounts):
    print("Get times")
    for account in accounts:
        change_accounts(account.number)
        db_update(account, "build", get_time_build(account, "main"))
        db_update(account, "attack", get_time_attack())
        db_update(account, "build_b", get_time_build(account, "village"))
        # db_update(account, "attack_b", get_time_attack_b())
        db_update(account, "coin", get_time_coin())

# def get_time_attack_b():
#     print("Get time attack - builder")
#     goto(builder)
#     click_cv2("attack_b")
#     if find_cv2("builder_attack_wins")[0] > 0.7:
#         print("Ready for attack")
#         result = datetime.now()
#         pag.click(BOTTOM_LEFT)
#         return result
#     result = read_text(ARMY_TIME_B, WHITE)
#     result = alpha_to_numbers(result)
#     result = text_to_time(result)
#     pag.click(BOTTOM_LEFT)
#     return result

def update_time_build(account, village):
    db_str = f"SELECT * FROM next WHERE account = '{account.number}' and village = '{village}' and currency = 'elixir1'"
    account_r, village_r, currency_r, building_r, cost, comment = db(db_str)[0]
    print("Get time build: ", account_r, village_r, currency_r, building_r, cost, comment)
    time_temp = string_to_time(comment)
    if time_temp > datetime.now(): return time_temp
    result = get_time_build(village)
    # db_update_comment(account, village, 'elixir1', result)

def get_time_build(village):
    if village == "main": goto(main)
    else: goto(builder)
    goto_list_very_top(village)
    time.sleep(0.2)
    if village == "main": region = BUILDER_LIST_TIMES
    else: region = BUILDER_LIST_TIMES_B
    # pag.screenshot('temp/build_time.png', region=region)
    # i = cv2.imread(f"temp/build_time.png", 0)
    result = build_time.read(region)
    # result = read_build_time(i)
    result = text_to_time_2(result)
    # print(result)
    return result

    # result = read_text(BUILDER_LIST_TIMES, WHITE)
    # try:
    #     result = alpha_to_numbers(result)
    #     result = text_to_time(result)
    # except:
    #     print("Failed to read screenshot")
    #     print(result)
    #     result = datetime.now() + timedelta(minutes=5)
    # db_update(current_account, "build", result)
    # time.sleep(0.2)
    #
    # click_cv2("builder", BUILDER_REGION, 0.5)
    # print("Final:", result)
    # return result

def get_time_build_b():
    print("Get build time - Builder Base")
    goto(builder)
    click_builder()
    time.sleep(0.2)
    result = read_text(BUILDER_LIST_TIMES_B, WHITE)
    print("Raw:", result)
    try:
        result = alpha_to_numbers(result)
        result = text_to_time(result)
        print("after text_to_time:", result)
    except:
        print("Failed to read screenshot")
        print(result)
        time.sleep(0.2)
    click_builder()
    print("Builder build time:", result)
    return result

