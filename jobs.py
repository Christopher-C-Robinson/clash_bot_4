from datetime import timedelta
from attacks_logic import *
from war import *
from research import *
from build import *
from coin import *

jobs = []


class Job:
    def __init__(self, data):
        self.name = data['name']
        self.time_active = data['time_active']
        self.time_inactive = data['time_inactive']
        self.update_time = data['update_time']
        jobs.append(self)

    def __str__(self):
        return "Job: " + self.name

    def run(self, account, village=None):
        db_update(account, self.name, datetime.now() + timedelta(minutes=5))
        if self not in active_jobs:
            print("Job not active:", self)
            db_update(account, self.name, datetime.now() + timedelta(hours=24))
            return
        print("Running:", self.name)
        if account != admin:
            change_accounts_fast(account)
        if self.name == "donate":
            donate(account)
            if account.mode == "donate" and admin.mode == "preparation" and admin.war_donations_remaining > 0 and account in war_participants:
                war_donations()
                queue_up_troops(account)
            if account.mode == "donate" and admin.mode == "cwl" and admin.war_donations_remaining > 0 and account in war_participants:
                war_donations(cwl=True)
                queue_up_troops(account)

        if self.name == "coin": coin()
        if self.name == "war_troops": train_war_troops(account)
        if self.name == "cwl_troops": train_war_troops(account)
        if self.name == "donate_war": donate_war(account)
        if self.name == "attack": attack(account, account.army_troops)
        if self == j_attack_b and account.attacking_b: attack_b_multi(account)
        if self.name == "challenge": challenge()
        if self.name == "research": research(account)
        if self.name == "build": build(account, "main")
        if self.name == "message": message()
        if self == j_completion_date: remaining_time_for_th(account)
        if self == j_sweep: sweep()
        if self == j_lose_trophies: lose_trophies(account)
        if account != admin:
            update_images(account)
            account.update_resources()
            if admin.inviting:
                invite()
            get_capital_coin()
        if not self.update_time: # Not updating time because time is updated by the function run immediately above
            print("Not updating time:", self.name)
            return
        if self.name == "attack":
            if not self.is_active(account):
                duration = self.time_inactive
                db_update(account, self.name, datetime.now() + duration)
            return

        duration = self.get_duration(account)
        # print("Run duration:", account, self.name, self.is_active(account), duration)
        db_update(account, self.name, datetime.now() + duration)

    def get_duration(self, account):
        if self.name == "coin": return get_time_coin()
        if self.name == "challenge": return timedelta(hours=5 * (5 - account.number))
        if self.is_active(account): return self.time_active
        return self.time_inactive

    def is_active(self, account):
        if self.name in ["donate", ] and account.mode in ["donate", ]: return True
        if self.name in ["donate_war", ]:
            if admin.mode in ["", "no war", "battle_day"]: return False
            if admin.mode == "no war": return False
            if admin.war_donations_remaining == 0: return False
            return True
        if self.name in ["attack", ] and account.mode in ["attack"]: return True
        if self == j_attack_b and account.attacking_b: return True
        if self == j_lose_trophies and account.current_trophies > account.max_trophies: return True
        if self == j_lose_trophies:
            print("Lose trophies turned off", account, account.current_trophies, account.max_trophies)
        return False

    def get_time(self, account):
        result = db_read(account, job.name)
        if result is None: result = datetime.now()
        # print("Raw result:", result)
        # result = string_to_time(result)
        # print(self, result)
        return result

    def reset_time(self, account):
        result = self.get_time(account) - datetime.now()
        if self in active_jobs and result > timedelta(hours=6):
            db_update(account, self.name, datetime.now() + timedelta(minutes = 15))
            print("Reset time for:", account, self)
        elif self in active_jobs and result < timedelta(hours=6):
            print("Did not reset time (less than 6 hours) for:", account, self)
        elif self not in active_jobs:
            print("Did not reset time (not active) for:", account, self)
        else:
            print("Did not reset time (not sure why) for:", account, self)

def reset_times():
    for job in jobs:
        if job == j_build: continue
        for account in accounts:
            job.reset_time(account)

def get_job(job):
    return next((x for x in jobs if x.name == job), None)

def sweep():
    change_accounts_fast(bad_daz)
    current_mode = admin.mode
    set_admin_mode()
    if current_mode != admin.mode:
        for account in accounts:
            account.set_mode(attacks_left_update=True)
        if admin.mode == "battle_day" and admin.has_prepped_for_war == False:
            admin.has_prepped_for_war = True
        if admin.mode == "preparation":
            admin.has_prepped_for_war = False
    if is_image_old("status", 30):
        update_image()

def challenge():
    goto(chat)
    i_challenge.click()
    time.sleep(1)
    i_challenge_start.click()
    time.sleep(1)



attack_data = {'name': "attack", 'time_active': timedelta(minutes=2), 'time_inactive': timedelta(hours=2), 'update_time': True}
attack_b_data = {'name': "attack_b", 'time_active': timedelta(hours=3), 'time_inactive': timedelta(days=1), 'update_time': True}
donate_data = {'name': "donate", 'time_active': timedelta(minutes=10), 'time_inactive': timedelta(minutes=30), 'update_time': True}
donate_war_data = {'name': "donate_war",'time_active': timedelta(minutes=10),'time_inactive': timedelta(hours=2),'update_time': True}
research_data = {'name': "research",'time_active': None,'time_inactive': None,'update_time': False}
build_data = {'name': "build",'time_active': None,'time_inactive': None,'update_time': False}
challenge_data = {'name': "challenge",'time_active': None,'time_inactive': None,'update_time': True}
coin_data = {'name': "coin","time_active": None,"time_inactive": None,'update_time': True}
message_data = {'name': "message","time_active": timedelta(hours=8),"time_inactive": timedelta(hours=8),'update_time': True}
completion_date_data = {'name': "completion_date","time_active": timedelta(hours=24),"time_inactive": timedelta(hours=24),'update_time': True}

j_attack = Job(data=attack_data)
j_attack_b = Job(data=attack_b_data)
j_donate = Job(data=donate_data)
# j_donate_war = Job(data=donate_war_data)
j_research = Job(data=research_data)
j_build = Job(data=build_data)
j_challenge = Job(data=challenge_data)
j_coin = Job(data=coin_data)
j_war_troops = Job({'name': "war_troops",'time_active': timedelta(minutes=10),'time_inactive': timedelta(hours=12),'update_time': True})
j_cwl_troops = Job({'name': "cwl_troops",'time_active': timedelta(minutes=10),'time_inactive': timedelta(hours=12),'update_time': True})
j_message = Job(data=message_data)
j_completion_date = Job(data=completion_date_data)
j_sweep = Job({'name': "sweep","time_active": timedelta(hours=0.5),"time_inactive": timedelta(hours=0.5),'update_time': True})
j_lose_trophies = Job({'name': "lose_trophies", "time_active": timedelta(minutes=5), "time_inactive": timedelta(hours=2), 'update_time': True})

# active_jobs = [j_build, j_donate, j_attack, j_coin, j_challenge, j_war_troops, j_donate_war, j_message]
# active_jobs = [j_attack, j_donate, j_attack_b]
active_jobs = [j_attack, j_donate, j_completion_date, j_attack_b, j_war_troops, j_cwl_troops, j_lose_trophies, j_challenge]
active_jobs.append(j_sweep)

text = "Not running: "
for job in jobs:
    if job not in active_jobs:
        text += str(job.name) + ", "
print(text[0:-2])

def print_info():
    for account in accounts:
        account.set_mode(resource_update=False)
        account.print_info()
    print()
    print("Mode:", admin.mode, admin.war_donations_remaining)
    db_view(no=5)
    # db_view_builds(no=5)


# admin.mode = "cwl"
# j_donate_war.run(account_1)
# print_info()

# print(get_job("donate_x"))