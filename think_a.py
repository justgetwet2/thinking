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

if __name__ == "__main__":

    worksheets = connect_gspred()
    ws = worksheets[0]

    df = pd.DataFrame(ws.get_all_records())
    data = [t.trifecta for t in df.itertuples()]

    print("size   : ", len(data))
    print("max    :", np.max(data))
    print("min    :", np.min(data))
    print("mean   : ", round(np.mean(data), 2))
    print("median : ", round(np.median(data), 2))
    print("std    :", round(np.std(data), 2))

    plt.hist(data, range=(0, 6000000), bins=50)
    plt.show()