# from nav import *
from troops import *
from people import *

# ========================
# === 7. LOSE TROPHIES ===
# ========================

def place(troop):
    if troop.i_attack.find():
        troop.i_attack.click()
        time.sleep(0.2)
        pag.click(STANDARD_DP2)
        return True
    return False

def calc_trophies():
    goto(main)
    time.sleep(1)
    result = trophies.read(TROPHIES, return_number=True, show_image=False)
    return result

def lose_trophies(account):
    global current_location
    account.current_trophies = calc_trophies()
    print("Lose trophies", account.number, account.max_trophies, account.current_trophies)
    if account.current_trophies > account.max_trophies:
        goto(find_a_match)

        hold_key("a", 0.5)
        for _ in range(2): pag.scroll(300)
        # zoom_out()
        dp = STANDARD_DP2
        for troop in [king, queen, warden, champ, barb, giant, bomber, super_barb, dragon]:
            val, loc, rect = find(troop.i_attack.image, get_screenshot(TROOP_ZONE))
            print("Lose trophies:", troop.name, val)
            if val > 0.65:
                if place(troop):
                    print("Unleashed", troop)
                    break

        time.sleep(0.2)
        i_surrender.click()
        time.sleep(0.2)
        i_surrender_okay.click()
        i_return_home.wait(80)
        i_return_home.click()
        current_location = "return_home"
        goto(main)

        # if troop in [barb, giant, bomb, ]:
        #     troop_delete_backlog()
        #     restock([troop], account, extra=False)
        #     attack(account, account.army_troops)

        return True
    return False
