import openpyxl as xl
from utilities import *
from admin import *

# file = ROOT_DIR + "/excel/image_db.xlsx"
# image_wb = xl.load_workbook(file)
# image_ws = image_wb["Sheet1"]
# admin.excel_last_row_images = len(list(image_ws.iter_rows()))

# def excel_write_image(image, result):
#     row = admin.excel_last_row_images + 1
#     image_ws.cell(row, 1).value = image.name
#     image_ws.cell(row, 2).value = result
#     try:
#         image_wb.save(file)
#         admin.excel_last_row_images += 1
#     except:
#         pass
