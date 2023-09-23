from nav import *

# ============
# === COIN ===
# ============

def coin():
    goto(main)
    hold_key('s', 0.5)
    hold_key('a', 0.5)
    time.sleep(1)
    val, loc, rect = i_capital_coin.find_detail()
    print("Coin available:", val)
    if val > 0.7:
        goto(forge)
        return i_collect_capital_coin.click()
    return False

def get_time_coin():
    print("Get time to next coin")
    goto(forge)
    time.sleep(0.2)
    result = coin_time.read(CAPITAL_COIN_TIME, show_image=False)
    print("A", type(result))
    print("Get time coin", result)
    try:
        result = text_to_time_2(result, return_duration=True) + timedelta(minutes=2)
        print("B", type(result))
    except:
        result = timedelta(hours=2)
        print("C", type(result))
    print("Coin time:", result)
    print("D", type(result))
    return result
