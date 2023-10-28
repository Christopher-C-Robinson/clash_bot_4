from attacks import *
from sql import *
from sql_account import *
from utilities import *

trophy_limits = {0: 0, 1: 100, 2: 200, 3: 300, 4: 400, 5: 500, 6: 600, 7: 1300, 8: 1000, 9: 1200, 10: 1400, 11: 1600, 12: 1800, 13: 2000, 14: 2000, 15: 2500}

accounts = []

def save_tower_details(tower, region):
    get_screenshot(region, filename=tower.name)


def extend_string(string, length):
    extra_spaces = max(length - len(string), 0)
    if extra_spaces > 0:
        string = string + " " * extra_spaces
    return string

def get_donation_troops():
    # Troops
    donation_troops = []
    for troop in troops:
        if troop.donations > 0 and troop.type != "siege" and troop != super_minion:
            for x in range(troop.donation_count):
                donation_troops.append(troop)

    if admin.war_donations_remaining and admin.war_donations_remaining > 0:
        donation_troops += [lava_hound] * 6

    # Siege equipment
    # donation_siege = [x for x in troops if x.type == 'siege' and x.donations > 0]
    # if len(donation_siege) < 6:
    #     for _ in range(6 - len(donation_siege)):
    #         donation_siege.append(log_thrower)
    return donation_troops

def get_donation_troops_min():
    donation_troops = []
    for troop in troops:
        if troop.donations > 0 and troop.type != "siege":
            donation_troops.append(troop)
    donation_siege = [x for x in troops if x.type == 'siege' and x.donations > 0]
    if len(donation_siege) < 6:
        for _ in range(6 - len(donation_siege)):
            donation_siege.append(log_thrower)
    return donation_troops, donation_siege

class Account:
    def __init__(self, data):
        self.name = data['name']
        self.number = data['number']
        self.th = data['th']
        self.has_siege = data['has_siege']
        self.requires_siege = data['requires_siege']
        self.building = data['building']
        self.build_sets = data['build_sets']
        # self.build_count = min(db_account_read(self.number, "build_count"), len(self.build_sets) - 1)
        # print(self, self.build_count, self.build_sets, len(self.build_sets))
        # self.build_items = self.build_sets[self.build_count]
        # if not self.build_count: self.build_count = 0
        self.building_b = data['building_b']
        self.max_trophies = trophy_limits[self.th]
        self.current_trophies = 0
        # if self.number == 6:
        #     self.max_trophies = 2100
        self.gold = db_account_read(self.number, "gold")
        if not self.gold: self.gold = 0
        self.elixir = None
        self.dark = db_account_read(self.number, "dark")
        self.total_gold = data['total_gold']
        self.total_elixir = data['total_elixir']
        self.total_dark = data['total_dark']
        self.required_currency = data['required_currency']
        self.army_troops = data['army_troops']
        self.army_clan_troops = data['army_clan_troops']
        self.war_troops = data['war_troops']
        self.cwl_troops = data['cwl_troops']
        self.war_donations = data['war_donations']
        self.siege_troops = data['siege_troops']
        self.donations_from = data['donations_from']
        self.games_troops = data['games_troops']
        self.army_troops_b = data['army_troops_b']
        icon = data['icon']
        self.icon = Image(icon, f"images/accounts/{icon}.png", threshold=0.84)
        # self.icon_b = Image(icon, f"images/accounts/{icon}_b.png", threshold=0.84)
        # icon2 = data['icon2']
        self.icon2 = Image(icon + "_2", f"images/accounts/{icon}_2.png", threshold=0.84)
        self.troops_to_build = None
        self.attacking = data['attacking']
        self.attacking_b = data['attacking_b']
        self.researching = data['army_troops_b']
        self.next_build = db_read(self.number, "build")
        self.next_build_b = db_read(self.number, "build_b")
        self.next_research = db_read(self.number, "research")
        self.completion_date = db_account_read(self.number, "completion_date")
        self.completion_string = db_account_read(self.number, "completion_string")
        self.build_cycle = 0
        self.needs_walls = data['needs_walls']
        self.next_research_b = None
        self.available_upgrades = []
        self.use_suggestion_b = False
        self.clan_troops = None
        self.clan_troops_war = data['clan_troops_war']
        self.current_game = db_account_read(self.number, "game")
        if self.th >= 6:
            self.playing_games = True
        else:
            self.playing_games = False
        self.attacks_left = False
        self.cwl_donations_left = True
        self.mode = None
        self.request_type = None
        self.initial_mode_set = False

        if self.number in [1,2]:
            self.cwl_donations_left = True
        accounts.append(self)

    def __str__(self):
        return f"Account {self.number}:"

    def set_mode(self, resource_update=True, attacks_left_update=False):
        start_mode = self.mode
        self.update_attacking(resource_update=resource_update)
        pre = self.attacks_left
        if attacks_left_update: self.update_attacks_left()
        if self.attacks_left != pre: admin.war_donations_remaining = -1

        self.mode = "donate"
        if self.attacking:                                                         self.mode = "attack"
        elif admin.mode == "preparation" and admin.war_donations_remaining == 0:   self.mode = "war_troops"
        elif admin.mode == "battle_day" and self.attacks_left:                     self.mode = "war_troops"
        elif admin.mode == "cwl" and admin.war_donations_remaining == 0:           self.mode = "cwl_troops"
        if self not in war_participants:
            self.mode = "donate"
            if self.attacking:                                                     self.mode = "attack"
        if self == donating_account():                                             self.mode = "donate"

        if self.mode != start_mode:
            db_update(self, self.mode, datetime.now() + timedelta(minutes=2))

    def update_attacks_left(self):
        change_accounts_fast(self)
        goto(main)
        if i_attacks_available.find():
            self.attacks_left = True
        else:
            self.attacks_left = False

    def update_troops_to_build(self):
        donation_troops = get_donation_troops()
        # if self.has_siege: donation_troops += donation_siege
        # print("Update troops to build", self, self.mode, self.has_siege, donation_troops, donation_siege)
        print("Updating troops to build:", self, self.mode)

        if self.mode in ["war_troops", ]: self.troops_to_build = self.war_troops + self.siege_troops
        elif self.mode in ["cwl_troops", ]: self.troops_to_build = self.cwl_troops + self.siege_troops
        elif self.mode in ["donate", ]: self.troops_to_build = donation_troops + self.siege_troops
        else: self.troops_to_build = self.convert_attack_to_troops(self.army_troops) + self.siege_troops

        # print("Update troops to build:\n", objects_to_str(self.troops_to_build))

        for troop in self.troops_to_build:
            if type(troop) != type(super_barb): self.troops_to_build.remove(troop)

    def convert_attack_to_troops(self, data):
        troops_required = data['initial_troops'] + data['final_troops']
        for x, no in data['troop_group']:
            troops_required += [x] * no * data['troop_groups']

        troops_required += data['spells']
        if self.has_siege:
            troops_required += [siege_troops]

        return troops_required

    def print_troops(self):
        print("Print troops")

        troops_counter = Counter(self.troops_to_build)
        string = ""
        for t in troops_counter:
            string += f"{t}: {troops_counter[t]}, "
        print(self, string[:-2])

    def next_update(self):
        if spare_builders(self, "main") > 0:
            self.next_build = datetime.now()
            blank = np.zeros((BUILDER_LIST_TIMES[3], BUILDER_LIST_TIMES[2], 3), np.uint8)
            cv2.imwrite(f'temp/tracker/builder_time{self.number}main.png', blank)
        elif self.building:
            self.update_build_time()
        else:
            self.next_build = datetime.now()

        pag.click(BOTTOM_LEFT)
        self.update_lab_time()

        if spare_builders(self, "builder") > 0:
            self.next_build_b = datetime.now()
            blank = np.zeros((BUILDER_LIST_TIMES_B[3], BUILDER_LIST_TIMES_B[2], 3), np.uint8)
            cv2.imwrite(f'temp/tracker/builder_time{self.number}builder.png', blank)
        else:
            goto_list_very_top("builder")
            get_screenshot(BUILDER_LIST_TIMES_B, filename=f"tracker/builder_time{self.number}builder")
        time.sleep(0.2)
        result = build_time.read(BUILDER_LIST_TIMES_B)
        if self.building_b:
            self.next_build_b = text_to_time_2(result)
        else:
            self.next_build_b = datetime.now() + timedelta(hours=1)
        pag.click(BOTTOM_LEFT)

    def update_build_time(self, village):
        change_accounts_fast(self)
        if spare_builders(self, village) > 0:
            result = datetime.now()
        else:
            goto_list_very_top(village)
            if village == "main":
                region = BUILDER_LIST_TIMES
            else:
                region = BUILDER_LIST_TIMES_B
            builder_list_times = get_screenshot(region, filename=f"tracker/builder_time{self.number}{village}")
            # get_screenshot(RESOURCES_G, filename=f"tracker/gold{self.number}")
            time.sleep(0.2)
            result = build_time.read_screen(builder_list_times, show_image=False)
            print("Result 1:", result)
            result = text_to_time_2(result)
            print("Result 2:", result)
            if result:
                result += timedelta(minutes=1)
            else:
                result = datetime.now() + timedelta(minutes=10)
        if village == "main":
            self.next_build = result
            db_update(self, "build", result)
        else:
            self.next_build_b = result
            db_update(self, "build_b", result)

    def update_lab_time(self):
        if not self.researching:
            db_update(self, "research", datetime.now() + timedelta(days=2))
            return
        goto(l_lab)
        screen = get_screenshot(RESEARCH_TIME, filename=f"tracker/research_time{self.number}main")
        result = research_time.read_screen(screen, show_image=False)
        result = text_to_time_3(result)
        if result:
            result = result + timedelta(minutes=1)
        else:
            result = datetime.now() + timedelta(minutes=120)
        self.next_research = result
        db_update(self, "research", result)
        print("Next research:", result)

    def donating(self):
        if self.attacking: return False
        result = True
        for account in accounts:
            if account.number < self.number and not account.attacking:
                # print("Donating:", self, account)
                result = False
        return result

    def update_resources(self, show_image=False):
        change_accounts_fast(self)
        time.sleep(2)
        goto(main)
        resources = current_resources(show_image=show_image)
        # print("Account update resources:", resources)
        if resources[0] > self.total_gold * 2: resources[0] = resources[0] / 10
        self.gold = resources[0]
        # print("Gold:", self.gold)
        # self.elixir = resources[1]
        # self.dark = resources[2]
        db_account_update(self.number, "gold", self.gold)
        # db_account_update(self.number, "dark", self.dark)

    def update_attacking(self, resource_update=True):
        start_mode = True
        if self.attacking is False: start_mode = False

        self.attacking = False
        if resource_update: self.update_resources()
        if self.gold < 0.96 * self.total_gold: self.attacking = True
        if start_mode is False and self.attacking:
            db_update(self, "attack", datetime.now() + timedelta(minutes=-20))
        return

    def war_goals(self):
        base_reward = 600000
        if self.th <= 4: return [5000, 0, 0]
        if self.th == 5: return [25000, 0, 0]
        if self.th == 6: base_reward = 100000
        if self.th == 7: base_reward = 200000
        if self.th == 8: base_reward = 300000
        if self.th == 9: base_reward = 400000
        total_reward = base_reward ** 2
        return [base_reward, 0, 0]

        # if not self.gold or not self.dark: return [base_reward, 0, 0]
        # gold_gap = max(self.total_gold - self.gold, 0)
        # dark_gap = max((self.total_dark - self.dark) * 100, 0)
        # total_gap = gold_gap + dark_gap
        # if total_gap == 0: return [0,0,0]
        # # print("War goals", gold_gap, total_gap, total_reward)
        # gold_goal = int((gold_gap / total_gap * total_reward) ** 0.5)
        # dark_goal = int((dark_gap / total_gap * total_reward) ** 0.5 / 100)
        # # return gold_goal, 0, dark_goal
        # return gold_goal, 0, 0

    def print_info(self):
        text = f"Account {self.number}: "
        text += str(self.mode)
        text = extend_string(text, 30)
        if self.gold and self.total_gold > 0: text += f"Gold {int(round(self.gold / self.total_gold, 2) * 100)}% "
        text = extend_string(text, 40)
        if self.dark and self.total_dark > 0: text += f"Dark {int(round(self.dark / self.total_dark, 2) * 100)}% "
        text = extend_string(text, 52)
        text += f"War goals {self.war_goals()} "
        text = extend_string(text, 80)
        if self.building: text += f"Build {time_to_string(self.next_build)} "
        text = extend_string(text, 102)
        if self.building_b: text += f"Build_b {time_to_string(self.next_build_b)} "
        text = extend_string(text, 122)
        text += f"Research {time_to_string(self.next_research)} "
        print(text)
        return text

    def get_next_build_set(self):
        # print("Get next build set. Count:", self.build_count, "Number of build sets", len(self.build_sets))
        self.build_count += 1
        if self.build_count >= len(self.build_sets): self.build_count = 0
        # print("Get next build set. Count:", self.build_count, "Number of build sets", len(self.build_sets))
        db_account_update(self.number, "build_count", self.build_count)
        self.build_items = self.build_sets[self.build_count]
        print("Build set for", self, self.build_items)
        return self.build_items




def get_account(account_number):
    for account in accounts:
        if account_number == account.number: return account
    return admin

def donating_account():
    # Returns the most senior account that isn't attacking.
    for account in accounts:
        if not account.attacking: return account

def change_accounts(account_number, target_base="main"):
    global current_account, current_location
    if current_account:
        if account_number == current_account.number: return
        # print(f"Change accounts from {current_account} to {account_number}")

    account = get_account(account_number)
    goto(change_account)
    time.sleep(0.2)
    account.icon.click()
    loc = [(0,0), (1184, 651), (1184, 524), (1184, 792), (1184, 930),][account_number]
    pag.click(loc)
    time.sleep(0.2)
    # if i_otto.find() or i_master.find():
    #     current_location = builder
    # else:
    #     current_location = main
    if target_base == "main": goto(main)
    else: goto(builder)
    zoom_out()
    current_account = account
    try:
        if current_account.gold is None or current_account.dark is None:
            current_account.update_attacking()
    except:
        pass
    return

def click_account_icon(account):
    if account.icon.find():
        account.icon.click()
    elif account.icon_b.find():
        account.icon_b.click()
    else:
        return False
    return True

def change_accounts_fast(account):
    if account == admin: return
    global current_account
    if current_account:
        if account == current_account: return

    # Change accounts
    goto(change_account)
    time.sleep(0.2)
    # Scroll down for crush and daen
    if account.number >= 5:
        for x in range(8):
            hold_key("up", 0.1)

    found, count = False, 0
    while not found and count < 10:
        if account.icon.click(): found = True
        if account.icon2.click(): found = True
        count += 1

    found, count = False, 0

    # Check you arrived
    while not found:
        time.sleep(0.1)
        for image in [i_builder, i_master_builder]:
            if image.find():
                if image == i_builder:
                    new_location = main
                else:
                    new_location = builder
                    # goto(main)
                change_current_location(new_location)
                found = True
            if i_okay.find():
                i_okay.click()
        count += 1
        if count > 30:
            goto(main)
            found = True
    zoom_out()
    # print("New account:", account)
    set_current_account()
    current_account = account

def set_current_account():
    global current_account
    goto(main)
    max_result = 0
    for account in accounts:
        result = account.icon2.find_detail()[0]
        if result > max_result:
            current_account = account
            max_result = result
    print("Current account:", current_account.name)
    return current_account.number

def update_images(account, create=False):
    if not create and not is_old(account, 10): return
    change_accounts_fast(account)
    goto(main)
    pag.click(BOTTOM_LEFT)
    i_builder.click()
    data = [(BUILDER_ZERO_REGION, "builders"), (BUILDER_LIST_TIMES, "time"), (RESOURCES_G, "gold")]
    for region, name in data:
        image = get_screenshot(region, colour=1)
        cv2.imwrite(f'temp/tracker/{name}{account.number}.png', image)
    # update_image()

def update_image():
    account_images = []
    max_width = 0
    account_to_highlight, next_build = get_account_to_highlight()
    for account in accounts:
        if is_old(account, 60):
            update_images(account)
        no = account.number
        i_mode = np.zeros((50, 50, 3), np.uint8)
        colour = (0,0,0)
        if account.mode == "attack": colour = (0, 0, 255)
        if account.mode == "donate": colour = (255, 0, 0)
        if account.mode == "war_troops": colour = (21,101,249)
        if account.mode == "cwl_troops": colour = (21,101,249)
        cv2.circle(i_mode, center=(25, 25), radius=10, color=colour, thickness=-1)
        i_name = np.zeros((50, 200, 3), np.uint8)
        colour = (0, 255, 0)
        if account.number == account_to_highlight: colour = (255, 255, 0)

        cv2.putText(i_name, account.name, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, colour, 2, cv2.LINE_AA)
        i_builders = cv2.imread(f'temp/tracker/builders{no}.png', 1)
        i_time = cv2.imread(f'temp/tracker/time{no}.png', 1)
        if account.number == account_to_highlight:
            i_time = add_green_border(i_time)
        i_gold = cv2.imread(f'temp/tracker/gold{no}.png', 1)
        i_completion_date = np.zeros((50, 250, 3), np.uint8)

        if account.completion_date:
            completion_date = f"{account.completion_date.day}/{account.completion_date.month}/{account.completion_date.year}"
            cv2.putText(i_completion_date, completion_date, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        i_completion_text = np.zeros((50, 650, 3), np.uint8)
        if account.completion_string:
            cv2.putText(i_completion_text, account.completion_string, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        combined = combine_image_horizontal([i_mode, i_name, i_builders, i_time, i_gold, i_completion_date, i_completion_text])
        account_images.append(combined)
        max_width = max(max_width, combined.shape[1])

    # Header
    header = np.zeros((50, 400, 3), np.uint8)
    time_string_now = datetime.now().strftime("%I:%M") + datetime.now().strftime("%p").lower()
    time_string_build = next_build.strftime("%I:%M") + next_build.strftime("%p").lower()
    time_string = time_string_now + " => " + time_string_build
    cv2.putText(header, time_string, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # Header
    footer = np.zeros((50, 400, 3), np.uint8)
    text = admin.mode.title()
    if admin.war_donations_remaining and admin.war_donations_remaining > 0:
        text += f": {admin.war_donations_remaining}"
    cv2.putText(footer, text, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # War Banner
    i_war_banner = cv2.imread(f'temp/tracker/war_banner.png', 1)[0:80]

    images = [header] + account_images + [footer] + [i_war_banner]
    result = combine_image_vertical(images)
    # show(result)
    cv2.imwrite("C:/Users/darre/OneDrive/Darren/clash_bot/tracker/status.png", result)
    cv2.imwrite("temp/tracker/status.png", result)

def get_account_to_highlight():
    for x in [1, 2, 3, 5]:
        file = f"temp/tracker/time{x}.png"
        i = cv2.imread(file, 0)
        result_text = build_time.read_screen(i)
        result = text_to_time_2(result_text)
        # print(x, result_text, result)
        # show(i)
        if x == 1:
            shortest_time = result
            shortest_time_account = 1
        elif result and result < shortest_time:
            shortest_time = result
            shortest_time_account = x
    # print(shortest_time_account, shortest_time)
    return shortest_time_account, shortest_time

def add_green_border(image):
    h, w, c = image.shape
    image = cv2.rectangle(image, (3, 3), (w-3, h-3), (255, 255, 0), 3)
    return image

def is_old(account, limit_minutes):
    name = "time"
    path = f'temp/tracker/{name}{account.number}.png'
    mtime = os.path.getmtime(path)  # get last modification time
    mtime_dt = datetime.fromtimestamp(mtime)
    time_since_modification = datetime.now() - mtime_dt
    mtime_str = mtime_dt.isoformat()
    result = time_since_modification > timedelta(minutes=limit_minutes)
    # if result: print(f"The {path} is old. {time_since_modification}")
    # else: print(f"The {path} is new. {time_since_modification}")
    # print(f"The file '{path}' was modified at: {mtime_str}. That was {time_since_modification} ago")
    return result

def is_image_old(file, limit_minutes):
    path = f'temp/tracker/{file}.png'
    mtime = os.path.getmtime(path)  # get last modification time
    mtime_dt = datetime.fromtimestamp(mtime)
    time_since_modification = datetime.now() - mtime_dt
    print("is_image_old:", path, time_since_modification)
    result = time_since_modification > timedelta(minutes=limit_minutes)
    return result

def get_coin():
    for image in resource_images_main:
        if image.find(): image.click()
    if i_coin_on_main_screen.find():
        for x in [i_coin_on_main_screen, i_coin_collect, i_red_cross_coin]:
            x.click()
            time.sleep(0.1)

a = ["barracks", "camp", "clan_castle", "spell", "lab", "pet_house"]
h = ["champ", "king", "queen", "warden", ]
s = ["elixir_storage", "gold_storage", "dark_elixir_storage"]

d = ["air_defence", "air_sweeper", "archer_tower", "bomb_tower", "cannon", "eagle", "inferno", "mortar", "tesla", "wizard_tower", "x-bow", "elixir_storage", "gold_storage", "dark_elixir_storage", "workshop", "dark_barracks", "dark_spell", "pet_house"]
t = ["air_bomb", "air_mine", "bomb", "giant_bomb", "skeleton", "spring_trap", "tornado", ]
r = ["dark_drill", "elixir_pump", "gold_mine",]
w = ["wall", ]

new_th = [a, h, s]
old_th_h = [d, w, t, w, r, w, h, w, s]
old_th = [d, w, t, w, r, w]
walls_done = [d, t, r,]

account_data_1 = {
    'name': "Bad Daz",
    'number': 1,
    'th': 15,
    'has_siege': True,
    'requires_siege': True,
    'building': True,
    'building_b': False,
    'total_gold': 20000000,
    'total_elixir': 20000000,
    'total_dark': 350000,
    'army_troops': BARBS_60,
    'army_clan_troops': [quake] * 3 + [log_thrower] + [super_barb] * 9,
    # 'army_clan_troops': [lightening] * 1 + [log_thrower] + [super_barb] * 3 + [super_minion],
    'war_troops': [edrag] * 2 + [dragon] * 12 + [lightening] * 3 + [freeze] * 8,
    'cwl_troops': [edrag] * 2 + [dragon] * 12 + [lightening] * 3 + [freeze] * 8 + [edrag] * 2 + [bloon] * 4,
    'war_donations': [archer] * 3 + [super_barb] * 14 + [bloon] * 6 + [dragon] * 3 + [edrag] + [lava_hound] * 5 + [ice_golem] + [log_thrower] * 6,
    'clan_troops_war': [dragon] * 2 + [bloon] + [lightening] * 3 + [log_thrower],
    'siege_troops': [log_thrower] * 5 + [flinger],
    'donations_from': 2,
    'games_troops': BARBS_60_GAMES,
    'army_troops_b': troops4,
    'required_currency': "gold",
    'icon': "bad_daz",
    'needs_walls': False,
    'attacking': True,
    'build_sets': old_th_h,
    'researching': True,
    'attacking_b': False,
}

account_data_2 = {
    'name': "Daz",
    'number': 2,
    'th': 13,
    'has_siege': True,
    'requires_siege': True,
    'building': True,
    'building_b': False,
    'total_gold': 14000000,
    'total_elixir': 10000000,
    'total_dark': 200000,
    'army_troops': BARBS_56,
    'army_clan_troops': [quake] * 2 + [log_thrower] + [super_barb] * 8,
    # 'army_clan_troops': [lightening] * 1 + [log_thrower] + [super_barb] * 3 + [super_minion],
    'war_troops': [edrag] * 2 + [dragon] * 12 + [lightening] * 3 + [freeze] * 8,
    'cwl_troops': [edrag] * 2 + [dragon] * 12 + [lightening] * 3 + [freeze] * 8 + [edrag] * 2 + [bloon] * 4,
    'war_donations': [archer] * 3 + [super_barb] * 7 + [bloon] * 3 + [dragon] * 1 + [edrag] + [lava_hound] * 3 + [ice_golem],
    'clan_troops_war': [dragon] * 2 + [lightening] * 2 + [log_thrower],
    'siege_troops': [log_thrower] * 6,
    'donations_from': 1,
    'games_troops': GIANT240_GAMES,
    'army_troops_b': troops4,
    'required_currency': "gold",
    'icon': "daz",
    'needs_walls': False,
    'attacking': True,
    'build_sets': old_th_h,
    'researching': True,
    'attacking_b': False,
}

account_data_3 = {
    'name': "Bob",
    'number': 3,
    'th': 12,
    'has_siege': False,
    'requires_siege': True,
    'building': True,
    'needs_walls': False,
    'attacking': True,
    'building_b': False,
    'total_gold': 14000000,
    'total_elixir': 6000000,
    'total_dark': 200000,
    'army_troops': BARBS_56,
    'army_clan_troops': [quake] * 2 + [log_thrower] + [super_barb] * 8,
    # 'army_clan_troops': [lightening] * 1 + [log_thrower] + [super_barb] * 3 + [super_minion],
    'war_troops': [edrag] * 2 + [dragon] * 11 + [lightening] * 4 + [freeze] * 7,
    'cwl_troops': [edrag] * 2 + [dragon] * 12 + [lightening] * 3 + [freeze] * 8 + [edrag] * 2 + [bloon] * 4,
    'clan_troops_war': [dragon] * 2 + [lightening] * 2 + [log_thrower],
    'war_donations': [archer] * 3 + [super_barb] * 7 + [bloon] * 3 + [dragon] * 1 + [lava_hound] * 3,
    'siege_troops': [ram, blimp, slammer] * 2,
    'donations_from': 1,
    'games_troops': GIANT200_GAMES,
    'army_troops_b': troops4,
    'required_currency': "gold",
    'icon': "bob",
    'build_sets': old_th_h,
    'researching': True,
    'attacking_b': False,
}

account_data_4 = {
    'name': "Crusher",
    'number': 4,
    'th': 11,
    'has_siege': False,
    'requires_siege': True,
    'building': True,
    'needs_walls': True,
    'attacking': True,
    'building_b': False,
    'total_gold': 10000000,
    'total_elixir': 22000,
    'total_dark': 160000,
    'army_troops': BARBS_52,
    'army_clan_troops': [quake] * 2 + [log_thrower] + [super_barb] * 7,
    'war_troops': [dragon] * 13 + [lightening] * 11,
    'cwl_troops': [dragon] * 13 + [lightening] * 14,
    'clan_troops_war': [bloon] + [edrag] + [lightening],
    'war_donations': [dragon] * 20 + [lightening] * 14,
    'siege_troops': [],
    'donations_from': 1,
    'games_troops': GIANT200_GAMES,
    'army_troops_b': troops4,
    'required_currency': "gold",
    'icon': "crusher",
    'build_sets': old_th_h,
    'researching': False,
    'attacking_b': False,
}

account_data_5 = {
    'name': "Daenerys",
    'number': 5,
    'th': 11,
    'has_siege': False,
    'requires_siege': True,
    'building': True,
    'needs_walls': True,
    'attacking': True,
    'building_b': False,
    'total_gold': 9500000,
    'total_elixir': 22000,
    'total_dark': 160000,
    'army_troops': BARBS_52,
    'army_clan_troops': [quake] * 2 + [log_thrower] + [super_barb] * 7,
    'war_troops': [dragon] * 13 + [lightening] * 11,
    'cwl_troops': [dragon] * 13 + [lightening] * 11,
    'clan_troops_war': [edrag] + [bloon] + [lightening] + [log_thrower],
    'war_donations': [dragon] * 20 + [lightening] * 14,
    'siege_troops': [],
    'donations_from': 1,
    'games_troops': GIANT200_GAMES,
    'army_troops_b': troops4,
    'required_currency': "gold",
    'icon': "daenerys",
    'build_sets': old_th_h,
    'researching': False,
    'attacking_b': True,
}



for data in [account_data_1, account_data_2, account_data_3, account_data_4, account_data_5]:
    Account(data)

def return_account(number):
    return next((x for x in accounts if x.number == number), None)

account_1 = next((x for x in accounts if x.number == 1), None)
account_2 = next((x for x in accounts if x.number == 2), None)
account_3 = next((x for x in accounts if x.number == 3), None)
account_4 = next((x for x in accounts if x.number == 4), None)
account_5 = next((x for x in accounts if x.number == 5), None)
# account_6 = next((x for x in accounts if x.number == 6), None)

bad_daz = account_1
daz = account_2
bob = account_3
jon = account_4
micah = account_4
daen = account_5

war_participants = [bad_daz, daz, bob, jon, daen]

# war_participants = []

# account_1.use_suggestion_b = True
# account_1.clan_troops = [super_barb] * 9
# account_1.clan_troops_war = [dragon, dragon, bloon]
# account_2.clan_troops = [super_barb] * 7
# account_2.clan_troops_war = [dragon, bloon, bloon, bloon]

current_account = None

# update_image()
# for account in accounts: print(account)

# change_accounts_fast(account_5)

