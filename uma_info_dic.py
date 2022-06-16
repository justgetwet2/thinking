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
        for tag in tags:
            dic[tag.text] = tag.get("href")

    print(dic)
