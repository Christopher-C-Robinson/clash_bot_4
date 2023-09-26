import sqlite3

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

def db_delete_table(name):
    db_str = f"DROP TABLE {TABLE_NAME}"
    db(db_str)

def db_image_update(name, result):
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
        print(db_str)
        db(db_str)
    else:
        success += output[0][1]
        failure += output[0][2]
        db_str = f"UPDATE {TABLE_NAME} SET {variable}='{name}'" + condition
        db(db_str)

def db_image_view():
    db_str = f"SELECT * FROM {TABLE_NAME} ORDER BY name"
    output = db(db_str)
    for name, success, failure in output:
        print(f"Image {name}: {success} {failure}")

def db_image_read(account):
    db_str = f"SELECT * FROM {TABLE_NAME} WHERE account='{account}'"
    output = db(db_str)
    if len(output) > 0: return output[0][1]
    return None

# db_create_table()

db_image_update("Test", False)
db_image_view()