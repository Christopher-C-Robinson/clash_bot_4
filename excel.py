import openpyxl as xl
from utilities import *
from admin import *


def set_last_row():
    file = ROOT_DIR + "/excel/log.xlsx"
    try:
        log_wb = xl.load_workbook(file)
        log_ws = log_wb["Sheet1"]
        admin.excel_last_row_log = len(list(log_ws.iter_rows()))
        log_ws.cell(1, 1).value = "Log"
        log_wb.save(file)
        log_wb.close()
        print("Last row:", admin.excel_last_row_log)
    except:
        print()
        print("You've got Excel open.")
        time.sleep(60)

set_last_row()



def log(admin_mode, account_mode, job, account, duration):
    file = ROOT_DIR + "/excel/log.xlsx"
    time = datetime.now()
    print("Log:", time, admin_mode, account_mode, job, account, duration)
    log_wb = xl.load_workbook(file)
    log_ws = log_wb["Sheet1"]
    row = admin.excel_last_row_log + 1

    try:
        values = [time, admin_mode, account_mode, job, account, duration]
        for count, value in enumerate(values, 1):
            log_ws.cell(row, count).value = value
        log_wb.save(file)
        log_wb.close()
        admin.excel_last_row_log += 1
    except:
        print("Couldn't update log")

