from images import *
from collections import namedtuple

TowerType = namedtuple("TowerTypes", ("name", "objects", "number"))
TowerLoc = namedtuple("TowerLoc", ("name", "rect"))
TroopInfo = namedtuple("TroopInfo", ("name", "likes", "dislikes"))

tower_types = [
    TowerType("Town Hall", town_halls, 1),
    TowerType("Eagle", eagles, 1),
    TowerType("Monolith", monoliths, 1),
    TowerType("Inferno Single", single_infernoes, 3),
    TowerType("Inferno Multi", multi_infernoes, 3),
    TowerType("Air Defence", air_defences, 4),
    TowerType("Cross Bow", cross_bowes, 4),
    TowerType("Scattershot", scattershots, 2),
    TowerType("Queen Tower", queen_towers, 1),
]

queen = TroopInfo("Queen", ["Town Hall", "Eagle", "Air Defence", "Scattershot", "Monolith"], ["Inferno Single"])
balloons = TroopInfo("Balloons", ["Town Hall", "Eagle"], ["Air Defence", "Queen Tower", "Scattershot"])

troops_info = [
    queen,
    balloons,
]

# for troop_info in troops_info:
#     print(troop_info.name)
#     print(troop_info.likes)

file = f'analyse/war_screen'

def hold_key(key, dur):
    # print("Pressing:", key)
    pag.keyDown(key)
    time.sleep(dur)
    pag.keyUp(key)

def snapshot():
    app()
    pag.keyDown('ctrl')
    for x in range(4): hold_key('o', 0.2)
    pag.keyUp('ctrl')

    for x in range(1, 31):
        pag.screenshot(file+str(x)+".png")
        if i_war_right_2.find():
            i_war_right_2.click()
            time.sleep(2)
        else:
            print("Where's the button?", i_war_right_2.find_detail())
    app()
    # show_snapshot()

def show_snapshot():
    screen = cv2.imread(file, 1)
    screen = screen[50:880, 350:1600]
    show(screen, dur=0)

def find_many(screen, items, number):
    found_items = []
    for item in items:
        result = cv2.matchTemplate(screen, item.image, method)
        yloc, xloc = np.where(result >= 0.70)
        found_items_loop = zip(xloc, yloc, result[yloc, xloc])
        found_items += found_items_loop
    found_items = sorted(found_items, key=lambda x: x[2], reverse=True)
    # print("All found items:", found_items)
    selected_items = []
    height, width = 50, 50
    for x, y, result in found_items:
        if len(selected_items) == number: continue
        already_selected = False
        for x0, y0, w, h in selected_items:
            center_x = x + width // 2
            center_y = y + height // 2
            if x0 < center_x < x0 + w and y0 < center_y < y0 + h:
                already_selected = True
        if not already_selected:
            rect = (x, y, width, height)
            selected_items.append(rect)
    # print(selected_items)
    return selected_items

def identify_towers():
    screen = cv2.imread(file, 0)[50:880, 350:1600]
    tower_locs = []
    for tower_type in tower_types:
        rects = find_many(screen, tower_type.objects, tower_type.number)
        for rect in rects:
            tower_locs.append(TowerLoc(tower_type.name, rect))

    return tower_locs


def show_towers(troop, tower_locs):
    screen = cv2.imread(file, 1)[50:880, 350:1600]

    for name, rect in tower_locs:
        if troop and name in troop.likes:
            print(name, rect, "Green")
            cv2.rectangle(screen, rect, (0, 255, 0), 2)
        elif troop and name in troop.dislikes:
            print(name, rect, "Red")
            cv2.rectangle(screen, rect, (0, 0, 0), 6)
            cv2.rectangle(screen, rect, (0, 0, 255), 4)
        else:
            print(name, rect, "White")
            cv2.rectangle(screen, rect, (255, 255, 255), 2)
    if troop:
        show(screen, dur=0, label=troop.name)
    else:
        show(screen, dur=0)

snapshot()
# show_towers(troop=None)
# tower_locs = identify_towers()
# show_towers(queen, tower_locs)
# show_towers(balloons, tower_locs)
# show_snapshot()
# identify_towers()
# find_many(number=4)


