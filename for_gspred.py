ua = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.57"}
from turtle import distance
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

    filename = "./data/races_2022.pickle"
    with open(filename, mode="rb") as f:
        races = pickle.load(f)

    nankan_url =  "https://www.nankankeiba.com"
    yyyy = "2022"

    worksheets = connect_gspred()
    ws = worksheets[0]

    for i, race in enumerate(races):
        # if i: continue
        if i and i%50 == 0:
            sleep(120)
        dt, course, r, racename, distance, head_count, condition, code = race
        url = nankan_url + "/result/" + yyyy + code + ".do"
        dfs = get_dfs(url)
        # win, qinella, trio = 0, 0, 0
        favorite, sec_fav, trd_fav = 0, 0, 0
        winner, sec_place, trd_place = "", "", ""
        for df in dfs:
            if df.columns[0] == "着":
                favorites, winners = [], []
                for i, row in df.iterrows():
                    if i < 3:
                        favorites.append(int(row["人気"]))
                        winners.append(row["馬名"])
            favorite, sec_fav, trd_fav = favorites
            winner, sec_place, trd_place = winners
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
        values = dt, course, r, racename, distance, head_count, condition
        values = values + (favorite, sec_fav, trd_fav, win, exac, trif, winner, sec_place, trd_place)
        print(values)
        # ws.append_row(values)

