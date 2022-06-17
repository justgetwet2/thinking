ua = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.57"}
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
# plt.rcParams["font.family"] = "Hiragino sans"
plt.rcParams["font.family"] = "meiryo"
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

def float_time(s):
    if ":" in s:
        a, b = s.split(":")
        ftime = int(a) * 60 + float(b)
    else:
        ftime = float(s)
    return ftime

def str_time(f):
    stime = ""
    if f:
        if f > 60.0:
            sec = f - 60.0
            stime = "1:" + str(round(sec, 1))
        elif f <= 60.0:
            stime = str(round(f, 1))
    return stime

def get_time(condition, stime):
    ftime = None
    if condition == "良":
        ftime = float_time(stime)
    if condition == "稍重":
        ftime = float_time(stime) + 0.2
    if condition == "重":
        ftime = float_time(stime) + 0.1
    return ftime

if __name__ == "__main__":

    nankan_url =  "https://www.nankankeiba.com"
    yyyy = "2022"
    JRA = "札幌", "函館", "福島", "新潟", "中山", "東京", "中京", "京都", "阪神", "小倉"

    filename = "./data/races_2022.pickle"
    with open(filename, mode="rb") as f:
        races = pickle.load(f)

    dic = {}
    for i, race in enumerate(races):
        if i != len(races) - 6: continue
        print(race)
        entry_url = nankan_url + "/race_info/" + yyyy + race[-1] + ".do"
        soup = get_soup(entry_url)
        race_data = soup.select_one("div#race-data01")
        dist_text = race_data.select_one("a").text
        dist_text = dist_text.strip()
        dist_text = dist_text.split("m")[0]
        dist_text = dist_text.strip("ダ").replace(",", "")
        race_distance = int(dist_text)
        # print("distance:", race_distance)
        tbl = soup.select_one("table.tb01")
        tags = tbl.select("a.tx-mid")
        data = []
        data_y = []
        for j, tag in enumerate(tags):
            # if j >1: continue
            uma_name = tag.text
            print("***", uma_name)
            uma_ulr = tag.get("href")
            url = nankan_url + uma_ulr
            dfs = get_dfs(url)
            for df in dfs:
                x, y = [], []
                if df.columns[0] == "年月日":
                    for idx, row in df.iterrows():
                        # if idx: continue
                        if type(row["人気"]) == float: # nan
                            continue
                        # if row["場名"] in JRA:
                        #     continue
                        racename = row["レース名"]
                        course = row["場名"]
                        distance = int(row["距離"].split("m")[0])

                        stime = row["タイム"]
                        condition = row["天候  馬場"].split("/")[1]
                        ftime = get_time(condition, stime)
                        if not ftime:
                            continue
                        fav = row["人気"].replace(" ", "")
                        odr = "".join(row["着/頭数"].split()[:2])
                        # print(odr, fav, distance, stime, condition, course, racename)
                        if len(x) > 20:
                            continue
                        if race_distance == distance:
                            x.append(j+1)
                            y.append(ftime)
                        # if 1600 <= distance and distance <= 1650:
                        #     data_y.append(ftime)
            data.append(y)

    fig, ax = plt.subplots()
    ax.set_title(race[3] + " " + race[4])
    # ax.set_ylim([min(data_y), max(data_y)])
    # ax.set_xlim([1200, 1800])
    # for y in data:
    #     # ax.plot(x, y, ".")
    #     ax.boxplot(y)
    ax.boxplot(data)
    ax.set_xticklabels([i for i in range(1, len(data)+1)])
    plt.show()