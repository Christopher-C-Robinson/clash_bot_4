import sqlite3
from excel import *

TABLE_NAME = "image"

def db(db_str):
    con = sqlite3.connect('data.db')
    c = con.cursor()
    # print(db_str)
    c.execute(db_str)
    output = c.fetchall()
    con.commit()
    con.close()
    return output

def db_create_table():
    db_str = f"CREATE TABLE {TABLE_NAME}(name TEXT, success INTEGER, failure INTEGER)"
    db(db_str)

def db_delete_table():
    db_str = f"DROP TABLE {TABLE_NAME}"
    db(db_str)
    db_create_table()

def db_image_update(image, result):
    name = image.name
    if result:
        success, failure = 1, 0
        variable = "success"
    else:
        success, failure = 0, 1
        variable = "failure"
    condition = f" WHERE name='{name}'"
    output = db(f"SELECT * FROM {TABLE_NAME} {condition}")
    existing = len(output)
    # print("Current Records: ", existing)
    if existing == 0:
        db_str = f"INSERT INTO {TABLE_NAME} VALUES ('{name}', '{success}', '{failure}')"
        db(db_str)
    else:
        success += int(output[0][1])
        failure += int(output[0][2])
        if result:
            value = success
        else:
            value = failure
        db_str = f"UPDATE {TABLE_NAME} SET {variable}='{value}'" + condition
        db(db_str)

def db_image_view():
    file = ROOT_DIR + "/excel/log.xlsx"

    db_str = f"SELECT * FROM {TABLE_NAME} ORDER BY success"
    output = db(db_str)

    log_wb = xl.load_workbook(file)
    log_ws = log_wb["Sheet2"]
    row = admin.excel_last_row_image

    print()
    print("Image database")
    for values in output:
        for count, value in enumerate(values, 1):
            log_ws.cell(row, count).value = value
        row += 1
        print(values)
    log_wb.save(file)
    log_wb.close()

def db_image_read(image):
    name = image.name
    db_str = f"SELECT * FROM {TABLE_NAME} WHERE name='{name}'"
    output = db(db_str)[0]
    if len(output) > 0: return output[1], output[2]
    return None

# db_delete_table()
if __name__ == "__main__":
    db_image_view()

