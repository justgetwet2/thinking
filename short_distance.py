ua = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.57"}
from bs4 import BeautifulSoup
import pandas as pd
import pickle
import re
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

    filepath = "./data/" + "races_2022.pickle"
    with open(filepath, "rb") as f:
        races = pickle.load(f)

    races = [race for race in races if re.match("800m", race[3]) or re.match("900m", race[3])]
    print(len(races))
    invest, payout = 0, 0
    for i, race in enumerate(races):
        # if i > 10:
        #     continue
        # print(race[2], race[3], race[-1])
        target_code = race[-1]
        url = nankan_url + "/result/" + yyyy + target_code + ".do"
        dfs = get_dfs(url)
        if len(dfs[0]) < 8: # 8頭以上
            continue
        for df in dfs:
            if df.columns[0] == "着":
                orders = []
                for i, row in df.iterrows():
                    if i == 0:
                        winner = row["馬名"]
                    if i < 3:
                        orders.append(int(row["人気"]))
            if df.columns[0] == "単勝":
                w = df.at[1, "単勝"], df.at[1, "単勝.1"].strip("円").replace(",", ""), df.at[1, "単勝.2"]
                p1 = df.at[1, "複勝"], df.at[1, "複勝.1"].strip("円").replace(",", ""), df.at[1, "複勝.2"]
                p2 = df.at[2, "複勝"], df.at[2, "複勝.1"].strip("円").replace(",", ""), df.at[2, "複勝.2"]
                p3 = df.at[3, "複勝"], df.at[3, "複勝.1"].strip("円").replace(",", ""), df.at[3, "複勝.2"]
                payout_df = pd.DataFrame([w, p1, p2, p3], columns=("umaban", "payout", "fav"))
                # print(race[0], race[2], orders, [int(n) for n in payout_df["fav"][1:].to_list()])
                win_df = payout_df.iloc[0, :]
                invest += 1000
                if win_df["fav"] == "2":
                    payout += int(win_df["payout"]) * 10

    print(invest, payout, round(payout/invest, 2))