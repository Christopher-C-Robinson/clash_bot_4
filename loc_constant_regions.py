from nav import *

links = [
    (troops_tab, (TRAIN_RANGE, TRAINING_RANGE, TRAINING_RANGE_FIRST_TROOP)),
    (army_tab, (ARMY_EXISTING, ARMY_EXISTING_NOT_SIEGE, ARMY_EXIST_FIRST_TROOP, CASTLE_TROOPS, SIEGE_EXISTING, CASTLE_TROOPS)),
    (l_donation_request_selector, (CASTLE_REQUEST_AREA_1, CASTLE_REQUEST_AREA_2)),
    (l_donate, (DONATE_AREA, )),
    (chat, (CHAT_AREA, )),
    (l_clan, (MEMBER_NUMBERS, )),

]


for loc, regions in links:
    for region in regions:
        loc.add_constant_region(region)

if __name__ == "__main__":
    l_clan.show_constant_regions()
    goto(pycharm)
