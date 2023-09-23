from nav import *

war_directory = "images/members/war/"
member_files = os.listdir(war_directory)
members = []

CHAT_NAME = (158, 132, 160, 770)

class Member():
    def __init__(self, name):
        self.name = name
        self.i_war = Image("member_war", war_directory + name + ".png", threshold=0.9)
        members.append(self)

    def __str__(self):
        return self.name

    def promote(self, position):
        goto(l_clan)
        found, count = False, 0
        while not found and count < 5:
            count += 1
            move_war_screen("up", 400)
            if self.i_war.find(fast=False):
                self.i_war.click()
                found = True
                if i_promote_coleader.find() and position == "coleader":
                    i_promote_coleader.click()
                    return
                if i_promote_elder.find():
                    i_promote_elder.click()
                    if position == "coleader":
                        self.promote()




for file in member_files:
    name = file[0:-4]
    Member(name)

m_rigg = next((x for x in members if x.name == 'rigg_kyo'), None)


def save_war_results():
    success = False
    results = []
    for x in range(5):
        get_to_war_results_screen()
        time.sleep(.5)
        print(i_war_log.find_detail()[0])
        if i_war_log.find():
            success = True
            break
    if not success:
        print("Couldn't find war log")
        return
    move_war_screen("up", 450)
    finished, count = False, 0
    while not finished and count < 20:
        print("Start of loop")
        print(count)
        region = (554, 312, 1200, 114)
        row = get_screenshot(region)
        # show(row)
        member = member_in_row(row)
        if member:
            print("Found")
            result = scores.read_screen(row)
            results.append((member.name, result))
            print(member.name, result)
            move_war_screen("up", 114)
            count += 1
        else:
            print("Not found")
            move_war_screen("up", 30)
            count += 1
        print("Finished, count", finished, count)

    print(results)

def member_in_row(row):
    best, found_member = 0, None
    for member in members:
        bool, result, loc = member.i_war.find_screen(row, show_image=False, return_result=True, return_location=True)
        print("Result:", member.name, bool, result, loc)
        if bool and loc[1] < 40:
            if result > best:
                best = result
                found_member = member
            print("Found:", member.name, result, loc)
    return found_member

def get_to_war_results_screen():
    goto(l_castle)
    result = False
    for image in [i_clan, i_war_log, i_details, i_view_map, i_war_details, i_war_my_team,]:
        if image.click():
            result = True
            time.sleep(0.5)
    return result

def move_war_screen(dir, distance):
    time = 0.1
    if distance > 200:
        time = distance * 2 / 450
    time = distance * 2 / 450

    if dir == "up":
        pag.moveTo(1726, 900, 0.3)
        pag.dragTo(1726, 900 - distance, time, button="left")

