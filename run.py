from bot import *
from games import *

def run(pause_hour=None):
    set_current_account()
    while True:
        run_job(db_next_job())
        if pause_hour and in_time_zone(pause_hour, pause_hour + 3):
            if admin.mode == "cwl":
                print("War prep - CWL")
                war_prep(cwl=True)
            if admin.mode == "battle_day":
                print("War prep - Battle Day")
                war_prep(cwl=False)
            goto(pycharm)
            admin.war_donations_remaining = -1
            wait(60 * 3)
        # else:
        #     print("Pause check:", pause_hour, in_time_zone(pause_hour, pause_hour + 3))
        #     time.sleep(60)

def check_status_files_exist():
    for account in accounts:
        for type in ["builders", "gold", "time"]:
            file = f"temp/tracker/{type}{account.number}.png"
            if not Path(file).is_file():
                print("Creating status file:", file)
                update_images(account, create=True)
    file = "temp/tracker/status.png"
    if not Path(file).is_file():
        print("Creating main status file.")
        update_image()

def seconds_to_half_hour():
    now = datetime.now()
    result = (now.replace(minute=30 * (now.minute//30), second=0, microsecond=0) + timedelta(minutes=30) - now).seconds
    return result


set_current_account()
run(pause_hour=None)
# war_prep()

goto(pycharm)

