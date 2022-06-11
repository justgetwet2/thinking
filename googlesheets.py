import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_KEY = "1_x_5HTf7hMZjmgrgIjVMf9O13iAXDD4V6I562yaGTls"
JSON_FILE = "./token.json"

def connect_gspred():
    scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_file(JSON_FILE, scopes=scope)
    gc = gspread.authorize(credentials)
    workbook = gc.open_by_key(SPREADSHEET_KEY)
    worksheets = workbook.worksheets()
    return worksheets


if __name__ == "__main__":

    worksheets = connect_gspred()
    ws = worksheets[0]

    # print(ws.cell(1,1).value)
    # print(ws.acell("A1").value)
    # a = 1,2,3
    # ws.append_row(a)
    ws.clear()