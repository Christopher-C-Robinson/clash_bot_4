import sqlite3
from datetime import datetime, timedelta

# from bot import *

def db(db_str):
    con = sqlite3.connect('data.db')
    c = con.cursor()
    # print(db_str)
    c.execute(db_str)
    output = c.fetchall()
    con.commit()
    con.close()
    return output

date_variables = ["completion_date", ]

def db_create_table():
    db_str = "CREATE TABLE accounts(account INTEGER, variable TEXT, value INTEGER)"
    db(db_str)

def db_delete_table(table):
    db_str = f"DROP TABLE {table}"
    db(db_str)

def db_account_update(account, variable, value):
    condition = f" WHERE account='{account}' and variable = '{variable}'"
    db_str = f"SELECT * FROM accounts" + condition
    existing = len(db(db_str))
    if existing == 0: db_str = f"INSERT INTO accounts VALUES ({account}, '{variable}', '{value}')"
    else: db_str = f"UPDATE accounts SET value='{value}'" + condition
    # print("Execution string in db_account_update:", db_str)
    db(db_str)

def db_account_read(account, variable):
    condition = f" WHERE account='{account}' and variable = '{variable}'"
    db_str = f"SELECT * FROM accounts" + condition
    result = db(db_str)
    if len(result) > 0:
        value = result[0][2]
        if variable in date_variables: value = datetime.fromisoformat(value)
        return value


def db_delete():
    db_str = f"DELETE from accounts"
    db(db_str)

def db_account_view():
    db_str = "SELECT * FROM accounts ORDER BY account"
    output = db(db_str)
    for account, variable, value in output:
        if variable in date_variables:
            value = datetime.fromisoformat(value)
        print(f"Account {account}: {variable}: {value}")

# db_create_table()
# db_account_view()

if __name__ == "__main__":
    db_account_view()
