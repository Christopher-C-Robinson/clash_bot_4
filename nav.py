import psutil

from towers_load import *
from images import *
from number_sets import *

ICONS = (300, 1012, 1200, 62)
TOP_LEFT = (0,0,300,100)
TOP_MIDDLE = (700,0,700,300)

locs = []
latest_path = None

def start_up():
    not_there_yet = True
    while not_there_yet:
        if not_there_yet:
            start_loop_again = False
        for i in [i_maximise, i_start_eyes, i_start_eyes_2, i_start_eyes_3, i_heart, i_bluestacks]:
            if start_loop_again: continue
            if i.find():
                i.click()
                start_loop_again = True
                if i.name == "i_maximise":
                    not_there_yet = False
            time.sleep(0.1)

def most_common(list, number):
    if len(list) == 0: return None
    number = min(number, len(list))
    data = Counter(list).most_common(number)
    number = min(number, len(data))
    return data[number - 1][0]

def hold_key(key, dur):
    # print("Pressing:", key)
    pag.keyDown(key)
    time.sleep(dur)
    pag.keyUp(key)

class Loc():
    def __init__(self, name, identifier=None, optional=False, accessible=True, regions=[], height=0, pause=False):
        self.name = name
        self.pause = pause
        self.accessible = accessible
        self.identifiers = [identifier, ]
        self.paths = []
        self.default_path = None
        self.sleep_path = self.Path(loc=self, destination=self, action="reload", parameter=None, expected_loc=self)
        self.height = height
        self.id_absence = False
        self.optional = optional
        self.regions = regions
        locs.append(self)

    def __str__(self):
        if self.name:
            return f"{self.name}"
        else:
            return "No name"

    def show_regions(self):
        goto(self)
        screen = get_screenshot(colour=1)
        for rectangle in self.regions:
            cv2.rectangle(screen, rectangle, (255, 0, 0), 3)
        show(screen, scale=0.6, dur=20000)


    class Path():
        def __init__(self, loc, destination, action, parameter, expected_loc, region=None):
            self.loc = loc
            self.destination = destination
            self.action = action
            self.parameter = parameter
            self.expected_loc = expected_loc
            self.actual_locs = []
            self.region = region
            loc.paths.append(self)
            # Load the image for clicks
            self.image = None
            # if action in ["click", "click_p", "pycharm_to_main"]:
            #     self.image = self.convert_parameter_to_image(parameter)

        # def format(self):
        #     return f"Path: {self.loc.name} -> {self.destination.name}"
        #
        def __str__(self):
            return f"Path: {self.loc.name} -> {self.destination.name} ({self.expected_loc})"

        def add_actual_loc(self, loc):
            if loc not in self.actual_locs:
                self.actual_locs = [loc] + self.actual_locs[0:10]

        def most_common_actuals(self):
            list = self.actual_locs
            actuals = []
            for x in range(1, 3):
                result = most_common(list, x)
                if result: actuals.append(result)
            return actuals

        def convert_parameter_to_image(self, parameter):
            path = f'images/nav/{parameter}.png'
            try:
                parameter = cv2.imread(path, 0)
                return parameter
            except:
                pass
                # print(f"Creating location: could not find {path}")


    # def add_regions(self, regions):
    #     self.regions += regions
    #
    # def show_regions(self, dur=5000):
    #     goto(self)
    #     screen = get_screenshot(colour=1)
    #     for x, y, w, h in self.regions:
    #         cv2.rectangle(screen, (x, y), (x + w, y + h), 255, 5)
    #     show(screen, scale=0.7, dur=dur)
    #
    def print_loc(self):
        print("Location:", self.name)
        for x in self.paths:
            print(" -", x)
            if x.actual_locs:
                for y in x.actual_locs:
                    print("   -", y.name)

    def add_path(self, destination, action, parameter, expected_loc, region=None):
        self.Path(loc=self, destination=destination, action=action, parameter=parameter, expected_loc=expected_loc, region=region)

    def add_default_path(self, action, parameter, expected_loc, region=None):
        new_path = self.Path(loc=self, destination=unknown, action=action, parameter=parameter,
                             expected_loc=expected_loc, region=region)
        self.default_path = new_path

    def add_identifier(self, image):
        self.identifiers.append(image)

    def add_height(self, height):
        self.height = height

    def perform_action(self, path):
        action = path.action
        parameter = path.parameter
        image = path.image
        expected_loc = path.expected_loc
        region = path.region
        successfully_found_icon = True

        global current_location
        global latest_path

        # print("Perform action:", action, parameter)
        outcome = False
        if action == "click":
            if parameter == "bottom_left":
                pag.click(BOTTOM_LEFT)
            else:
                # print("Click", path.parameter.find_detail())
                # print("Loc - perform action - click:", path.parameter)
                if path.parameter.find():
                    path.parameter.click()
                else:
                    print("Perform action (image to click not found):", path.parameter, path.parameter.find_detail())
        elif action == "click_p":
            found, count = False, 0
            while not found and count < 10:
                if path.parameter.find():
                    path.parameter.click()
                    found = True
                else:
                    time.sleep(0.1)
                    count += 1
        elif action == "pycharm_to_main":
            time.sleep(0.1)
            path.parameter.click()
            time.sleep(0.4)
            # hold_key("down", 0.1)
            # for x in range(5):
            #     # pag.press("down")
            #     hold_key("down", 0.1)
        elif action == "click_identifier":
            self.identifiers[0].click()
            # val, outcome = click(self.identifier_images[0])
            # print("Clicking identifier:", val)
        elif action == "reload":
            # print("Power down")
            # goto(main)
            reload()
            outcome = True
        elif action == "key":
            pag.press(parameter)
            outcome = True
        elif action == "key_p":
            time.sleep(0.1)
            pag.press(parameter)
            time.sleep(0.1)
            outcome = True
        elif action == "wait":
            time.sleep(parameter)
            outcome = True
        elif action == "from_ld_to_main":
            from_ld_to_main()
        elif action == "goto_forge":
            hold_key("a", 0.1)
            hold_key("s", 0.1)
            val, outcome = click_cv2("nav/forge_button")
        elif action == "goto_builder":
            goto_builder()
        elif action == "goto_lab":
            pag.click(BOTTOM_LEFT)
            for i_lab in lab.images:
                val, x, rect = i_lab.find_detail(fast=False, show_image=False)
                if val > i_lab.threshold:
                    i_lab.click()
                    time.sleep(0.2)
                    i_research.click()
                    time.sleep(0.2)
                    break
        elif action == "goto_castle":
            pag.click(BOTTOM_LEFT)
            for i in castles:
                val, x, rect = i.find_detail(fast=False, show_image=False)
                if val > i.threshold:
                    i.click()
                    time.sleep(0.2)
                    break
        elif action == "goto_clan":
            print("Goto clan")
            pag.click(BOTTOM_LEFT)
            goto(main)
            for image in [i_profile_star, i_my_clan_tab]:
                found, count = False, 0
                while not found and count < 5:
                    if image.find():
                        image.click()
                        found = True
                    else:
                        print(image.name, image.find_detail())
                    count += 1
        elif action == "goto_games":
            pag.click(BOTTOM_LEFT)
            time.sleep(0.2)
            zoom_out()
            hold_key("s", 0.1)
            successfully_found_icon = False
            if i_caravan.find():
                i_caravan.click()
                successfully_found_icon = True
            else:
                hold_key("s", 0.1)
                if i_caravan.find(fast=False):
                    i_caravan.click()
                    successfully_found_icon = True
                else:
                    print("Couldn't find caravan:", i_caravan.find_detail())
        elif action == "goto_main":
            return_from_builder()
        elif action == "start_bluestacks":
            os.startfile("C:\Program Files (x86)\BlueStacks X\BlueStacks X.exe")
            start_up()
            outcome = True
        elif action == "start_app":
            print("Action: start app")
            open_app()
            outcome = True
        elif action == "recovery":
            print("Action: recovery")
            recover()
            outcome = True
        elif action == "log_in":
            self.identifiers[0].click()
            # val, outcome = click(self.identifier_images[0])
            # print("Clicking identifier:", val)
            time.sleep(0.5)
            pag.click((1184, 651))
            # current_location = change_account
            # change_accounts(1)
        else:
            print("Action not coded:", action)
            return False

        # Validate location, and store unusual outcomes
        # for identifier in expected_loc.identifiers:
            # if identifier.wait(dur=2):
            #     print("Identifier success:", identifier.name)
            # else:
            #     print("Identifier failure:", identifier.name)
        found, count = False, 0
        while not found and count < 10:
            for x in expected_loc.identifiers:
                if x.find():
                    # print("Found:", x)
                    found = True
                    break
                if not found:
                    print("Not found:", x, x.find_detail())
            if not found:
                count += 1

        if successfully_found_icon:
            current_location = loc(expected_loc)
        else:
            current_location = loc(current_location)
        # print("Current location:", current_location)

        if current_location != expected_loc and current_location != unknown and path.destination != unknown:
            print()
            current_location = loc()
            path.add_actual_loc(current_location)
            print(f"Actual outcome added: {path.loc.name} -> {path.destination.name}. Actual: {current_location.name}")
            for x in path.actual_locs:
                print("   ", x.name)

        latest_path = path
        return outcome

    def goto(self, destination):
        global current_location
        # print(f"Loc goto: {current_location} -> {destination}")
        path_found = False
        path = [path for path in self.paths if path.destination == destination]
        check = False
        if path:
            # print(f"Goto Loc: {self.name}. {path[0]}")
            self.perform_action(path[0])
            check = True
            expected_location = path[0].expected_loc
        if not path and self.default_path:
            # for x in self.paths:
            #     print(x)
            # print("Using default path. Going to", destination)
            # print(f"Goto Loc (Default): {self.name}. {self.default_path}")
            path_found = self.perform_action(self.default_path)
            check = True
            expected_location = self.default_path.expected_loc

        # print("Goto (loc): check =", check)
        # if check:
        #     pass

        return path_found

    def has_path(self, destination):
        global current_location
        # print(f"Has path: {self} -> {destination}")
        path_found = False
        path = [path for path in self.paths if path.destination == destination]
        if path: return True
        if self.default_path: return True
        return False

def reload(rest_time=20):
    close_app()
    end_time = time_to_string(datetime.now() + timedelta(minutes=rest_time))
    print(f"Power down: {end_time}")
    add_power_down_to_image(f"Power down: {end_time}")
    time.sleep(60 * rest_time)
    open_app()


def goto_builder():
    zoom_out()
    found, count = False, 0
    while not found and count < 8:
        hold_key("d", 0.1)
        hold_key("w", 0.1)
        count += 1
        found = i_boat_to.find(fast=False)
    if found:
        i_boat_to.click()

def return_from_builder():
    zoom_out()
    found, count = i_boat_back.find(fast=False), 0
    while not found and count < 10:
        hold_key("s", 0.05)
        found = i_boat_back.find(fast=False)
        print(i_boat_back.find_detail())
        count += 1
    while not found and count < 8:
        for x in range(5):
            hold_key("a", 0.2)
        found = i_boat_back.find(fast=False)
        count += 1
    found, count = i_boat_back.find(fast=False), 0
    while not found and count < 10:
        hold_key("s", 0.05)
        found = i_boat_back.find(fast=False)
        print(i_boat_back.find_detail())
        count += 1
    if found:
        i_boat_back.click()

def add_power_down_to_image(text):
    image = cv2.imread("temp/tracker/status.png", 1)
    cv2.putText(image, text, (400, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    cv2.imwrite("C:/Users/darre/OneDrive/Darren/clash_bot/tracker/status.png", image)

def from_ld_to_main():
    found, count = False, 0
    while not found and count < 60:
        if i_clash_icon.find(fast=False):
            i_clash_icon.click()
            found = True
        if count % 10 == 0: i_app.click()
    if not found: return

    found, count = False, 0
    while not found and count < 60:
        val, loc, rect = i_builder.find_detail()
        print("From ld to main (builder val):", val)
        if val > 0.6 and val < i_builder.threshold:
            i_maximise.click()
        if val > i_builder.threshold:
            found = True
        if count % 20 == 0: i_app.click()
        count += 1
        time.sleep(1)

    return found

# -------------------
# ---- LOCATIONS ----
# -------------------

pycharm = Loc(name="pycharm", identifier=i_pycharm, accessible=True)
pycharm.height = -1
no_app = Loc(name="no_app", identifier=i_app, accessible=False)
no_app.id_absence = True
no_app.id_val_max = 0.8
no_app.height = -0.4
l_ldplayer = Loc(name="LD PLayer", identifier=i_clash_icon, accessible=False)
# no_bluestacks = Loc(name="no_bluestacks", identifier=i_bluestacks, accessible=False)
# no_bluestacks.id_absence = True
# no_bluestacks.id_val_max = 0.75
# no_bluestacks.height = -0.5
# maintenance = Loc(name="maintenance", identifier=i_maintenance, accessible=False)
maintenance2 = Loc(name="maintenance2", identifier=i_maintenance2, accessible=False)

main = Loc(name="main", identifier=i_builder, accessible=True, regions=main_regions)
unknown = Loc(name="unknown", identifier=i_x, accessible=False)
unknown.height = -0.5
chat = Loc(name="chat", identifier=i_challenge, accessible=True)
chat.height = main.height + 1
settings = Loc(name="settings", identifier=i_settings, accessible=True)
change_account = Loc(name="change_account", identifier=i_switch_account, accessible=True, pause=True)
change_account.height = settings.height + 1
# forge = Loc(name="forge", identifier=i_forge, accessible=True)
builder = Loc(name="builder", identifier=i_master_builder, accessible=True)
# builder.add_identifier(i_otto)

overlays = []
for overlay in [i_another_device, i_reload, i_reload_game, i_try_again, i_return_home, i_okay,
                i_return_home_2, i_return_home_3, i_red_cross, i_red_cross_2, i_red_cross_3, i_close_app, i_return_home_b]:
    new_overlay = Loc(name=overlay.name[2:], identifier=overlay, accessible=False)
    if overlay == i_another_device:
        new_overlay.add_default_path(action="reload", parameter=None, expected_loc=main)
        another_device = new_overlay
    elif overlay == i_return_home_b:
        new_overlay.add_default_path(action="click_identifier", parameter=None, expected_loc=builder)
    else:
        new_overlay.add_default_path(action="click_identifier", parameter=None, expected_loc=main)
    new_overlay.id_val_min = 0.8
    if overlay not in [i_red_cross, i_red_cross_2, i_red_cross_3, i_return_home_2, i_return_home_3]:
        new_overlay.add_height(4)
    overlays.append(new_overlay)

# log_in2 = Loc(name="log_in", identifier=i_bad_daz, accessible=False)
# log_in2.add_default_path(action="click_identifier", parameter=None, expected_loc=main)

# log_in = Loc(name="log_in", identifier=i_log_in, accessible=False)
# log_in.add_default_path(action="click_identifier", parameter=None, expected_loc=log_in2)

army_tab = Loc(name="army_tab", identifier=i_army_tab, accessible=True, regions=army_regions, height=1)
troops_tab = Loc(name="troops_tab", identifier=i_troops_tab, accessible=True, height=1)
spells_tab = Loc(name="spells_tab", identifier=i_spells_tab, accessible=True, height=1)
siege_tab = Loc(name="siege_tab", identifier=i_siege_tab, accessible=True, height=1)

l_lab = Loc(name="lab", identifier=i_research_upgrading, accessible=True)
l_lab.add_identifier(i_lab_girl)

l_games = Loc(name="games", identifier=i_games, accessible=False)
# l_castle = Loc(name="castle", identifier=i_treasury, accessible=True)
l_clan = Loc(name="clan", identifier=i_my_clan, accessible=True)

n_attack = Loc(name="attack", identifier=i_find_a_match, accessible=True)
n_attack.height = 2
find_a_match = Loc(name="find_a_match", identifier=i_next, accessible=True)
attacking = Loc(name="attacking", identifier=i_surrender, accessible=False)
# attacking_end_1 = Loc(name="attacking_end_1", identifier=i_surrender_okay, accessible=False)
attack_end = Loc(name="attack_end", identifier=i_return_home, accessible=False)

attack_b2 = Loc(name="attack_b2", identifier=i_versus_battle, accessible=True)
attack_b2.height = 3
attacking_b = Loc(name="attacking_b", identifier=i_defender, accessible=True)
# attacking_b_end_1 = Loc(name="attacking_b_end_1", identifier=i_surrender_okay, accessible=False)

# ---------------
# ---- PATHS ----
# ---------------

# Start-up
pycharm.add_default_path(action="pycharm_to_main", parameter=i_app, expected_loc=main, region=ICONS)
# pycharm.add_default_path(action="pycharm_to_main", parameter=i_app, expected_loc=builder, region=ICONS)
unknown.add_default_path(action="wait", parameter=0.2, expected_loc=main)
# no_bluestacks.add_default_path(action="start_bluestacks", parameter=None, expected_loc=main)
no_app.add_default_path(action="start_app", parameter=None, expected_loc=main)
# maintenance.add_default_path(action="reload", parameter=None, expected_loc=main)
maintenance2.add_default_path(action="reload", parameter=None, expected_loc=main)
l_ldplayer.add_default_path(action="from_ld_to_main", parameter=None, expected_loc=main)


# Main
main.add_path(destination=pycharm, action="click", parameter=i_pycharm_icon, expected_loc=pycharm)
main.add_path(destination=chat, action="click", parameter=i_open_chat, expected_loc=chat)
main.add_path(destination=army_tab, action="click", parameter=i_army, expected_loc=army_tab)
main.add_path(destination=troops_tab, action="click", parameter=i_army, expected_loc=army_tab)
main.add_path(destination=spells_tab, action="click", parameter=i_army, expected_loc=army_tab)
main.add_path(destination=siege_tab, action="click", parameter=i_army, expected_loc=army_tab)
main.add_path(destination=settings, action='click', parameter=i_settings_on_main, expected_loc=settings)
main.add_path(destination=change_account, action='click', parameter=i_settings_on_main, expected_loc=settings)
# main.add_path(destination=forge, action='goto_forge', parameter='', expected_loc=forge)
main.add_path(destination=builder, action="goto_builder", parameter='', expected_loc=builder)
main.add_path(destination=find_a_match, action="click", parameter=i_attack, expected_loc=n_attack)
main.add_path(destination=n_attack, action="click_p", parameter=i_attack, expected_loc=n_attack)
main.add_path(destination=attack_b2, action="goto_builder", parameter="", expected_loc=builder)
main.add_path(destination=attacking_b, action="goto_builder", parameter="", expected_loc=builder)
main.add_path(destination=l_lab, action="goto_lab", parameter="", expected_loc=l_lab)
main.add_path(destination=l_games, action="goto_games", parameter="", expected_loc=l_games)
# main.add_path(destination=l_castle, action="goto_castle", parameter="", expected_loc=l_castle)
main.add_path(destination=l_clan, action="goto_clan", parameter="", expected_loc=l_clan)

# Builder
builder.add_path(destination=pycharm, action="click", parameter=i_pycharm_icon, expected_loc=pycharm)
builder.add_path(destination=chat, action="key", parameter="c", expected_loc=chat)
builder.add_path(destination=settings, action='click', parameter=i_settings_on_main, expected_loc=settings)
builder.add_path(destination=change_account, action='click', parameter=i_settings_on_main, expected_loc=settings)
builder.add_path(destination=main, action="goto_main", parameter='', expected_loc=main)
builder.add_path(destination=attack_b2, action="click", parameter=i_attack_b, expected_loc=attack_b2)
builder.add_path(destination=attacking_b, action="click", parameter=i_attack_b, expected_loc=attack_b2)
builder.add_default_path(action="goto_main", parameter='', expected_loc=main)

# Research
l_lab.add_default_path(action="click", parameter=i_red_cross_2, expected_loc=main)

# Games
l_games.add_default_path(action="click", parameter=i_red_cross_games, expected_loc=main)

# Castle
# l_castle.add_default_path(action="click", parameter="bottom_left", expected_loc=main)

# Clan
l_clan.add_default_path(action="click", parameter="bottom_left", expected_loc=main)

# Chat
chat.add_height(1)
chat.add_default_path(action="click", parameter=i_close_chat, expected_loc=main)

# Settings
settings.add_path(destination=change_account, action="click_p", parameter=i_change_accounts_button, expected_loc=change_account)
settings.add_default_path(action="click", parameter=i_red_cross_settings, expected_loc=main)
change_account.add_default_path(action="click", parameter=i_close_switch_account, expected_loc=settings)
change_account.height = settings.height + 1

# Forge
# forge.add_default_path(action="click", parameter=i_red_cross_2, expected_loc=main)
# forge.add_height(main.height + 1)

# Army tabs
army_tab.add_default_path(action="click", parameter=i_red_cross_5, expected_loc=main)
troops_tab.add_default_path(action="click", parameter=i_red_cross_5, expected_loc=main)
spells_tab.add_default_path(action="click", parameter=i_red_cross_5, expected_loc=main)
siege_tab.add_default_path(action="click", parameter=i_red_cross_5, expected_loc=main)

army_tab.add_path(destination=troops_tab, action="click", parameter=i_troops_tab_dark, expected_loc=troops_tab)
army_tab.add_path(destination=spells_tab, action="click", parameter=i_spells_tab_dark, expected_loc=spells_tab)
army_tab.add_path(destination=siege_tab, action="click", parameter=i_siege_tab_dark, expected_loc=siege_tab)
troops_tab.add_path(destination=spells_tab, action="click", parameter=i_spells_tab_dark, expected_loc=spells_tab)
troops_tab.add_path(destination=siege_tab, action="click", parameter=i_siege_tab_dark, expected_loc=siege_tab)
troops_tab.add_path(destination=army_tab, action="click", parameter=i_army_tab_dark, expected_loc=army_tab)
spells_tab.add_path(destination=troops_tab, action="click", parameter=i_troops_tab_dark, expected_loc=troops_tab)
spells_tab.add_path(destination=siege_tab, action="click", parameter=i_siege_tab_dark, expected_loc=siege_tab)
spells_tab.add_path(destination=army_tab, action="click", parameter=i_army_tab_dark, expected_loc=army_tab)
siege_tab.add_path(destination=troops_tab, action="click", parameter=i_troops_tab_dark, expected_loc=troops_tab)
siege_tab.add_path(destination=spells_tab, action="click", parameter=i_spells_tab_dark, expected_loc=spells_tab)
siege_tab.add_path(destination=army_tab, action="click", parameter=i_army_tab_dark, expected_loc=army_tab)

# Attacking
n_attack.add_path(destination=find_a_match, action="click", parameter=i_find_a_match, expected_loc=find_a_match)
find_a_match.add_default_path(action="click", parameter=i_end_battle, expected_loc=main)
attacking.add_default_path(action="click", parameter=i_surrender, expected_loc=main)
n_attack.add_default_path(action="click", parameter=i_red_cross_attack, expected_loc=main)

attack_b2.add_default_path(action="click", parameter=i_return_home, expected_loc=builder)
attack_b2.add_path(destination=attacking_b, action='click', parameter=i_find_now_b, expected_loc=attacking_b)
attacking_b.add_default_path(action='click', parameter=i_surrender, expected_loc=attack_b2)
# attacking_b_end_1.add_default_path(action="click_identifier", parameter=None,expected_loc=attack_b2)

def goto(destination, depth=0):
    global current_location
    admin.goto_depth += 1
    # print("Goto depth", admin.goto_depth)
    if admin.goto_depth > 8:
        reload(2)
        admin.goto_depth = 0
        return current_location
    # print(f"Goto (Initial): {current_location} -> {destination}")
    if current_location == destination:
        admin.goto_depth = 0
        return
    loop_count = 0
    path_found = True
    while current_location != destination and path_found and loop_count < 8 and current_location:
        # print(f"Goto: {current_location} => {destination}")
        path_found = current_location.has_path(destination)
        result = current_location.goto(destination)
        loop_count += 1
        # print("Goto loop count:", loop_count)
        if destination.pause: time.sleep(2)
        current_location = loc(current_location) # This validates that expectations match reality wrt location
        # print("Current location:", current_location)
    if not path_found:
        # for path in current_location.paths:
        #     print(path)
        # print(current_location, destination, path_found, loop_count)
        print(f"Path not found (loc): {current_location} -> {destination}")
    if loop_count >= 7:
        print("Loop count:", loop_count)
        loop_count = 0
        reload(1)

    admin.goto_depth = 0
    print("Goto complete:", current_location)
    return current_location

def loc(guess=None):
    global current_location
    time.sleep(0.2)
    if guess and guess != unknown:
        guesses = [guess]
        if latest_path:
            guesses += latest_path.most_common_actuals()
        for guess in guesses:
            for identifier in guess.identifiers:
                val, loc, rect = identifier.find_detail(fast=False, show_image=False)
                result = val > identifier.threshold
                if result != guess.id_absence:
                    # print(identifier.name, val, result, val)
                    # print("Loc guess", guess)
                    current_location = guess
                    return current_location
                print("Loc guess (fail)", guess, identifier.name, val, identifier.threshold)
            if guess == find_a_match or guess == attacking_b:
                for x in range(30):
                    for identifer in guess.identifiers:
                        if identifer.find(): return current_location
                    time.sleep(0.1)
    for location in locs:
        if location.height >= 4:
            for identifier in location.identifiers:
                val, loc, rect = identifier.find_detail(fast=True)
                result = val > identifier.threshold
                if result != location.id_absence:
                    current_location = location
                    # print("Loc success (overlays)", location, "FAST", identifier.name, round(val,2), identifier.threshold, result)
                    return current_location
                # print("Loc fail (overlays)", location, "FAST", identifier.name, round(val,2), identifier.threshold, identifier.regions)

    current_location = unknown
    # Search all locations quickly then thoroughly
    # print("B", datetime.now() - start_time)
    for location in locs:
        # print("C", datetime.now() - start_time)
        for identifier in location.identifiers:
            val, loc, rect = identifier.find_detail(fast=True)
            result = val > identifier.threshold
            if result != location.id_absence:
                current_location = location
                print("Loc success (all locations)", location, "FAST", identifier.name, round(val,2), identifier.threshold, result)
                return current_location
            # print("Loc fail (all locations)", location, "FAST", identifier.name, round(val,2), identifier.threshold, identifier.regions, location.height)
    time.sleep(0.5)
    for location in locs:
        # print("C", datetime.now() - start_time)
        for identifier in location.identifiers:
            val, loc, rect = identifier.find_detail(fast=False)
            result = val > identifier.threshold
            if result != location.id_absence:
                current_location = location
                # print("Loc success (all locations)", location, location.height, "SLOW", identifier.name, round(val,2), identifier.threshold, result)
                return current_location
            # print("Loc fail (all locations)", location, location.height, "SLOW", identifier.name, round(val,2), identifier.threshold, identifier.regions)
            # if identifier.name == "i_find_a_match":
            #     i_multiplayer.find_detail(show_image=True)
    time.sleep(0.5)

    # print("D", datetime.now() - start_time)
    print(f"Loc: (guess unsuccessful). Guess:{guess}. Actual:{current_location}")

    return current_location

def click_builder():
    # print("Click builder")
    pag.click(BOTTOM_LEFT)
    for image in [i_builder, i_master_builder]:
        if image.find():
            image.click()
            return True

    return False

def move_list(direction, dur=0.5):
    if direction == "up":
        pag.moveTo(855,630)
        pag.dragTo(855,250, dur)
    if direction == "down":
        # pag.press("s")
        pag.moveTo(855,250)
        pag.dragTo(855,630, dur)

def goto_list_top(village):
    # print("Goto list top")
    if village == "main": goto(main)
    else: goto(builder)
    # click_builder()
    time.sleep(.2)
    pag.click(BOTTOM_LEFT)
    time.sleep(.2)
    click_builder()
    at_top = False
    count = 0
    time.sleep(0.2)
    while not at_top and count < 3:
        # print(i_suggested_upgrades.find_detail(fast=False))
        if i_suggested_upgrades.find(fast=False, show_image=False):
            at_top = True
        if not at_top:
            move_list("down", 1)
            time.sleep(0.2)
        count += 1
    time.sleep(2)
    val, loc, rect = i_suggested_upgrades.find_detail()
    # print("Goto list top", val)
    pag.moveTo(855, loc[1])
    pag.dragTo(855,210, .5)
    time.sleep(2)

def goto_list_very_top(village):
    if village == "main": goto(main)
    else: goto(builder)
    time.sleep(0.5)
    pag.click(BOTTOM_LEFT)
    click_builder()
    at_top = False
    count = 0
    while not at_top and count < 5:
        if i_upgrades_in_progress.find(show_image=False):
            at_top = True
        else:
            move_list("down", 1)
            time.sleep(0.2)
        count += 1

def format_list_of_locs(locs):
    output = ""
    for x in locs:
        output += x.name + ", "
    return output

def print_locs():
    print()
    print("ALL LOCATIONS")
    for x in locs:
        print()
        print(x.name)
        for path in x.paths:
            print(" -", path)
            for added in path.actual_locs:
                print("   -", added.name)





# OLD NAV

def attack_b_get_screen():
    time.sleep(1)
    pag.screenshot('temp/attack_b/attacking_b.png')

def zoom_out():
    # print("Zooming out")
    time.sleep(0.1)

    pag.keyDown('ctrl')

    for x in range(7):
        hold_key('o', 0.2)

    pag.keyUp('ctrl')


def start():
    click_cv2('bluestacks_icon')
    time.sleep(.2)
    # pag.moveTo(1000,500)
    pag.keyDown('ctrl')
    for x in range(5):
        pag.scroll(-100)
    pag.keyUp('ctrl')

def end():
    click_cv2("pycharm")


def current_resources(show_image=False):
    time.sleep(.1)
    result_array = []
    for region in [RESOURCES_G]:
    # for region in [RESOURCES_G, RESOURCES_E, RESOURCES_D]:
        result_array.append(resource_numbers.read(region, show_image=show_image, return_number=True))
    if result_array[0] > 50000000: result_array[0] = result_array[0]/10
    # print("Current Resources:", result_array)
    return result_array

def reset():
    if "BlueStacksWeb.exe" in (p.name() for p in psutil.process_iter()):
        print("Bluestacks Running")
        # click_cv2('bluestacks_icon')
        goto("main")
    else:
        os.startfile("C:\Program Files (x86)\BlueStacks X\BlueStacks X.exe")
        wait_cv2('start_d')
        pag.click((338,603)) # this is the love heart
        time.sleep(15)
        i_start_eyes.click()
        i_start_eyes_2.click()
        i_start_eyes_3.click()
        wait_and_click('maximise')
        wait_cv2("attack")

def open_app_old():
    global current_location
    success = False
    while not success:
        current_location = loc(current_location)
        if current_location == "pycharm_running":
            click_cv2("nav/bluestacks")
        else:
            click_cv2("nav/" + current_location.name)
            if current_location == "heart": current_location = "start_eyes"
            elif current_location == "start_eyes": current_location = "maximise"
            elif current_location == "maximise": current_location = "main"
        if current_location not in ["pycharm_running", "start_eyes", "heart", "maximise", ]: # loc doesn't return maximise if it finds it at the top of the screen (above y = 100)
            success = True
        if current_location == "pycharm_running": current_location = None
        time.sleep(1)

def recover():
    images = [i_close_app, i_close, i_minimise]
    multi_click(images)

    found = False
    for x in range(3):
        time.sleep(0.2)
        if i_app_player_1.find():
            i_app_player_1.click(button=right)
            found = True
        else:
            i_minimise.click()
    if not found:
        print("Couldn't find app_1")

    images = [i_run_as_admin, i_yes, i_maximise, i_barb]
    multi_click(images)

def open_app():
    for x in range(5):
        if not i_clash_icon.find():
            i_app.click()
        else:
            i_clash_icon.click()
            return
        time.sleep(0.3)

def close_app():
    i_close_cross.click()
    # time.sleep(0.2)
    # i_close_close.click()

def tour(start=0, end=13):
    list = [main, chat, settings, change_account, army_tab, troops_tab, spells_tab, siege_tab, n_attack, find_a_match, forge, builder, attacking_b]
    count = 0
    for location in list:
        if start <= count <= end:
            print()
            print("Tour:", location)
            goto(location)
        count += 1

def spare_builders(account, village):
    # print(village)
    if village == "main":
        # print("Spare builder - going to main")
        goto(main)
        region = BUILDER_ZERO_REGION
    else:
        # print("Spare builder - going to builder")
        goto(builder)
        region = BUILDER_B_ZERO_REGION
    screen = get_screenshot(region, filename=f"tracker/builders{account.number}{village}")
    if i_builder_zero.find_screen(screen, show_image=False): return 0
    if i_builder_one.find_screen(screen): return 1
    return 2

def spare_builders_read(account, village):
    # print(village)
    if village == "main": region = BUILDER_ZERO_REGION
    else: region = BUILDER_B_ZERO_REGION

    screen = get_screenshot(region, filename=f"tracker/builders{account.number}{village}")
    if i_builder_zero.find_screen(screen, show_image=False): return 0
    if i_builder_one.find_screen(screen): return 1
    return 2

def change_current_location(loc):
    global current_location
    current_location = loc


# Set-up
locs.sort(key=lambda x: x.height, reverse=True)
current_location = pycharm
