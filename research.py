from time import sleep
from account import *

def research_slide(direction):
    global current_position
    if direction == "right":
        pag.moveTo(1500, 630, 0.3)
        pag.dragTo(620, 630, 0.5, button="left")
        time.sleep(0.3)
    else:
        pag.moveTo(620, 630, 0.3)
        pag.dragTo(1500, 630, 0.5, button="left")
        time.sleep(0.3)

def research(account):
    change_accounts_fast(account)
    goto(main)
    if account.th <= 10:
        research_preference = [giant, wizard, bomber, lightening, dragon, barb, minion, hog, archer, goblin, bloon, heal, rage]
    if account.th <=5:
        research_preference = [barb, archer, giant, wizard, bomber, ]
    else:
        research_preference = [barb, minion, dragon, lightening, log_thrower, freeze, golem, witch, clone, skeleton, lava_hound]
    goto(l_lab)
    if i_research_upgrading.find():
        print("Still researching")
        goto(main)
        pag.click(BOTTOM_LEFT)
        account.update_lab_time()
        return
    if not i_lab_girl.find():
        return
    for troop in research_preference:
        found = False
        for slide_direction in ["right", "right", "right", "left", "left", "left"]:
            if found: continue
            val, loc, rect = troop.i_research.find_detail()
            print("Research", troop, "Found", val)
            if troop.i_research.find():
                colour = troop.i_research.colour()
                print("Research", troop, "Found", troop.i_research.colour())
                if colour > 400:
                    troop.i_research.click()
                    sleep(0.1)
                    if i_research_elixir.find():
                        i_research_elixir.click()
                    print("Available")
                    # pag.press("esc")
                    pag.click(BOTTOM_LEFT)
                    return
                else:
                    found = True
            else:
                research_slide(slide_direction)
    account.update_lab_time()

    goto(main)
    pag.click(BOTTOM_LEFT)
