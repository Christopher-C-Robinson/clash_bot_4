from object_recognition import *
from regions import *
from excel import *
from sql_image import *
import shutil

images = []
list_of_new_images = []
    # "i_app", "pycharm", "i_pycharm",
    # "bomber", "machine",
    # "barb", "bomber", "giant", "pekka", "machine",
# ]
class Image():
    def __init__(self, file, name=None, threshold=0.79, always_slow=False, no_of_regions=5, region_limit=None, type=None, screen=None, level=None):
        if not name: name = file
        self.name = name
        self.image = None
        if not os.path.isfile(file):
            if "troops" in file:
                try:
                    scale = 1
                    source = file.replace("troops", "troops/new")
                    destination = file
                    shutil.copy(source, destination)
                    self.image = cv2.resize(cv2.imread(file, 0), (0,0), fx=scale, fy=scale)
                except:
                    self.image = None
                    admin.missing_images += 1
                    print(f"{admin.missing_images}. No troop file for:", name)
        else:
            # print("Set up image (file found):", self, file)
            self.image = cv2.imread(file, 0)
        self.regions = []
        self.region_limit = region_limit
        self.threshold = threshold
        self.always_slow = always_slow
        self.no_of_regions = no_of_regions
        self.loc = None
        self.level = level
        if type: self.type = type
        else: self.type = "Not specified"
        self.load_regions()
        images.append(self)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return "No name provided"

    def add_loc(self, loc):
        self.loc = loc

    def show_regions_on_screen(self):
        screen = get_screenshot(colour=1)
        for rectangle in self.regions:
            cv2.rectangle(screen, rectangle, (255, 0, 0), 3)
        show(screen, scale=0.6)

    def click(self, button="left", y_offset=0, show_loc=False):
        val, loc, rect = self.find_detail(fast=True)
        if val < self.threshold:
            val, loc, rect = self.find_detail(fast=False, show_image=False)
        if val > self.threshold:
            loc = (max(loc[0], LIMITS[0]), loc[1] + y_offset)
            if button == "left":
                if show_loc:
                    print("Click left:", loc)
                pag.click(loc)
            else:
                pag.moveTo(loc)
                pag.click(button="right")
            return True
        else:
            # print("Click Failure:", self.name, round(val,2), self.threshold)
            return False

    def click_region(self, region, show_image=False):
        screen = get_screenshot(region)
        result = cv2.matchTemplate(screen, self.image, method)
        min_val, val, min_loc, loc = cv2.minMaxLoc(result)
        rect = (loc[0] + region[0], loc[1] + region[1], self.image.shape[1], self.image.shape[0])
        loc = (int(rect[0] + rect[2] / 2), int(rect[1] + rect[3] / 2))
        if show_image:
            show(self.image)
            show(screen)
            print("Click region:", round(val, 2))
        # print("Click region", round(val,2), self.threshold)
        if val > self.threshold:
            pag.click(loc)
            return True
        return False

    def wait(self, dur=1):
        increment = 0.2
        for x in range(int(dur / increment)):
            time.sleep(increment)
            val, loc, rect = self.find_detail(fast=False)
            # print("Wait", val)
            if val > self.threshold: return True
        val, loc, rect = self.find_detail(fast=False, show_image=False)
        # print("Wait (slow)", val)
        if val > self.threshold: return True
        return False

    def find(self, show_image=False, fast=False, show_result=False):
        val, loc, rect = self.find_detail(show_image=show_image, fast=fast)
        if show_result:
            print("Find:", val, self.threshold, val > self.threshold, loc)
        return val > self.threshold

    def check_colour(self, fast=False):
        val, loc, rect = self.find_detail(fast=fast)
        if val < self.threshold: return False
        image = get_screenshot(rect, colour=1)
        if image is None: return False
        y, x, channels = image.shape
        spots = [(1 / 4, 1 / 4), (1 / 4, 3 / 4), (3 / 4, 1 / 4), (3 / 4, 3 / 4), (7 / 8, 1 / 8), (0.95, 0.05)]
        count = 0
        for s_x, s_y in spots:
            pixel = image[int(y * s_y)][int(x * s_x)]
            blue, green, red = int(pixel[0]), int(pixel[1]), int(pixel[2])
            if abs(blue - green) > 5 or abs(blue - red) > 5: count += 1
        colour = False
        if count > 1: colour = True
        return colour

    def colour(self, show_image=False):
        val, loc, rect = self.find_detail(fast=False)
        image = get_screenshot(rect, colour=1)
        if image is None: return False
        if show_image: show(image)
        y, x, channels = image.shape
        spots = [(1 / 4, 1 / 4), (1 / 4, 3 / 4), (3 / 4, 1 / 4), (3 / 4, 3 / 4), (7 / 8, 1 / 8), (0.95, 0.05)]
        colour = 0
        for s_x, s_y in spots:
            pixel = image[int(y * s_y)][int(x * s_x)]
            blue, green, red = int(pixel[0]), int(pixel[1]), int(pixel[2])
            colour += abs(blue - green) + abs(blue - green) + abs(red - green)
        return colour

    def colours(self):
        val, loc, rect = self.find_detail(fast=False)
        image = get_screenshot(rect, colour=1)
        if image is None: return False
        return cv2.mean(image)

    def find_detail(self, show_image=False, fast=False):
        if self.image is None:
            print("Find - No image provided:", self.name)
            return 0, 0, 0
        if self.always_slow: fast = False
        if len(self.regions) == 0: fast = False
        # Regions
        for region in self.regions:
            screen = get_screenshot(region)
            if show_image:
                show(self.image)
                show(screen)
            try:
                result = cv2.matchTemplate(screen, self.image, method)
            except:
                if screen is None:
                    print("Find detail - No screen:")
                    return 0, 0, 0
                print("Image didn't fit in region:", self.name)
                self.increase_regions()
                db_image_update(self, False)
                return 0, 0, 0

            min_val, val, min_loc, loc = cv2.minMaxLoc(result)
            rect = (loc[0] + region[0], loc[1] + region[1], self.image.shape[1], self.image.shape[0])
            loc = (int(rect[0] + rect[2] / 2), int(rect[1] + rect[3] / 2))
            if val > self.threshold:
                db_image_update(self, True)
                return round(val, 2), loc, rect
        if fast:
            db_image_update(self, False)
            return 0, 0, 0
        # Whole screen
        if self.region_limit:
            screen = get_screenshot(self.region_limit)
        else:
            screen = get_screenshot()
        if show_image:
            show(self.image)
            show(screen)
        try:
            result = cv2.matchTemplate(screen, self.image, method)
        except:
            db_image_update(self, False)
            return 0, 0, 0
        min_val, val, min_loc, loc = cv2.minMaxLoc(result)
        region_limit_x, region_limit_y = 0, 0
        if self.region_limit:
            region_limit_x = self.region_limit[0]
            region_limit_y = self.region_limit[1]

        # print("Region limit:", self, region_limit_x, region_limit_y)

        rect = (loc[0] + region_limit_x, loc[1] + region_limit_y, self.image.shape[1], self.image.shape[0])
        loc = (int(rect[0] + rect[2] / 2 + region_limit_x), int(rect[1] + rect[3] / 2 + region_limit_y))
        region = [max(rect[0] - 1, 0), max(rect[1] - 1, 0), rect[2] + 2, rect[3] + 2]
        if val > self.threshold:
            # print("Val > threshold", self.region_limit, self.check_region_limit(region))
            if self.region_limit is None or self.check_region_limit(region):
                # print("Save region")
                self.save_region(region)
        # excel_write_image(self, val > self.threshold)
        db_image_update(self, val > self.threshold)
        return round(val,2), loc, rect

    def find_screen(self, screen, show_image=False, return_location=False, return_result=False):
        if self.image is None:
            print("Find - No image provided:", self.name)
            return False, (0, 0)
        if show_image:
            show(self.image)
            show(screen)
        result = cv2.matchTemplate(screen, self.image, method)
        min_val, val, min_loc, loc = cv2.minMaxLoc(result)
        if return_result and return_location: return val > self.threshold, round(val,2), loc
        if return_result: return val > self.threshold, round(val,2)
        if return_location: return val > self.threshold, loc
        return val > self.threshold


    def find_screen_many(self, screen, show_image=False):
        # print("Find screen many:", self)
        if self.image is None: return []
        h, w = self.image.shape
        if show_image:
            show(self.image)
            show(screen)
        result = cv2.matchTemplate(screen, self.image, method)
        yloc, xloc = np.where(result >= self.threshold)
        z = zip(xloc, yloc)

        rectangles = []
        for (x, y) in z:
            rectangles.append([int(x), int(y), int(w), int(h)])
            rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)

        return rectangles

    def find_many(self, show_image=False):
        h, w = self.image.shape
        screen = get_screenshot()
        if show_image:
            show(self.image)
            show(screen)
        try:
            result = cv2.matchTemplate(screen, self.image, method)
        except:
            print("Find many failure:", screen.shape, self.image.shape)
            return []
        # min_val, val, min_loc, loc = cv2.minMaxLoc(result)
        # print("Find many:", self, val)
        yloc, xloc = np.where(result >= self.threshold)
        z = zip(xloc, yloc)

        rectangles = []
        for (x, y) in z:
            rectangles.append([int(x), int(y), int(w), int(h)])
            rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)

        return rectangles

    def check_region_limit(self, region):
        if self.region_limit is None: return True
        within_region = True
        if region[0] < self.region_limit[0]: within_region = False
        if region[1] < self.region_limit[1]: within_region = False
        if region[0] + region[2] > self.region_limit[0] + self.region_limit[2]: within_region = False
        if region[1] + region[3] > self.region_limit[1] + self.region_limit[3]: within_region = False
        return within_region

    def increase_regions(self):
        for region in self.regions:
            print(region[2], self.image.shape[1])
            if region[2] < self.image.shape[1]:
                region[2] = self.image.shape[1]
            print(region[3], self.image.shape[0])
            if region[3] < self.image.shape[0]:
                region[3] = self.image.shape[0]
            self.save_region(region)

    def load_regions(self):
        self.regions = []
        if self.image is None: return
        regions = db_regions_get(self, type=self.type)
        min_y, min_x = self.image.shape
        for r in regions:
            region = [r[1], r[2], max(r[3], min_x), max(r[4], min_y)]
            r2 = [r[1], r[2], r[3], r[4]]
            check_region = self.check_region_limit(region)
            if self.region_limit is None or check_region:
                if region and region in self.regions:
                    db_regions_delete(self, r2)
                if region and region not in self.regions:
                    self.regions.append(region)
            if not check_region:
                db_regions_delete(self, r2)

    def save_region(self, region):
        if region not in self.regions:
            db_regions_add(self, region, type=self.type)
            self.load_regions()

    def show(self):
        show(self.image)

    def show_regions(self):
        total_area = 0
        for region in self.regions:
            print(region)
            total_area += region[2] * region[3]

    def merge_regions(self):
        self.load_regions()
        start = len(self.regions)
        if len(self.regions) == 0: return
        min_increase = None
        min_region_a = None
        min_region_b = None
        min_region_c = None
        total_area = 0
        for region_a in self.regions:
            total_area += region_a[2] * region_a[3]

        for region_a in self.regions:
            for region_b in self.regions:
                if region_a == region_b: continue
                if region_a[0] == region_b[0] and region_a[1] == region_b[1] and region_a[2] == region_b[2] and region_a[3] == region_b[3]:
                    db_regions_delete(self, min_region_b)
                    self.load_regions()
                    continue
                size_a = region_a[2] * region_a[3]
                size_b = region_b[2] * region_b[3]
                combined_x1 = min(region_a[0], region_b[0])
                combined_x2 = max(region_a[0] + region_a[2], region_b[0] + region_b[2])
                combined_w = combined_x2 - combined_x1
                combined_y1 = min(region_a[1], region_b[1])
                combined_y2 = max(region_a[1] + region_a[3], region_b[1] + region_b[3])
                combined_h = combined_y2 - combined_y1
                size_c = combined_w * combined_h
                increase = size_c - size_a - size_b
                if min_increase is None or increase < min_increase:
                    min_increase = increase
                    min_region_a = region_a
                    min_region_b = region_b
                    min_region_c = [combined_x1, combined_y1, combined_w, combined_h]
        if len(self.regions) <= self.no_of_regions and min_increase and min_increase > 0:
            return False
        if min_region_a is None or min_region_b is None:
            return False
        db_regions_delete(self, min_region_a, type=self.type)
        db_regions_delete(self, min_region_b, type=self.type)
        self.save_region(min_region_c)
        if start > len(self.regions):
            print("Merge regions", self, start, len(self.regions))
        return True




# Navigation images
# i_ad_cross = Image(name="i_ad_cross", file='images/nav/ad_cross.png')
# i_ad_back = Image(name="i_ad_cross", file='images/nav/ad_back.png')
i_app = Image(name="i_app", file='images/nav/app.png')
i_another_device = Image(name="i_another_device", file='images/nav/another_device.png')
i_army = Image(name="i_army", file='images/nav/army.png')
i_army_tab = Image(name="i_army_tab", file='images/nav/army_tab.png')
i_army_tab_dark = Image(name="i_army_tab_dark", file='images/nav/army_tab_dark.png')
i_attack = Image(name="i_attack", file='images/nav/attack.png')
i_attack_b = Image(name="i_attack_b", file='images/nav/attack_b.png')
i_attacking = Image(name="i_attacking", file='images/nav/attacking.png')
i_battle_end_b1 = Image(name="i_battle_end_b1", file='images/nav/battle_end_b1.png')
i_battle_end_b2 = Image(name="i_battle_end_b2", file='images/nav/battle_end_b2.png')
i_clash_icon = Image(name="i_clash_icon", file='images/nav/clash_icon.png')
i_close_app = Image(name="i_close_app", file='images/nav/close_app.png', threshold=0.75)
# i_bluestacks = Image(name="i_bluestacks", file='images/nav/bluestacks.png', always_slow=True)
# i_bluestacks_big = Image(name="i_bluestacks_big", file='images/nav/bluestacks_big.png', always_slow=True)
# i_bluestacks_app = Image(name="i_bluestacks_app", file='images/nav/bluestacks_app.png')
# i_bluestacks_coc_icon = Image(name="i_bluestacks_coc_icon", file='images/nav/bluestacks_coc_icon.png')
# i_bluestacks_coc_icon2 = Image(name="i_bluestacks_coc_icon2", file='images/nav/bluestacks_coc_icon2.png')

# i_bluestacks_message = Image(name="i_bluestacks_message", file='images/nav/bluestacks_message.png')
# i_bluestacks_message_cross = Image(name="i_bluestacks_message_cross", file='images/nav/bluestacks_message_cross.png')
i_boat_to = Image(name="i_boat_to", file='images/nav/boat_to.png')
i_boat_back = Image(name="i_boat_back", file='images/nav/boat_back.png', threshold=0.75)
i_builder = Image(name="i_builder", file='images/nav/builder.png')
i_builder_goblin = Image(file='images/nav/builder_goblin.png')
i_change_accounts_button = Image(name="i_change_accounts_button", file='images/nav/change_accounts_button.png')
i_chat = Image(name="i_chat", file='images/nav/chat.png')
i_chat_flag = Image(file='images/donate/chat_flag.png', threshold=0.9)
i_donate_troops = Image(name="donate_troops", file="images/nav/donate_troops.png")
i_close_chat = Image(name="i_close_chat", file='images/nav/close_chat.png')
i_open_chat = Image(name="i_open_chat", file='images/nav/open_chat.png')
i_challenge = Image(name="i_challenge", file='images/nav/challenge.png')
i_close_close = Image(name="i_close_close", file='images/nav/close_close.png')
i_close_cross = Image(name="i_close_cross", file='images/nav/close_cross.png')
i_coin = Image(name="i_coin", file='images/nav/coin.png')
i_defender = Image(name="i_defender", file='images/nav/defender.png')
i_donate = Image(name="i_donate", file='images/nav/donate.png')
i_end_battle = Image(name="i_end_battle", file='images/nav/end_battle.png')
i_find_a_match = Image(name="i_find_a_match", file='images/nav/find_a_match.png')
i_find_now = Image(name="i_find_now", file='images/nav/find_now.png')
i_find_now_b = Image(name="i_find_now", file='images/nav/find_now_b.png')
# i_forge = Image(name="i_forge", file='images/nav/forge.png')
i_forge_button = Image(name="i_forge_button", file='images/nav/forge_button.png')
i_forge_path = Image(name="i_forge_path", file='images/nav/forge_path.png')
i_heart = Image(name="i_heart", file='images/nav/heart.png')
i_log_in = Image(name="i_log_in", file='images/nav/log_in.png')
# i_log_in_with_supercell = Image(name="i_log_in_with_supercell", file='images/nav/log_in_with_supercell.png')
i_main = Image(name="i_main", file='images/nav/main.png')
i_maintenance = Image(name="i_maintenance", file='images/nav/maintenance.png', threshold=0.9)
i_maintenance2 = Image(name="i_maintenance", file='images/nav/maintenance2.png')
# i_master = Image(name="i_master", file='images/master.png')
i_master_builder = Image(name="i_master_builder", file='images/nav/master_builder.png')
i_maximise = Image(name="i_maximise", file='images/nav/maximise.png')
i_multiplayer = Image(name="i_multiplayer", file='images/nav/multiplayer.png')
i_next = Image(name="i_next", file='images/nav/next.png')
# i_next2 = Image(name="i_next2", file='images/nav/next2.png')
i_okay = Image(name="i_okay", file='images/nav/okay.png')
# i_okay2 = Image(name="i_okay2", file='images/nav/okay2.png')
# i_okay3 = Image(name="i_okay3", file='images/nav/okay3.png')
# i_okay4 = Image(name="i_okay4", file='images/nav/okay4.png')
# i_okay5 = Image(name="i_okay5", file='images/nav/okay5.png')
# i_otto = Image(name="i_otto", file='images/nav/otto.png')
# i_pre_app = Image(name="i_pre_app", file='images/nav/pre_app.png')
i_pycharm = Image(name="i_pycharm", file='images/nav/pycharm.png')
i_pycharm_icon = Image(name="i_pycharm_icon", file='images/nav/pycharm_icon.png')
i_pycharm_running = Image(name="i_pycharm_running", file='images/nav/pycharm_running.png')
i_raid_weekend = Image(name="i_raid_weekend", file='images/nav/raid_weekend.png')
i_red_cross = Image(name="i_red_cross", file='images/nav/red_cross.png')
i_red_cross_2 = Image(name="i_red_cross_2", file='images/nav/red_cross.png')
i_red_cross_3 = Image(name="i_red_cross_3", file='images/nav/red_cross.png')
# i_red_cross_4 = Image(name="i_red_cross_4", file='images/nav/red_cross_4.png')
i_red_cross_5 = Image(name="i_red_cross_5", file='images/nav/red_cross_5.png')
i_red_cross_settings = Image(name="i_red_cross_settings", file='images/nav/red_cross_settings.png')
i_red_cross_attack = Image(name="i_red_cross_attack", file='images/nav/red_cross_attack.png')
i_red_cross_clan = Image(name="i_red_cross_clan", file='images/nav/red_cross_clan.png')
i_red_cross_super_troops = Image(name="i_red_cross_super_troops", file='images/super_boost/red_cross_super_troops.png')


for cross in [i_red_cross, i_red_cross_2, i_red_cross_3]:
    height = 0.5
i_reload = Image(name="i_reload", file='images/nav/reload.png')
# i_reload_2 = Image(name="i_reload", file='images/nav/reload_2.png')
i_reload_game = Image(name="i_reload_game", file='images/nav/reload_game.png')
i_return_home = Image(name="i_return_home", file='images/nav/return_home.png')
i_return_home_2 = Image(name="i_return_home_2", file='images/nav/return_home_2.png', threshold=0.7)
i_return_home_3 = Image(name="i_return_home_3", file='images/nav/return_home_3.png')
i_settings = Image(name="i_settings", file='images/nav/settings.png')
i_settings_on_main = Image(name="i_settings_on_main", file='images/nav/settings_on_main.png')
i_siege_tab = Image(name="i_siege_tab", file='images/nav/siege_tab.png')
i_siege_tab_dark = Image(name="i_siege_tab_dark", file='images/nav/siege_tab_dark.png')
i_spells_tab = Image(name="i_spells_tab", file='images/nav/spells_tab.png')
i_spells_tab_dark = Image(name="i_spells_tab_dark", file='images/nav/spells_tab_dark.png')
i_splash = Image(name="i_splash", file='images/nav/splash.png')
i_start_eyes = Image(name="i_start_eyes", file='images/nav/start_eyes.png')
i_start_eyes_2 = Image(name="i_start_eyes_2", file='images/nav/start_eyes_2.png')
i_start_eyes_3 = Image(name="i_start_eyes_3", file='images/nav/start_eyes_3.png')
i_surrender = Image(name="i_surrender", file='images/nav/surrender.png')
i_surrender_okay = Image(name="i_surrender_okay", file='images/nav/surrender_okay.png')
i_switch_account = Image(name="i_switch_account", file='images/nav/switch_account.png')
i_close_switch_account = Image(name="i_close_switch_account", file='images/nav/close_switch_account.png')
# i_bad_daz = Image(name="i_bad_daz", file='images/nav/bad_daz.png')
i_troops_tab = Image(name="i_troops_tab", file='images/nav/troops_tab.png')
i_troops_tab_dark = Image(name="i_troops_tab_dark", file='images/nav/troops_tab_dark.png')
i_try_again = Image(name="i_try_again", file='images/nav/try_again.png')
i_versus_battle = Image(name="i_versus_battle", file='images/nav/versus_battle.png')
i_war_okay = Image(name="i_war_okay", file='images/war/okay.png')
i_wins = Image(name="i_wins", file='images/nav/wins.png')
i_x = Image(name="i_unknown", file='images/nav/x.png')

i_okay_buttons = [i_okay,]

# Main screen
i_trader = Image(name="i_trader", file='images/nav/trader.png')
i_trader_close = Image(name="i_trader_close", file='images/nav/trader_close.png')
i_raid_medals = Image(name="i_raid_medals", file='images/nav/raid_medals.png', threshold=0.95)
i_raid_medals_selected = Image(name="i_raid_medals_selected", file='images/nav/raid_medals_selected.png', threshold=0.95)
i_capital_coin = Image(name="capital_coin", file='images/capital_coin.png')
# i_collect_capital_coin = Image(name="i_collect_capital_coin", file='images/collect_capital_coin.png')
i_coin_on_main_screen = Image(name="coin_on_main_screen", file='images/capital_coin/coin_on_main_screen.png')
i_coin_collect = Image(name="coin_collect", file='images/capital_coin/coin_collect.png')
i_red_cross_coin = Image(name="red_cross_coin", file='images/capital_coin/red_cross_coin.png')

# Castle
# i_treasury = Image(name="i_treasury", file='images/members/i_treasury.png')
i_clan = Image(name="i_clan", file='images/members/clan.png')
i_clan_2 = Image(name="i_clan", file='images/members/clan2.png')
i_clan_3 = Image(name="i_clan", file='images/members/clan3.png')
# i_details = Image(name="i_details", file='images/members/details.png')
# i_view_map = Image(name="i_view_map", file='images/members/view_map.png')
# i_collect_castle = Image(name="i_collect_castle", file='images/collect_castle.png')
# i_remove_castle_troops = Image(name="i_remove_castle_troops", file="images/castle/remove_castle_troops.png")
i_remove_troops = Image(name="i_remove_troops", file="images/remove_troops.png", threshold=0.79)
i_remove_troops_army = Image(name="i_remove_troops_army", file="images/remove_troops_army.png", threshold=0.79)
i_remove_troops_castle = Image(name="i_remove_troops_castle", file="images/remove_troops_castle.png", threshold=0.79)

# Games
i_caravan = Image(name="i_caravan", file='images/nav/caravan.png', threshold=0.65)
i_games = Image(name="i_games", file='images/nav/games.png')
i_red_cross_games = Image(name="i_red_cross_games", file='images/nav/red_cross_games.png')

# Research
i_research = Image(name="i_research", file='images/research/research.png')
i_research_upgrading = Image(name="i_research", file='images/research/research_upgrading.png')
i_research_elixir = Image(name="i_research_elixir", file='images/research/research_elixir.png')
i_lab_girl = Image(name="lab_girl", file="images/nav/lab_girl.png")
# i_research_dark = Image(name="i_research_dark", file='images/research/research_dark.png')

# Games
i_start_game = Image(name="i_start_game", file='images/games/start_game.png')
i_complete = Image(name="i_complete", file="images/games/complete.png", threshold=0.93)

# Attack
# i_single_player = Image(name="i_single_player", file="images/nav/single_player.png")
i_next_attack = Image(name="i_next_attack", file="images/attacks/next_attack.png")
i_3_stars = Image(name="i_3_stars", file="images/attacks/3_stars.png")
# i_3_stars_2 = Image(name="i_3_stars", file="images/attacks/3_stars_2.png")
# i_share_replay = Image(name="i_share_replay", file="images/attacks/share_replay.png")
# i_share_replay_message = Image(name="i_share_replay_message", file="images/attacks/share_replay_message.png")
# i_share_replay_send = Image(name="i_share_replay_send", file="images/attacks/share_replay_send.png")
i_two_stars = Image(name="two_stars", file="images/attack_b/two_stars.png")
i_end_battle_b = Image(name="end_battle_b", file="images/attack_b/end_battle.png")
i_surrender_b = Image(name="surrender_b", file="images/attack_b/surrender.png")
i_surrender_b_okay = Image(name="surrender_b_okay", file="images/attack_b/okay.png")
i_return_home_b = Image(name="return_home_b", file="images/attack_b/return_home.png")
i_star_bonus_okay = Image(name="surrender_b_okay", file="images/attack_b/okay_star_bonus.png")
# i_war_elixir_cart = Image(name="war_elixir_cart", file="images/attack_b/war_elixir_cart.png")
i_collect_elixir = Image(name="collect_elxir", file="images/attack_b/collect_elixir.png")
i_red_cross_elixir_cart = Image(name="red_cross_elixir_cart", file="images/attack_b/red_cross_elixir_cart.png")
# Attack_b troops
i_barb_b = Image(name="barb_b", file="images/attack_b/barb_b.png")
i_machine = Image(name="machine", file="images/attack_b/machine.png")
i_chopper = Image(name="chopper", file="images/attack_b/chopper.png")
# i_bomber = Image(name="bomber", file="images/attack_b/bomb_b.png")
# i_giant = Image(name="giant", file="images/attack_b/giant.png")
# i_cannon = Image(name="cannon", file="images/attack_b/cannon_b.png")
# i_pekka = Image(name="pekka", file="images/attack_b/pekka.png")
i_attack_screen_resources = Image(name="attack screen resources", file="images/attack_screen_resources.png")
i_king_activate = Image(name="king_activate", file="images/troops/king_activate.png")
i_queen_activate = Image(name="queen_activate", file="images/troops/queen_activate.png")
i_warden_activate = Image(name="warden_activate", file="images/troops/warden_activate.png")
i_champ_activate = Image(name="champ_activate", file="images/troops/champ_activate.png")

# War
i_war = Image(name="i_war", file='images/war/war.png', threshold=0.76)
# i_war_1 = Image(name="i_war_1", file='images/war/war_1.png')
i_clan_wars = Image(name="i_clan_wars", file='images/war/clan_wars.png')
# i_clan_wars_2 = Image(name="i_clan_wars", file='images/war/clan_wars2.png')
i_war_cwl = Image(name="i_war_cwl", file='images/nav/war_cwl.png')
# i_war_cwl_2 = Image(name="i_war_cwl", file='images/war/war_cwl_2.png')
i_season_info = Image(name="i_season_info", file='images/war/season_info.png')
# i_war_details = Image(name="i_war_details", file="images/war/war_details.png")
# i_war_my_team = Image(name="i_war_my_team", file="images/war/my_team.png")
# i_war_log = Image(name="i_war_log", file="images/war/war_log.png")
i_war_preparation = Image(name="i_war_preparation", file='images/war/preparation.png')
i_war_battle_day = Image(name="i_battle_day", file='images/war/battle_day.png')
# i_war_battle_day_2 = Image(name="i_battle_day_2", file='images/war/battle_day_2.png')
i_war_left = Image(name="i_war_left", file='images/war/left.png', threshold=0.7, region_limit=[415, 700, 500, 240])
i_war_right = Image(name="i_war_right", file='images/war/right.png')
i_war_right_2 = Image(name="i_war_right_2", file='images/war/right_2.png')
i_war_donate = Image(name="i_war_donate", file='images/war/donate.png')
i_war_request = Image(name="i_war_request", file='images/war/war_request.png')
i_war_donate_reinforcements = Image(name="i_war_donate_reinforcements", file='images/war/donate_reinforcements.png', threshold=0.7)
# i_clan_army = Image(name="i_clan_army", file="images/troops/clan_army.png")
i_cwl_prep = Image(name="i_cwl_prep", file="images/war/cwl_prep.png", threshold=0.7)
# i_cwl_prep_2 = Image(name="i_cwl_prep_2", file="images/war/cwl_prep_2.png")
# i_cwl_last_day = Image(name="i_cwl_last_day", file="images/war/cwl_last_day.png")
i_attacks_available = Image(name="i_attacks_available", file="images/war/attacks_available.png")

# Donate images
# i_more_donates = Image(name="i_more_donates", file="images/more_donates.png")
i_donate_cross = Image(name="i_donate_cross", file='images/donate_cross.png')

# Challenge
i_challenge_start = Image(name="challenge_start", file="images/challenge/challenge_start.png")

# Building images
i_builder_zero = Image(name="i_builder_zero", file='images/builder_zero.png', threshold=0.75, region_limit=[744, 79, 198, 32])
i_builder_one = Image(name="i_builder_one", file='images/builder_one.png', threshold=0.75)
i_upgrade_button = Image(name="i_upgrade_button", file='images/upgrade.png', threshold=0.7)
i_upgrade_2_button = Image(name="i_upgrade_button", file='images/upgrade_2.png', threshold=0.7)
i_confirm = Image(file='images/upgrade/confirm.png')
i_upgrade_hero_button = Image(name="i_upgrade_hero_button", file='images/upgrade_hero.png', threshold=0.7)
i_build_confirm = Image(name="build_confirm", file="images/builder/build_confirm.png")
i_build_confirm_2 = Image(name="build_confirm", file="images/builder/build_confirm_2.png")
i_suggested_upgrades = Image(name="i_suggested_upgrades", file='images/towers/suggested_upgrades.png')
i_upgrades_in_progress = Image(name="i_upgrades_in_progress", file='images/towers/upgrades_in_progress.png')

# Builder base attacks
# i_attack_b_0 = Image(name="i_attack_b_0", file='images/attack_b/attack_0.png', threshold=0.85)

# Army tab
i_army_clock = Image(name="i_army_clock", file='images/army_clock.png')
i_army_edit = Image(name="i_army_edit", file='images/nav/army_edit.png')
i_army_okay = Image(name="i_army_okay", file='images/nav/army_okay.png')
i_army_okay2 = Image(name="i_army_okay2", file='images/nav/army_okay2.png')
i_army_request = Image(name="i_army_request", file='images/nav/army_request.png')
i_army_donate_edit = Image(name="i_army_donate_edit", file='images/nav/army_donate_edit.png')
# i_army_donate_confirm = Image(name="i_army_donate_confirm", file='images/nav/army_donate_confirm.png')
# i_army_request_send = Image(name="i_army_request_send", file='images/nav/army_request_send.png')
i_castle_remove = Image(name="i_castle_remove", file='images/castle/castle_remove.png')
i_castle_confirm = Image(name="i_castle_confirm", file='images/castle/castle_confirm.png')
i_castle_send = Image(name="i_castle_send", file='images/castle/castle_send.png')
i_army_tab_cancel = Image(name="army_tab_cancel", file="images/nav/army_tab_cancel.png")

# Members
i_perks = Image(name="i_perks", file="images/members/perks.png")
i_my_clan = Image(name="i_my_clan", file="images/nav/my_clan.png")
i_war_league_on = Image(name="i_war_league_on", file="images/nav/war_league_on.png")
i_war_classic_on = Image(name="i_war_classic_on", file="images/nav/war_classic_on.png")
i_war_classic_off = Image(name="i_war_classic_off", file="images/nav/war_classic_off.png")
i_war_league_on = Image(name="i_war_league_on", file="images/nav/war_league_on.png")
i_warlog = Image(name="warlog", file="images/nav/warlog.png")
i_war_details = Image(file="images/nav/war_details.png")
i_war_details_map = Image(file="images/nav/war_details_map.png")
i_view_map = Image(file="images/nav/view_map.png")
i_war_results = Image("images/nav/war_results.png")
i_war_stats_on = Image("images/nav/war_stats_on.png")
i_war_team_on = Image("images/nav/war_team_on.png")
i_war_team_off = Image("images/nav/war_team_off.png")

i_war_star = Image("images/members/war_star.png")

i_find_new_members = Image(name="i_find_new_members", file="images/people/find_new_members.png")
i_profile_star = Image(name="i_profile_star", file="images/nav/profile_star.png")
i_my_clan_tab = Image(name="my_clan_tab", file="images/nav/my_clan_tab.png")
i_request_reinforcements = Image(name="request_reinforcements", file="images/nav/request_reinforcements.png")
i_highest_level = Image(name="highest_level", file="images/nav/highest_level.png")

# Super boost
i_boost = Image(name="i_boost", file='images/super_boost/boost.png', threshold=0.7)
i_boost_on = Image(name="i_boost_on", file='images/super_boost/boost_on.png', threshold=0.7)
i_boost_on_2 = Image(name="i_boost_on", file='images/super_boost/boost_on.png', threshold=0.7)

i_super_barb = Image(name="i_super_barb", file='images/super_boost/super_barb.png')
i_super_minion = Image(name="i_super_minion", file='images/super_boost/super_minion.png')
i_potion = Image(name="i_potion", file='images/super_boost/potion.png')
i_dark = Image(name="i_dark", file='images/super_boost/dark.png')
i_dark_2 = Image(name="i_dark_2", file='images/super_boost/dark_2.png')
i_potion_small = Image(name="i_potion_small", file='images/super_boost/potion_small.png')

i_activate = Image(name="activate", file="images/super_boost/activate.png")
i_000 = Image(name="000", file="images/super_boost/000.png")
i_000v2 = Image(name="000", file="images/super_boost/000v2.png")
i_00 = Image(name="000", file="images/super_boost/00.png")
i_00v2 = Image(name="000", file="images/super_boost/00v2.png")

# Messages
# i_new_message = Image(name="new_message", file="images/message/new_message.png")
# i_send_message = Image(name="send_message", file="images/message/send_message.png")

def create_image_group(directory, show=False, threshold=0.79, add_levels=False):
    files = dir_to_list(directory)
    image_group = []
    for file in files:
        level = None
        if add_levels:
            start = len(directory) + 1
            level = int(file[start:start+2])
        new = Image(name=file, file="images/" + file + ".png", threshold=threshold, level=level)
        image_group.append(new)
    if show:
        for x in image_group:
            x.show()
    return image_group

i_tree_remove = Image(name="remove_tree", file="images/trees/remove_tree.png")

# Image groups
resource_images_main = create_image_group("resources/main")
resource_images_builder = create_image_group("resources/builder")
i_clock_1 = Image(file="images/resources/clock/clock_1.png")
i_clock_2 = Image(file="images/resources/clock/clock_2.png")
i_clock_3 = Image(file="images/resources/clock/clock_3.png")
carts = create_image_group('attack_b/carts', threshold=0.7)
castles = create_image_group("towers/castles/")
trees_main = create_image_group("trees/main", threshold=0.80)
trees_builder = create_image_group("trees/builder")
available_builders = create_image_group("builder/available_builders", threshold=0.88)


town_halls = create_image_group("towers/town_halls/", add_levels=True)
eagles = create_image_group("towers/eagles/")
monoliths = create_image_group("towers/monoliths/")
air_defences = create_image_group("towers/air_defence/")
single_infernoes = create_image_group("towers/inferno_single/")
multi_infernoes = create_image_group("towers/inferno_multi/")
cross_bowes = create_image_group("towers/cross_bowes")
scattershots = create_image_group("towers/scattershots")
queen_towers = create_image_group("towers/queen_towers")

town_halls_b = create_image_group("attack_b/th_b", add_levels=False)

def get_image(name):
    return next((x for x in images if x.name == name), None)


i_app_player_1 = get_image("app_player_1")
i_barb = get_image("barb")
i_blank_screen = get_image("blank_screen")
i_close = get_image("close")
# i_close_app = get_image("close_app")
# i_maximise = get_image("maximise")
i_minimise = get_image("minimise")
i_run_as_admin = get_image("run_as_admin")
i_yes = get_image("yes")

dir = "war/castles/"
files = dir_to_list(dir)
war_castles = []
for file in files:
    new = Image(name=file, file='images/' + file + ".png", threshold=0.69, no_of_regions=1)
    war_castles.append(new)

# Building
i_wall_text = Image(name="i_wall_text", file="images/towers/wall.png")

# i_watch = Image(name="watch", file="images/attack_b/watch.png")

# img_message = cv2.imread('images/message.png', 0)

# Upgrades
# i_hero_upgrade_identifier = Image(name="hero_upgrade_identifier", file="images/upgrades/hero_upgrade_identifier.png")

# People
# i_mail = Image(name="mail", file="images/people/mail.png")
# i_message = Image(name="message", file="images/people/message.png")
# i_profile = Image(name="profile", file="images/people/profile.png")
# i_attack_log = Image(name="attack_log", file="images/people/attack_log.png")
# i_add_friend = Image(name="add_friend", file="images/people/add_friend.png")
i_invite = Image(name="invite", file="images/people/invite.png")
i_clan_back = Image(name="clan_back", file="images/people/clan_back.png")
files = dir_to_list("people/castles/")
member_castles = []
for file in files: member_castles.append(Image(name=file, file='images/' + file + ".png", threshold=0.65))

# GUI
# i_gui_icon = Image(name="gui_icon", file="images/gui/gui_icon.png")
# i_tkinter = Image(name="tkinter", file="images/gui/tkinter.png")

def multi_click(images):
    for image in images:
        time.sleep(0.3)
        clicked, count = False, 0
        while not clicked and count < 20:
            clicked = image.click()
            count += 1
            time.sleep(0.1)
        if count == 20:
            print("Multi click failure:", image)

def merge_regions():
    for image in images:
        count = 0
        merge_success = True
        while merge_success and count < 3:
            merge_success = image.merge_regions()
            count +=1
    return count

def app():
    i_app.click()

def shrink_images(directory):
    files = os.listdir(directory)
    for file in files:
        filename = f"{directory}/{file}"
        if os.path.isfile(filename):
            scale = 0.92
            image1 = cv2.imread(filename, 0)
            image2 = cv2.resize(image1, (0,0), fx=scale, fy=scale)
        else:
            shrink_images(filename)

for i in images:
    i.merge_regions()



# for i in war_castles:
#     print(i, i.no_of_regions, len(i.regions))


# shrink_images("images")



