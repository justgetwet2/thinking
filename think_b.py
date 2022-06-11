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

    p = "./data/racenames_2022.pickle"
    with open(p, mode="rb") as f:
        races = pickle.load(f)

    nankan_url =  "https://www.nankankeiba.com"
    yyyy = "2022"

    worksheets = connect_gspred()
    ws = worksheets[0]

    for i, race in enumerate(races[:12]):
        target_url = race.split()[-1]
        url = nankan_url + "/race_info/" + yyyy + target_url + ".do"
        soup = get_soup(url)
        print(soup.select_one("span.race-name").text)
        # ws.append_row(values)