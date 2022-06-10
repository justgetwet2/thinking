import datetime
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import pickle
import re

import gspread
from google.oauth2.service_account import Credentials

# 2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
#ダウンロードしたjsonファイル名をクレデンシャル変数に設定。
credentials = Credentials.from_service_account_file("token.json", scopes=scope)
#OAuth2の資格情報を使用してGoogle APIにログイン。
gc = gspread.authorize(credentials)
#スプレッドシートIDを変数に格納する。
SPREADSHEET_KEY = '1_x_5HTf7hMZjmgrgIjVMf9O13iAXDD4V6I562yaGTls'
# token.json - "client_email"の横に書かれているアドレスをコピーする
# スプレッドシートの共有を開き、コピーしたアドレスをユーザーやグループに追加に記入。

# スプレッドシート（ブック）を開く
workbook = gc.open_by_key(SPREADSHEET_KEY)




if __name__ == "__main__":

    filepath = "./data/racenames_22.pickle"
    with open(filepath, mode="rb") as f:
        races = pickle.load(f)

    print(races[0])

    # シートの一覧を取得する。（リスト形式）
    worksheets = workbook.worksheets()
    # print(worksheets)
    worksheet = worksheets[0]

    for race in races[:12]:
        worksheet.append_row([race])
