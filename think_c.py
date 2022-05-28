ua = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.57"}
from bs4 import BeautifulSoup
import numpy as np
import matplotlib.pyplot as plt
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

def ftime(s):
    if ":" in s:
        a, b = s.split(":")
        time = int(a) * 60 + float(b)
    else:
        time = float(s)
    return time

if __name__ == "__main__":

    filepath = "./data/racenames_22.pickle"
    with open(filepath, mode="rb") as f:
        races = pickle.load(f)

    b = [race for race in races if re.match("Ｂ", race.split()[2])]
    c1 = [race for race in races if re.match("Ｃ１\(", race.split()[2])]
    c2 = [race for race in races if re.match("Ｃ２\(", race.split()[2])]
    c3 = [race for race in races if re.match("Ｃ３\(", race.split()[2])]
    
    print("all", "B", "C1", "C2", "C3")
    print(len(races), len(b), len(c1), len(c2), len(c3))

    c3_1500 = [race for race in c3 if "1,600m" in race.split()[-4]]
    c3_1500_dry = [race for race in c3_1500 if "/良" in race.split()[-2]]
    c3_1500_wet = [race for race in c3_1500 if "/稍重" in race.split()[-2]]
    c3_1500_hvy = [race for race in c3_1500 if "/重" in race.split()[-2]]

    print(len(c3_1500), len(c3_1500_dry), len(c3_1500_wet), len(c3_1500_hvy))

# all B C1 C2 C3
# 708 9 39 107 92
# 14 5 2 3


    # for races in [c3_1500_dry, c3_1500_wet, c3_1500_hvy]:
    #     x = []
    #     for race in races:
    #         result_url = nankan_url + "/result/" + yyyy + race.split()[-1] + ".do"
    #         dfs = get_dfs(result_url)
    #         result_df = dfs[0]
    #         x += [ftime(row.タイム) for i, row in result_df.iterrows() if row.タイム != "-"]
        
    #     print(len(races), len(x), np.mean(x))




    # fig = plt.figure()
    # ax = fig.add_subplot(1,1,1)

    # ax.hist(favs, bins=50)
    # ax.set_title('tri histogram')
    # ax.set_xlabel('favorite')
    # ax.set_ylabel('freq')
    # plt.show()


    # print(pd.__version__)

    # favs = []
    # for i, (racename, entry_df, odds_df, result_df) in enumerate(races):
    #     # print(racename)
    #     if i > -1:
    #         odds_d = {}
    #         for idx, row in odds_df.iterrows():
    #             try:
    #                 odds = float(row["単勝"])
    #                 odds_d[row["馬番"]] = odds
    #             except:
    #                 pass
    #         # print(odds_d)        
    #         for idx, row in result_df.iterrows():
    #             if idx < 2:
    #                 umaban, fav = row["馬番"], int(row["人気"])# 人気 1.0
    #                 # winnings.append((umaban, row["馬名"], fav, odds_d[umaban])) 
    #                 favs.append(fav)
    #                 # print(umaban, row["馬名"], fav, odds_d[umaban])