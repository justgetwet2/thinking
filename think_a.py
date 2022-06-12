import gspread
from google.oauth2.service_account import Credentials
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SPREADSHEET_KEY = "1_x_5HTf7hMZjmgrgIjVMf9O13iAXDD4V6I562yaGTls"
JSON_FILE = "./token.json"

def connect_gspred():
    scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_file(JSON_FILE, scopes=scope)
    gc = gspread.authorize(credentials)
    workbook = gc.open_by_key(SPREADSHEET_KEY)
    worksheets = workbook.worksheets()
    return worksheets

def describe(values):
    pd.options.display.float_format = '{:.2f}'.format
    df = pd.DataFrame(values, columns=("X",))
    print(df.describe())

if __name__ == "__main__":

    worksheets = connect_gspred()
    ws = worksheets[0]

    df = pd.DataFrame(ws.get_all_records())
    x = [t.trifecta for t in df.itertuples()]

    describe(x)

    plt.title("trifecta payout chart 0 - 6000k")
    # plt.hist(x, bins=50)
    plt.hist(x, range=(0, 1000000), bins=50)
    plt.show()