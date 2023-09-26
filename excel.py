import openpyxl as xl
from utilities import *
from admin import *

file = ROOT_DIR + "/excel/log.xlsx"
log_wb = xl.load_workbook(file)
log_ws = log_wb["Sheet1"]
admin.excel_last_row_log = len(list(log_ws.iter_rows()))
log_wb.close()


def log(admin_mode, account_mode, job, account, duration):
    time = datetime.now()
    print("Log:", time, admin_mode, account_mode, job, account, duration)
    log_wb = xl.load_workbook(file)
    log_ws = log_wb["Sheet1"]
    row = admin.excel_last_row_log + 1

    try:
        values = [time, admin_mode, account_mode, job, account, duration]
        for count, value in enumerate(values, 1):
            print("Log count:", count)
            log_ws.cell(row, count).value = value
        log_wb.save(file)
        log_wb.close()
        admin.excel_last_row_log += 1
    except:
        print("Couldn't update log")


