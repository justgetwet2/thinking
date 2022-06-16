ua = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.57"}
from bs4 import BeautifulSoup
import pandas as pd
import pickle
import requests

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

    filename = "./data/races_2022.pickle"
    with open(filename, mode="rb") as f:
        races = pickle.load(f)

    dic = {}
    for i, race in enumerate(races):
        if i: continue
        entry_url = nankan_url + "/race_info/" + yyyy + race[-1] + ".do"
        soup = get_soup(entry_url)
        tbl = soup.select_one("table.tb01")
        tags = tbl.select("a.tx-mid")
        for j, tag in enumerate(tags):
            if j: continue
            uma_name = tag.text
            uma_ulr = tag.get("href")
            url = nankan_url + uma_ulr
            dfs = get_dfs(url)
            for df in dfs:
                if df.columns[0] == "年月日":
                    for idx, row in df.iterrows():
                        # if idx: continue
                        racename = row["レース名"]
                        course = row["場名"]
                        dist = row["距離"]
                        time = row["タイム"]
                        cond = row["天候  馬場"]
                        fav = row["人気"].replace(" ", "")
                        odr = "".join(row["着/頭数"].split()[:2])
                        print(odr, fav, dist, time, cond, course, racename)