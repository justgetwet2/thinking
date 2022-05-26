ua = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.57"}
from bs4 import BeautifulSoup
import pandas as pd
import pickle
import re
import requests

nankan_url =  "https://www.nankankeiba.com"
course_d = { "浦和": "18", "船橋": "19", "大井": "20", "川崎": "21" }
eng_d = { "18": "urawa", "19": "funabashi", "20": "ooi", "21": "kawasaki" }
yyyy = "2022"

def get_soup(url):
    res = requests.get(url, headers=ua)
    
    return BeautifulSoup(res.content, "html.parser")

def get_dfs(url):
    soup = get_soup(url)
    dfs = []
    if soup.find("table"):
        dfs = pd.io.html.read_html(soup.prettify())
    else:
        print(f"it's no table! {url}")
    return dfs

def jocky_reading():

    nankan_url =  "https://www.nankankeiba.com"
    jokeky_url = "/ltd/leading_kis/000000002022011.do"
    url = nankan_url + jokeky_url
    df = get_dfs(url)[0]
    d = {}
    for i, row in df.iterrows():
        jockey = row.騎手名
        count = row.騎乗回数
        qin_rate = row.連対率
        if count > 10:
            d[jockey] = qin_rate
    
    return d

if __name__ == "__main__":

    jokeky_url = "/ltd/leading_kis/000000002022011.do"
    # 南関東 202201- 勝利数順


    url = nankan_url + jokeky_url
    df = get_dfs(url)[0]
    for i, row in df.iterrows():
        order = row.順位
        jockey = row.騎手名
        count = row.騎乗回数
        win_rate = row.勝率
        qin_rate = row.連対率
        if count > 10:
            print(jockey, qin_rate)