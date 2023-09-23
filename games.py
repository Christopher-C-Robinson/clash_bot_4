# from nav import *
# from account import *
from attacks_logic import *
from images import *
from utilities import *
from sql_games import *

games = []


class Game():
    def __init__(self, name, preference, min_th=0, extra_troops=[]):
        self.name = name
        images_string = dir_to_list(f'games/{name}')
        self.images = []
        for image_string in images_string:
            image = Image(name=image_string, file=f'images/{image_string}.png', threshold=0.8)
            self.images.append(image)

        self.action = name
        self.preference = preference
        self.min_th = min_th
        self.extra_troops = extra_troops
        games.append(self)

    def __str__(self):
        return self.name

    def is_available(self):
        goto(l_games)
        result = False
        for image in self.images:
            if image.find(): result = True
        # print(self, result)
        return result

    def start(self, account):
        goto(l_games)
        result = False
        for image in self.images:
            if not result:
                if image.find():
                    result = True
                    image.click()
                    i_start_game.click()
                    account.current_game = self.name

        if not result:
            pag.moveTo(1600, 260)
            pag.dragTo(1600, 670, .2)
            for image in self.images:
                if not result:
                    if image.find():
                        result = True
                        image.click()
                        i_start_game.click()
                        account.current_game = self.name

        i_red_cross_games.click()

        return result

    def run(self, account):
        if self.action == "builder":
            print("Game run: Attack_b")
            attack_b_multi(account, count=3)
        elif self.action == "main":
            print("Game run: Attack", account.games_troops)
            troops_to_use = account.games_troops
            troops_to_use["initial_troops"] = troops_to_use["initial_troops"] + self.extra_troops
            attack(account, troops_to_use, siege_required=False, attack_regardless=True)
        else:
            print("Run: action not coded", self, self.action)

        if not game_active():
            account.current_game = None
            db_games_update(account.number, "")


def game_active():
    # Counter({(128, 128, 0): 1250}) - active game
    goto(l_games)
    time.sleep(0.4)
    region = (749, 374, 50, 20)
    pag.screenshot('temp/games_colour.png', region=region)
    image = cv2.imread('temp/games_colour.png', 1)
    # show(image)
    new, counter = simplify(image, gradients=2)
    print("Colour count:", counter)
    result = counter[(0, 128, 128)] > 800
    print("Game active:", result)
    return result

def choose_game(account):
    goto(l_games)
    if i_complete.find():
        # print(i_complete.find_detail())
        print("Choose game - complete")
        account.playing_games = False
        return False
    if game_active():
        print("Choose game - game already in progress")
        return False
    available_games = []
    for game in games:
        if game.is_available() and account.th >= game.min_th:
            available_games.append(game)
    pag.moveTo(1600, 670)
    pag.dragTo(1600, 260, .2)
    for game in games:
        if game.is_available() and account.th >= game.min_th:
            available_games.append(game)

    available_games.sort(key=lambda x: x.preference, reverse=False)
    print("Choose game:", objects_to_str(available_games))
    if len(available_games) > 0:
        result = available_games[0]
        account.current_game = result.name
        db_account_update(account.number, "game", account.current_game)
        result.start(account)
        return available_games[0]
    return False


# def run_game(account):
#     # change_accounts(account.number, "main")
#     if account.current_game is None:
#         choose_game(account)
#     if account.current_game is None:
#         return
#     account.current_game.run()

def create_combined_games_image(accounts):
    account_images = []
    for account in accounts:
        account_images.append(cv2.imread(f'temp/tracker/games_{account.number}.png', 1))

    header = np.zeros((50, 190, 3), np.uint8)
    x = datetime.now().strftime("%I:%M") + datetime.now().strftime("%p").lower()
    cv2.putText(header, x, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    images = [header] + account_images
    result = combine_image_vertical(images)
    show(result)
    cv2.imwrite("C:/Users/darre/OneDrive/Darren/clash_bot/tracker/games.png", result)

def get_current_game(account):
    goto(l_games)
    screen = get_screenshot(CURRENT_GAME)
    # get_screenshot(GAMES_SCORE, filename=f"tracker/games_{account.number}")
    max_result = 0
    current_game = None
    account.current_game = None
    for game in games:
        for image in game.images:
            result, val = image.find_screen(screen, return_result=True, show_image=False)
            # print(game, image, result, val)
            if val > 0.58 and val > max_result:
                max_result = result
                current_game = game
    if current_game:
        account.current_game = current_game.name
    db_account_update(account.number, "game", account.current_game)

    return current_game

g_builder = Game("builder", 1)

def return_game(name):
    return next((x for x in games if x.name == name), None)

def run_games(count):
    for _ in range(count):
        for account in accounts:
            if not account.playing_games:
                print("Run games. Not playing:", account)
                continue
            change_accounts_fast(account)
            game = return_game(account.current_game)
            if not game:
                game = get_current_game(account)
            if not game:
                game = choose_game(account)
            if game:
                game.run(account)
        # create_combined_games_image(accounts)


# print(micah.current_game)

# goto(pycharm)