from troops import *

def read_troops():
    file = ROOT_DIR + "/excel/army_troops.xlsx"
    try:
        wb = xl.load_workbook(file)
        ws = wb["Sheet1"]
        last_row = len(list(ws.iter_rows()))
        last_col = len(list(ws.iter_cols()))
    except:
        print("Couldn't open troops file")
        return

    troops_db = []
    output = []
    row = 1
    for col in range(3, last_col):
        troop_string = ws.cell(row, col).value
        troop = get_troop(troop_string)
        troops_db.append(troop)
        # print(troop)

    for row in range(2, last_row + 1):
        account_no = ws.cell(row, 1).value
        cat = ws.cell(row, 2).value
        troops_acc = []

        for index, col in enumerate(range(3, last_col)):
            result = ws.cell(row, col).value
            if not result: result = 0
            number = int(result)
            troop = troops_db[index]
            troops_acc += [troop] * number

        data = (account_no, cat, troops_acc)
        output.append(data)
    # print(output)
    return output

troop_db = read_troops()

