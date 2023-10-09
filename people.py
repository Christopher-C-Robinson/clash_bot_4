from nav import *
from admin import *

def invite_latest_attackee():
    if not admin.inviting: return
    goto(main)
    i_mail.click()
    time.sleep(0.2)
    i_attack_log.click()
    rects = i_message.find_many(show_image=False)
    rects = sorted(rects, key=lambda x: x[1])
    if len(rects) > 0:
        click_rect(rects[0])
        time.sleep(0.3)
        multi_click([i_profile, i_invite])
    time.sleep(0.7)
    i_red_cross.click()

def invite():
    # return
    invited = []
    not_invited = []
    goto(l_clan)
    if not i_find_new_members.wait(dur=2):
        print("Didn't get into the clan")
        return invited, not_invited
    time.sleep(1)
    members = get_member_numbers()
    print("No of members:", members)
    if members >= 50:
        i_red_cross_clan.click()
        pag.click(BOTTOM_LEFT)
        admin.inviting = False
        return
    i_find_new_members.click()
    time.sleep(0.5)
    for castle in member_castles:
        rects = castle.find_many()
        # print(castle, len(rects))
        for rect in rects:
            click_rect(rect)
            time.sleep(0.5)
            member_stars = stars.read(STARS)
            try:
                member_stars = int(member_stars)
                print("Member stars:", member_stars)
                if member_stars > 150:
                    # print("Heaps of Stars")
                    multi_click([i_invite, i_clan_back])
                    # i_clan_back.click()
                    invited.append(member_stars)
                else:
                    # print("Not enough stars")
                    i_clan_back.click()
                    not_invited.append(member_stars)
            except:
                i_clan_back.click()
        time.sleep(1)
    i_red_cross_clan.click()
    pag.click(BOTTOM_LEFT)
    goto(main)
    return invited, not_invited

def get_member_numbers():
    screen = get_screenshot(MEMBER_NUMBERS)
    result = members.read_screen(screen, show_image=False, return_number=False)
    results = result.split("x")
    try:
        result = int(results[0])
    except:
        result = 0
    if result == 50:print("Full")
    return result

def app():
    i_app.click()

def invite_many(count):
    invited = []
    not_invited = []
    for x in range(count):
        print("loop:", x)
        invited_1, not_invited_1 = invite()
        invited.append(invited_1)
        not_invited.append(not_invited_1)
        # app()
        time.sleep(1)
        # app()
    print("Invited:", invited)
    print("Not invited:", not_invited)

# invite()



# invite_latest_attackee()

