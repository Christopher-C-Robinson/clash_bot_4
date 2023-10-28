from operator import attrgetter

from nav import *
from towers_load import *
from tracker import *
from utilities import *
from account import *

# buildings_to_upgrade = [
#     "air_bomb", "air_defence", "air_mine", "air_sweeper", "archer_tower", "barracks", "bomb", "bomb_tower", "camp",
#     "cannon", "champ", "clan_castle", "dark_barracks", "dark_drill", "dark_spell", "spell", "eagle", "elixir_storage",
#     "giant_bomb", "giga_tesla", "gold_storage", "inferno", "king", "lab", "mortar", "queen","skeleton",
#     "spell", "spring_trap", "sweeper", "tesla", "tornado", "warden", "war_machine", "wizard_tower", "x-bow",
#     "elixir_pump", "gold_mine",
#                         ]

buildings_to_upgrade_b = [
    "air_bombs", "air_defence", "archer_tower", "barracks",
    "cannon", "clock", "crusher", "double_cannon", "elixir_pump", "elixir_storage", "gem"
                                                                                    "giant_cannon", "gold_mine",
    "gold_storage", "guard_post", "lab", "lava", "mega_mine", "mega_tesla", "mine",
    "mortar", "roaster", "tesla", "war_machine",
]


def build():
    builders = spare_builders()
    # print("Build - spare builders", builders)
    if builders == 0: return
    goto_list_top("main")
    i_suggested_upgrades.click(y_offset=40)
    time.sleep(0.3)
    if has_cash():
        multi_click([i_upgrade_button, i_build_confirm])
    else:
        print("Build - insufficient cash")

def has_cash():
    result, loc, rect = i_upgrade_button.find_detail()
    cash_rect = [rect[0], rect[1] - 105, rect[2], rect[3]]
    image = get_screenshot(cash_rect, colour=1)
    # print(cv2.mean(image))
    return cv2.mean(image)[0] > 170



def build_x(account, village):
    start_build_items = account.build_items
    builders = spare_builders(account, village)
    print("Build - spare builders", builders)
    if builders == 0:
        account.update_build_time(village)
        return
    remove_trees(village)

    if village == "builder":
        region = [BUILDER_FIRST_ROW_B[0], BUILDER_FIRST_ROW_B[1], BUILDER_FIRST_ROW_B[2], BUILDER_FIRST_ROW_B[3], ]
        list_of_towers = build_towers_b
    else:
        region = [BUILDER_FIRST_ROW[0], BUILDER_FIRST_ROW[1], BUILDER_FIRST_ROW[2], BUILDER_FIRST_ROW[3], ]
        list_of_towers = build_towers

    print("Build items:", account.build_items)

    goto_list_top(village)
    count, found = 0, False
    time.sleep(0.5)
    while count < 30:
        next_row = get_screenshot(region)
        result = list_of_towers.read_screen(next_row, return_y=True)
        print(result)

        if result[0] in account.build_items:
            print("Found in desirable:", result[0])
            pag.click(region[0] + region[2] / 2, region[1] + region[3] / 2)
            upgrade1(account, village, result[0])
            account.get_next_build_set()
            builders = spare_builders_read(account, village)
            if builders == 0:
                account.update_build_time(village)
                return
        if result[1]:
            # print(result[0], region[1], count)
            region[1] = result[1] + region[1]
            count += 1
            region[1] = region[1] + 35
        else:
            # Couldn't read text - incremental shift in viewing space
            region[1] += 5
        if region[1] > 660:
            # Moving list
            gap, dur = 250, 1
            pag.moveTo(855, 240 + gap)
            pag.dragTo(855, 240, dur)
            region[1] -= gap
            time.sleep(0.5)
            count += 5
    if start_build_items == account.build_items:
        account.get_next_build_set()


def upgrade1(account, village, building):
    print("Upgrade1", building)
    time.sleep(0.3)
    if building == "wall":
        upgrade_wall("elixir", select_tower_bool=False)
    else:
        upgrade(village)
        account.update_build_time(village)

    builders = spare_builders(account, village)
    if village == "main":
        if builders > 0:
            db_update(account, "build", datetime.now())
        account.attacking = True
        db_update(account, "attack", datetime.now() + timedelta(minutes=2))
    else:
        if builders > 0:
            db_update(account, "build_b", datetime.now())

    # get_castle_resources()
    return


def build_old(account, village="main"):
    return
    builders = spare_builders(account, village)
    print("Build - spare builders", builders)
    if builders == 0: return
    remove_trees(village)
    if account.use_suggestion_b and village == "builder":
        # print("Using suggestion")
        goto_list_top(village)
        val, loc, rect = i_suggested_upgrades.find_detail()
        pag.click(loc[0], loc[1] + 50)
        gold, elixir, dark = current_resources()
        # print("Build", gold, elixir)
        upgrade_currency = "gold"
        if elixir > gold: upgrade_currency = "elixir"
        print(upgrade_currency)
        upgrade_wall(upgrade_currency, select_tower_bool=False)

        return

    available_options, all_options = get_available_upgrades(village)
    if wall in available_options:
        need_walls = True
    else:
        need_walls = False
    preferences = get_preferences(available_options)

    print("Needs walls", need_walls)
    if need_walls:
        print("Build", account, "Building walls")
        count = 1
        if account.th <= 12: count = 2
        if account.th <= 11: count = 5
        if account.th <= 8: count = 5
        upgrade_currency = "gold"
        if preferences[0].resource == "gold": upgrade_currency = "elixir"
        print(upgrade_currency)
        for x in range(count):
            upgrade_wall(upgrade_currency)

    for preference in preferences:
        select_tower(village, preference)
        time.sleep(0.2)
        upgrade(village)
        if spare_builders(account, village) == 0:
            account.attacking = True
            db_update(account, "attack", datetime.now() + timedelta(minutes=2))
            get_castle_resources()
            return


def get_available_upgrades(village):
    print("Get available upgrades")
    goto_list_top(village)
    bottom_image_previous = None
    available_upgrades, all_upgrades = [], []

    at_bottom, count = False, 0
    while not at_bottom and count < 5:
        all_upgrades, available_upgrades = identify_towers(village, all_upgrades, available_upgrades)
        bottom_image_current = get_screenshot(BUILDER_BOTTOM)
        at_bottom = image_similar(bottom_image_previous, bottom_image_current)
        bottom_image_previous = bottom_image_current
        move_list("up", dur=1)
        time.sleep(.2)
        count += 1
    all_upgrades, available_upgrades = identify_towers(village, all_upgrades, available_upgrades)
    move_list("down", dur=1)
    all_upgrades, available_upgrades = identify_towers(village, all_upgrades, available_upgrades)

    available_upgrades.sort(key=lambda x: x.priority, reverse=False)
    all_upgrades.sort(key=lambda x: x.priority, reverse=False)
    print("Available upgrades:", objects_to_str(available_upgrades))

    return all_upgrades, available_upgrades


def image_similar(bottom_image_previous, bottom_image_current, confidence=0.8):
    if bottom_image_current is None or bottom_image_previous is None: return False
    result = cv2.matchTemplate(bottom_image_previous, bottom_image_current, method)
    min_val, val, min_loc, loc = cv2.minMaxLoc(result)
    print("Image similar:", val)
    return val > confidence


def identify_towers(village, all_upgrades, available_upgrades):
    if village == "main":
        region = BUILDER_LIST_REGION
    else:
        region = BUILDER_B_LIST_REGION
    screen = get_screenshot(region)
    for tower in towers:
        if tower.village == village:
            if tower not in all_upgrades:
                show_image = False
                if tower.name == "lab": show_image = False
                val, loc, rect = find(tower.i_text, screen, text=tower.name, show_image=show_image)
                print("Get available upgrades:", tower, val)
                if val > 0.75:
                    val2, loc2, rect2 = i_suggested_upgrades.find_detail()
                    if val2 > i_suggested_upgrades.threshold:
                        # print(loc[1] + region[1], loc2[1])
                        if loc[1] + region[1] < loc2[1]: val = 0

                if val > 0.80:
                    # print("Val > 0.8")
                    tower_region = [region[0] + rect[0], region[1] + rect[1], 480, 30]
                    get_screenshot(tower_region, filename="temp_tower")
                    i = cv2.imread("temp/temp_tower.png", 1)
                    all_upgrades.append(tower)
                    if tower == wall: show(i)
                    cash = has_cash_2(i)
                    print("Cash:", cash)
                    if cash:
                        available_upgrades.append(tower)
    return all_upgrades, available_upgrades


def get_all_upgrades(account, village):
    print("Get available upgrades")
    goto_list_very_top(village)
    bottom_image_previous = None
    upgrades = []

    at_bottom, count = False, 0
    while not at_bottom and count < 5:
        upgrades = identify_towers_with_levels(upgrades)
        bottom_image_current = get_screenshot(BUILDER_BOTTOM)
        at_bottom = image_similar(bottom_image_previous, bottom_image_current)
        bottom_image_previous = bottom_image_current
        move_list("up", dur=1)
        time.sleep(.2)
        count += 1
    upgrades = identify_towers_with_levels(upgrades)
    move_list("down", dur=1)
    upgrades = identify_towers_with_levels(upgrades)

    upgrades.sort(key=lambda x: x[0].priority, reverse=False)
    print("Available upgrades:")
    total_time = timedelta(days=0)
    for tower, level, count in upgrades:
        if level is None:
            print(" -", tower, count, "No level")
        else:
            remaining_time = tower.remaining_time(level.number, account.th) * count
            total_time += remaining_time
            print(" -", tower, level.number, count, "Remaining Time:", remaining_time)
    print("Total time:", total_time)
    return total_time


def identify_towers_with_levels(upgrades):
    gap = int((661 - 196) / 9)
    points = []
    for x in range(9):
        point = (600, 196 + x * gap)
        points.append(point)
    print("Points", points)

    for point in points:
        result = get_tower(point)
        if result:
            tower_region = [point[0], point[1] - gap / 2, 200, gap]
            screen = get_screenshot(tower_region, filename="temp_tower")
            # show(screen)
            count = tower_count.read_screen(screen, show_image=False, return_number=True)
            if count == 0 or count == "": count = 1

            # print(result)
            existing = next((x for x in upgrades if x[0] == result[0] and x[1] == result[1]), None)
            if not existing:
                upgrades.append((result[0], result[1], count))
    return upgrades


def get_tower(loc):
    # Level
    pag.click(loc)
    time.sleep(0.35)
    filename = f'temp/temp_read_tower.png'
    pag.screenshot(filename, region=SELECTED_TOWER)
    screen = cv2.imread(filename, 0)
    tower_name = selected_tower.read_screen(screen)
    tower = return_tower(tower_name)
    if tower is None: return
    level_int = selected_level.read_screen(screen, show_image=False, return_number=True)
    level = tower.return_level(level_int)
    print("Get Tower", tower, level, level_int)

    return tower, level, 1


def get_count(screen, tower, screen_loc):
    # Count
    screen_count = screen[:, 0:200]
    count = tower_count.read_screen(screen_count, show_image=False, return_number=True)
    if count == 0 or count == "": count = 1
    return count


def select_tower(village, tower):
    print("Select tower:", tower)
    goto(main)
    if village == "main":
        region = BUILDER_LIST_REGION
    else:
        region = BUILDER_B_LIST_REGION
    if check_if_tower_visible(tower, region): return
    goto_list_top(village)
    bottom_image_previous, at_bottom, count = None, False, 0
    while not at_bottom and count < 5:
        screen = get_screenshot(region)
        val, loc, rect = find(tower.i_text, screen, show_image=False)
        print("Select tower", tower, val)
        if val > 0.8:
            click(tower.i_text, region=region)
            return True
        bottom_image_current = get_screenshot(BUILDER_BOTTOM)
        at_bottom = image_similar(bottom_image_previous, bottom_image_current)
        bottom_image_previous = bottom_image_current
        move_list("up", dur=1)
        time.sleep(.2)
        count += 1
    return False


def check_if_tower_visible(tower, region):
    click_builder()
    screen = get_screenshot(region)
    val, loc, rect = find(tower.i_text, screen, show_image=False)
    val1, loc2 = i_suggested_upgrades.find_screen(screen, return_location=True)
    # print(loc, loc2)
    if loc2[1] > loc[1]: return False
    if val > 0.85:
        click(tower.i_text, region=region)
        return True


def get_preference(available_towers):
    available_towers.sort(key=lambda x: x.priority, reverse=False)
    print("Available towers")
    for tower in available_towers:
        print(tower.name, tower.priority)
    if len(available_towers) == 0: return None
    chosen_upgrade = min(available_towers, key=attrgetter('priority'))
    print("Chosen upgrade:", chosen_upgrade)
    return chosen_upgrade


def get_preferences(available_towers):
    available_towers.sort(key=lambda x: x.priority, reverse=False)
    if wall in available_towers: available_towers.remove(wall)
    print("Get preferences (initial list):", objects_to_str(available_towers))

    preferences = []
    if len(available_towers) == 0: return preferences
    count = 0
    while count < 5:
        preference = available_towers[0]
        preferences.append(preference)
        # print("Round", count, "Available towers:", objects_to_str(available_towers))
        # print("Round", count, "Preferences:", objects_to_str(preferences))
        available_towers = [x for x in available_towers if x.resource != preference.resource]
        if len(available_towers) == 0:
            print("Get preferences (preferences):", objects_to_str(preferences))
            return preferences
        count += 1
    return preferences


def remove_tree(r, village):
    out_of_bounds = True
    if LIMITS[0] < r[0] < LIMITS[2] and LIMITS[1] < r[1] < LIMITS[3]: out_of_bounds = False
    if out_of_bounds: return

    print("Remove tree", r)
    click_rect(r)
    time.sleep(0.1)
    click_cv2("trees/remove_tree")
    time.sleep(2)
    pag.click(BOTTOM_LEFT)
    builders = False
    count = 0
    region = BUILDER_ZERO_REGION
    if village == "builder": region = BUILDER_B_ZERO_REGION
    while not builders and count < 65:
        time.sleep(1)
        val, loc, rect = find_cv2("builder_zero", region)
        # print("Remove tree - Zero Builder Val:", val)
        if val < 0.8:
            builders = True
        else:
            builders = False
        count += 1

def remove_trees_main():
    goto(main)
    time.sleep(0.1)
    screen = get_screenshot(region=BUILDER_ZERO_REGION, filename="builders")
    are_builders_available = False
    for x in available_builders:
        if x.find_screen(screen=screen):
            print(x.find_screen(screen=screen, return_result=True))
            are_builders_available = True
    if not are_builders_available:
        # print("No builders available", i_builder_zero.find_detail())
        return
    for tree in trees_main:
        if tree.find():
            print("Found tree:", tree)
            tree.click()
            time.sleep(0.1)
            i_tree_remove.click()
        # wait for a builder
        found, count = False, 0
        while not found and count < 300:
            screen = get_screenshot(region=BUILDER_ZERO_REGION, filename="builders")
            for x in available_builders:
                print(x, screen.shape, x.image.shape)
                if x.find_screen(screen=screen):
                    found = True
            time.sleep(0.1)
            count += 1

# file = "builder"
# screen = cv2.imread(f'temp/builders.png', 0)
# show(screen)

# for x in available_builders:
#     print(x, x.find_screen(screen=screen, return_result=True))

# i_app.click()
# time.sleep(0.1)
# remove_trees_main()
# time.sleep(0.1)
# i_app.click()


def remove_trees_old(village):
    zoom_out()
    for letter in ['w', 's']:
        hold_key(letter, 0.5)
        rects = find_many_array(BUSHES, confidence=0.82)
        # print(len(rects))
        for r in rects:
            remove_tree(r, village)


def upgrade(village):
    rects = i_upgrade_button.find_many(show_image=False)
    print("Upgrade - upgrade buttons found:", len(rects))
    if len(rects) == 0:
        rects = find_many("upgrade_2", confidence=0.75)
        print("Upgrade - upgrade2 (second attempt) buttons found:", len(rects))
    if len(rects) == 0:
        rects = find_many("upgrade_3", confidence=0.75)
        print("Upgrade - upgrade3 (third attempt) buttons found:", len(rects))

    sufficient_funds = False
    # print(rects)
    for rect in rects:
        region = (rect[0] - 20, rect[1] - 40, 130, 40)
        # image = get_screenshot(region)
        # show(image)
        result = has_cash(region)
        if result:
            sufficient_funds = True
            # print("Clicking")
            click_rect(rect)
    if not sufficient_funds:
        print("Upgrade - inadequate funds")
        return False

    time.sleep(0.5)
    # print("Hero identifier", i_hero_upgrade_identifier.find_detail(show_image=True, fast=False))
    if i_hero_upgrade_identifier.find(fast=False):
        print("Upgrade: hero")
        pag.click((1518, 851))
    else:
        print("Upgrade: non-hero")
        pag.click((1100, 851))

    click_cv2("red_cross")
    goto_list_top(village)

    return True


def upgrade_wall(currency, select_tower_bool=True):
    if select_tower_bool:
        select_tower("main", wall)
    result = i_upgrade_button.find_many(show_image=False)
    result = sorted(result, key=lambda x: x[0])
    print("Upgrade wall result:", result)
    if len(result) == 0:
        print(result)
        return False
    elif len(result) == 1:
        currency = "gold"
    if currency == "gold":
        rectangle = result[0]
    else:
        rectangle = result[1]
    spot = int(rectangle[0] + rectangle[2] / 2), int(rectangle[1] + rectangle[3] / 2)
    # print(spot)
    pag.click(spot)
    time.sleep(0.1)
    pag.click((1115, 877))
    return True


def has_cash_old(region):
    # Warden: Counter({(128, 128, 128): 3475, (0, 128, 128): 949, (0, 0, 0): 814, (0, 128, 0): 159, (0, 0, 128): 3})
    # Mortar: Counter({(128, 128, 128): 4093, (0, 0, 0): 924, (0, 128, 128): 131, (0, 128, 0): 52})
    # Wall (inadequate cash): Counter({(128, 128, 128): 3818, (0, 0, 0): 668, (0, 128, 128): 416, (0, 0, 128): 298})
    # Queen (adequate cash): Counter({(128, 128, 128): 3495, (0, 0, 0): 910, (0, 128, 128): 576, (0, 0, 128): 185, (0, 128, 0): 30, (128, 0, 128): 4})
    pag.screenshot('temp/upgrade_colour.png', region=region)
    image = cv2.imread('temp/upgrade_colour.png', 1)
    # show(image)
    new, counter = simplify(image, gradients=2)
    # print(counter)
    if counter[(128, 128, 0)] > 4000: return False  # This is the wall rings
    if counter[(0, 128, 128)] < 400: return True
    if counter[(0, 128, 0)] > 100 and counter[(0, 128, 128)] < 1000: return True  # This is the warden
    if counter[(0, 0, 0)] > 800 and counter[(0, 128, 128)] < 600: return True  # This is the queen
    return False


def has_cash_2(image):
    image = image[:, 0:400]
    # show(image)
    new, counter = simplify(image, gradients=2)

    print(counter)
    return counter[(0, 128, 128)] < 400


def create_combined_builders_image(accounts):
    account_images = []
    max_width = 0
    for account in accounts:
        no = account.number
        i1 = cv2.imread(f'temp/tracker/builders{no}main.png', 1)
        i2 = cv2.imread(f'temp/tracker/builder_time{no}main.png', 1)
        i3 = cv2.imread(f'temp/tracker/gold{no}.png', 1)
        i4 = cv2.imread(f'temp/tracker/research_time{no}main.png', 1)
        i5 = cv2.imread(f'temp/tracker/trader_clock_potion{no}.png', 1)
        i6 = cv2.imread(f'temp/tracker/trader_research_potion{no}.png', 1)
        i7 = cv2.imread(f'temp/tracker/builders{no}builder.png', 1)
        i8 = cv2.imread(f'temp/tracker/builder_time{no}builder.png', 1)
        i9 = cv2.imread(f'temp/tracker/remaining_attacks{no}.png', 1)

        i4 = cv2.resize(i4, (0, 0), fx=.65, fy=.65)
        i5 = cv2.resize(i5, (0, 0), fx=.25, fy=.25)
        i6 = cv2.resize(i6, (0, 0), fx=.25, fy=.25)

        combined = combine_image_horizontal([i1, i2, i3, i4, i5, i6, i7, i8, i9])
        account_images.append(combined)
        max_width = max(max_width, combined.shape[1])

    header = np.zeros((50, 200, 3), np.uint8)
    x = datetime.now().strftime("%I:%M") + datetime.now().strftime("%p").lower()
    cv2.putText(header, x, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    war_banner = cv2.imread(f'temp/tracker/war_banner.png', 1)
    war_banner = cv2.resize(war_banner, (0, 0), fx=.65, fy=.65)
    header = combine_image_horizontal([header, war_banner])

    images = [header] + account_images
    result = combine_image_vertical(images)
    # show(result)
    cv2.imwrite("C:/Users/darre/OneDrive/Darren/clash_bot/tracker/builders_combined.png", result)


def get_next_completion(account, village):
    print("Get next completion")
    if spare_builders(account, village) > 0: return
    goto_list_very_top(village)
    if i_upgrades_in_progress.find():
        pag.click(570, 250)
        time.sleep(0.15)
        pag.screenshot('temp/temp_read_tower.png', region=SELECTED_TOWER)
        screen = cv2.imread('temp/temp_read_tower.png', 0)
        level = selected_level.read_screen(screen, show_image=False)
        tower = selected_tower.read_screen(screen, show_image=False)
        # print("Get next completion:", tower, level)
        if level == "": level = None
        excel_write(account.number, "next_completion", (tower, level))
        return tower, level
    else:
        return None, None


def check_completion(account):
    if spare_builders(account, "main") == 0: return
    previous_completion = excel_read(account.number, "next_completion")
    next_completion = get_next_completion(account, "main")
    print("Check completion (next completion):", next_completion)
    result = "No result"
    if previous_completion == (None, None):
        result = "No previous result"
    elif previous_completion == next_completion:
        result = "No change"
    elif previous_completion != next_completion:
        result = f"Completed: {previous_completion[0]} level: {previous_completion[1]}"
        # excel_write(account.number, "completion", previous_completion)
        # progress(account, previous_completion)
    print("Check completion", previous_completion, next_completion, result)


def get_castle_resources():
    global current_location
    goto(l_castle)
    for i in [i_treasury, i_collect_castle, i_okay3]:
        time.sleep(0.2)
        i.click()
    current_location = main


def get_build_images(account):
    set_current_account()
    change_accounts_fast(account)
    goto_list_very_top("main")

    at_bottom, count = False, 0
    bottom_image_previous = None
    while not at_bottom and count < 13:

        file_name = f"/temp/build{account.number}_{count}.png"
        print(file_name)
        if os.path.exists(file_name): os.remove(file_name)
        get_screenshot(region=BUILDER_LIST_REGION, filename=f'build{account.number}_{count}')
        gap, dur = 250, 2
        pag.moveTo(855, 240 + gap)
        pag.dragTo(855, 240, dur)

        time.sleep(0.5)
        bottom_image_current = get_screenshot(BUILDER_BOTTOM)
        at_bottom = image_similar(bottom_image_previous, bottom_image_current)
        bottom_image_previous = bottom_image_current
        count += 1


def create_build_image(account):
    height_of_matching_area = 75
    image = cv2.imread(f'temp/build{account.number}_0.png', 1)
    print(f'temp/build{account.number}_0.png')
    # print(image)
    # if not image: return
    for x in range(1, 13):
        if not os.path.isfile(f'temp/build{account.number}_{x}.png'): continue
        print("Create build image:", x)
        bottom_bit = image[-height_of_matching_area:, 100:400]

        next_image = cv2.imread(f'temp/build{account.number}_{x}.png', 1)

        result = cv2.matchTemplate(next_image, bottom_bit, method)
        min_val, val, min_loc, loc = cv2.minMaxLoc(result)
        next_image = next_image[loc[1] + height_of_matching_area:]
        image = np.concatenate((image, next_image), axis=0)
        # print("Val, y:", val, loc[1])

    show(image, scale=0.5)
    cv2.imwrite(f"temp/build_{account.number}.png", image)


# get_build_images(bad_daz)
# create_build_image(bad_daz)

def find_image(screen, image, show_image=False):
    if show_image:
        show(screen)
        show(image)
    min_val, val, min_loc, loc = cv2.minMaxLoc(cv2.matchTemplate(screen, image, method))
    return val, loc


def remaining_time_of_upgrading_towers(account):
    total_time_heroes = timedelta(days=0)
    total_time_towers = timedelta(days=0)
    total_time_traps = timedelta(days=0)
    total_time = timedelta(days=0)

    step = 52
    goto_list_very_top("main")
    result = i_upgrades_in_progress.find_detail()
    x = result[1][0]
    start_y = result[1][1] + step
    result = i_suggested_upgrades.find_detail()
    max_y = result[1][1] - step // 2
    print(start_y, max_y)
    for y in range(start_y, max_y, step):
        pag.click(x, y)
        time.sleep(0.4)
        tower_string = selected_tower.read(SELECTED_TOWER)
        level_string = selected_level.read(SELECTED_TOWER)
        tower = return_tower(tower_string)
        # print(tower_string)
        level = None
        if tower:
            try:
                level = tower.return_level(int(level_string))
            except:
                level = 0
                print("Remaining time: couldn't read string:", level_string)
        if level:
            total_time_for_tower = tower.remaining_time(level, account.th)
            print(f"{tower}, Level: {level_string}, Time: {total_time_for_tower}")
            total_time += total_time_for_tower
            if tower.category == "hero": total_time_heroes += total_time_for_tower
            if tower.category == "defence": total_time_towers += total_time_for_tower
            if tower.category == "trap": total_time_traps += total_time_for_tower

    print("\nTotal time for currently upgrading towers (assuming 1 builder):")
    print("Total time (heroes):", int(total_time_heroes.days), "days")
    print("Total time (towers):", int(total_time_towers.days), "days")
    print("Total time (traps):", int(total_time_traps.days), "days")
    print("Total time:", int(total_time.days), "days\n")
    return total_time_heroes, total_time_towers, total_time_traps, total_time


# remaining_time_of_upgrading_towers(jon)

def analyse_build_image(account, include_upgrading=True):
    gap = 40
    height = 65
    file = f"temp/build_{account.number}.png"
    image_bw = cv2.imread(file, 0)
    image = cv2.imread(file, 1)
    max_y, _ = image_bw.shape
    # print(max_y)
    val, loc = find_image(image_bw, i_suggested_upgrades.image, show_image=False)
    current_y = loc[1]
    remaining_towers = []

    if include_upgrading:
        total_time_heroes, total_time_towers, total_time_traps, total_time = remaining_time_of_upgrading_towers(account)
    else:
        total_time_heroes, total_time_towers, total_time_traps, total_time = timedelta(), timedelta(), timedelta(), timedelta()
    finished, count, tower_count = False, 0, 1
    excel_values = []
    while not finished and count <= 60 and tower_count <= 100:
        current_y = current_y + gap
        if current_y + height > max_y:
            finished = True
            break
        region = image[current_y: current_y + height]
        region_bw = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        region_bw_mult = region_bw[:, 0:350]
        # show(region_bw_mult)
        tower_string, y = build_towers.read_screen(region_bw, return_y=True)
        mult = build_towers_mult.read_one_screen(region_bw_mult)
        cost = build_towers_cost.read_screen(region_bw, return_number=True)
        tower_string = tower_string.replace("barracksbarracks", "barracks")
        tower_string = tower_string.replace("bombbomb", "bomb")
        tower = return_tower(tower_string)
        if mult != 0 and cost != 0 and str(mult) == str(cost)[0]:
            cost = int(str(cost)[1:])
        if mult == 0 or not mult: mult = 1
        if y: current_y += y
        if len(tower_string) > 0 and tower is not None:
            for x in range(mult):
                remaining_towers.append(tower_string)

            current_level = tower.get_level_from_cost(cost)
            time_for_one_tower = tower.remaining_time(current_level, account.th)
            total_time_for_tower = time_for_one_tower * mult
            total_time += total_time_for_tower
            if tower.category == "hero": total_time_heroes += total_time_for_tower
            if tower.category == "defence": total_time_towers += total_time_for_tower
            if tower.category == "trap": total_time_traps += total_time_for_tower
            print(f"{tower_count}. {tower_string} x{mult}",
                  f"{cost:,.0f}. Total remaining time: {total_time_for_tower.days} days. [{tower.category}]")
            tower_count += 1
            if current_level is None:
                excel_values_one = [tower.name, "None", time_for_one_tower.days, mult, total_time_for_tower.days]
            else:
                excel_values_one = [tower.name, current_level.number, time_for_one_tower.days, mult, total_time_for_tower.days]
            excel_values.append(excel_values_one)
        count += 1

    print("\nTotal time (assuming 5 builders)")
    print("Total time (heroes):", int(total_time_heroes.days / 5), "days")
    print("Total time (towers):", int(total_time_towers.days / 5), "days")
    print("Total time (traps):", int(total_time_traps.days / 5), "days")
    print("Total time:", int(total_time.days / 5), "days")
    completion_date = datetime.today() + total_time / 5
    account.completion_date = completion_date
    db_account_update(account.number, "completion_date", completion_date)
    if total_time != 0:
        try:
            completion_string = f"Total: {total_time.days}. Heroes: {total_time_heroes.days} ({int(total_time_heroes/total_time*100)}%)"
        except:
            completion_string = ""
    else:
        completion_string = f"Total: {total_time.days}. Heroes: {total_time_heroes.days}"
    account.completion_string = completion_string
    db_account_update(account.number, "completion_string", completion_string)
    print(f"Completion date: {completion_date.day}/{completion_date.month}/{completion_date.year}")
    print(f"Completion string: {completion_string}")

    excel_write_rows(file="remaining_time", sheet=account.number, start_row=4, values=excel_values)

    # for values in excel_values:
    #     print(values)

    return completion_date
    # print(remaining_towers)

# analyse_build_image(bad_daz, include_upgrading=False)

def delete_build_files():
    if not os.path.isdir("temp"):
        os.makedirs("temp", exist_ok=True)
        os.makedirs("temp/tracker", exist_ok=True)
    files = os.listdir("temp")
    for file in files:
        result = False
        if file[0:5] == "build" and file[0:7] != "builder": result = True
        file = "temp/" + file
        # print(file, result)
        if result and os.path.isfile(file):
            os.remove(file)
            # print("Deleted:", file)

# delete_build_files()

def remaining_time_for_th(account, delete_files=True):
    if account == admin: return
    set_current_account()
    change_accounts_fast(account)
    get_build_images(account)
    create_build_image(account)
    analyse_build_image(account)
    if delete_files:
        delete_build_files()


# remaining_time_of_upgrading_towers(bob)

# for tower in towers: print(tower.name, tower.category)

# file = f"temp/tracker/time{6}.png"
# i = cv2.imread(file, 1)
# i = add_green_border(i)
# show(i)



# create_build_image(bob)

# print(analyse_build_image(bob))


# account = account_3
# print(account.th)
# create_build_image(jon)
# remaining_time_for_th(jon)
# analyse_build_image(account)
# goto(pycharm)
