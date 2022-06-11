
ua = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.57"}
from bs4 import BeautifulSoup
import pandas as pd
import pickle
import requests
from time import sleep

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

def get_soup(url):
    try:
        res = requests.get(url, headers=ua)
    except requests.RequestException as e:
        print("Error: ", e)
    else:
        return BeautifulSoup(res.content, "html.parser")

def get_dfs(url):
    dfs = []
    soup = get_soup(url)
    if soup:
        if soup.find("table"):
            dfs = pd.io.html.read_html(soup.prettify())
        else:
            print(f"It's no table! {url}")
    return dfs

if __name__ == "__main__":

    nankan_url =  "https://www.nankankeiba.com"
    yyyy = "2022"

    p = "./data/racenames_2022.pickle"
    with open(p, mode="rb") as f:
        races = pickle.load(f)

    worksheets = connect_gspred()
    ws = worksheets[0]

    for i, race in enumerate(races[234:]):
        if i and i%50 == 0:
            sleep(120)
        dt = race.split()[-1:][0][:4] + " " + " ".join(race.split()[:2])
        racename = " ".join(race.split()[2:-4:])
        print(dt, racename)
        dist = race.split()[:-3:][-1].strip("ダ")
        entries = race.split()[:-2:][-1]
        condition = race.split()[:-1:][-1]
        # print(dt, racename, dist, entries, condition)
        target_url = race.split()[-1]
        url = nankan_url + "/result/" + yyyy + target_url + ".do"
        dfs = get_dfs(url)
        win, qine, trio = 0, 0, 0
        fst, sec, trd = 0, 0, 0
        for df in dfs:
            if df.columns[0] == "着":
                orders = []
                for i, row in df.iterrows():
                    if i == 0:
                        winner = row["馬名"]
                    if i < 3:
                        orders.append(int(row["人気"]))
            fst, sec, trd = orders
            if df.columns[0] == "単勝":
                for i, row in df.iterrows():
                    if row.name == 1:
                        win_s = row["単勝.1"]
                        win = int(win_s.strip("円").replace(",", ""))
                        exac_s = row["馬単.1"]
                        exac = int(exac_s.strip("円").replace(",", ""))
            if df.columns[0] == "ワイド":
                for i, row in df.iterrows():
                    if row.name == 1:
                        trif_s = row["三連単.1"]
                        trif = int(trif_s.strip("円").replace(",", ""))
        values = dt, racename, dist, entries, condition, fst, sec, trd, win, exac, trif, winner
        # ws.append_row(values)
        print(values)
