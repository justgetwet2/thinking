ua = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.57"}
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Hiragino sans"
# plt.rcParams["font.family"] = "meiryo"
import numpy as np
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

def times_for_boxplot(race):
    nankan_url =  "https://www.nankankeiba.com"
    yyyy = "2022"
    racename = race[1] + " " + race[2] + " " + race[3] + " " + race[4]
    print(racename)
    dist = race[4].split("m")[0]
    dist = dist.replace(",", "")
    race_distance = int(dist)
    entry_url = nankan_url + "/race_info/" + yyyy + race[-1] + ".do"
    soup = get_soup(entry_url)
    # race_data = soup.select_one("div#race-data01")
    # dist_text = race_data.select_one("a").text
    # dist_text = dist_text.strip()
    # dist_text = dist_text.split("m")[0]
    # dist_text = dist_text.strip("ダ").replace(",", "")
    # race_distance = int(dist_text)

    tbl = soup.select_one("table.tb01")
    tags = tbl.select("a.tx-mid")
    data = []
    for i, tag in enumerate(tags):
        ftimes = []
        # if i: continue
        uma_name = tag.text
        print(i+1, uma_name)
        uma_ulr = tag.get("href")
        url = nankan_url + uma_ulr
        dfs = get_dfs(url)
        for df in dfs:
            if df.columns[0] == "年月日":
                for j, row in df.iterrows():
                    # if j: continue
                    if type(row["人気"]) == float: # nan
                        continue
                    if "芝" in row["距離"]:
                        continue
                    distance = int(row["距離"].split("m")[0])
                    stime = row["タイム"]
                    condition = row["天候  馬場"].split("/")[1]
                    ftime = get_time(condition, stime)
                    if not ftime:
                        continue
                    ftimes.append((distance, ftime))
        
        med, race_ftimes = 0, []
        if ftimes:
            race_distance_ftimes, another_distance_ftimes = [], []
            for distance, ftime in ftimes:
                if distance == race_distance:
                    race_distance_ftimes.append(ftime)
                else:
                    a = abs(race_distance - distance)
                    if a <= 100:
                        ftime = ftime * (race_distance / distance)
                        another_distance_ftimes.append(ftime)
            
            race_ftimes = [ftime for i, ftime in enumerate(race_distance_ftimes) if i < 10]
            x = 10 - len(race_ftimes)
            if x > 0:
                another_ftimes = [ftime for i, ftime in enumerate(another_distance_ftimes) if i < x]
                race_ftimes = race_ftimes + another_ftimes
            med = np.percentile(race_ftimes, 50)

        data.append((i+1, med, race_ftimes))

    sorted_data = sorted(data, key=lambda x: x[1])
    plots = [t[2] for t in sorted_data]
    xlabels = [str(t[0]) for t in sorted_data]

    return racename, plots, xlabels

if __name__ == "__main__":

    filename = "./data/races_2022.pickle"
    with open(filename, mode="rb") as f:
        races = pickle.load(f)

    race = races[-1]
    racename, plots, xlabels = times_for_boxplot(race)

    import warnings
    warnings.simplefilter('ignore', UserWarning)
    # UserWarning: FixedFormatter should only be used together with FixedLocator
    fig, ax = plt.subplots()
    ax.set_title(racename)
    ax.set_xticklabels(xlabels)
    ax.boxplot(plots)

    plt.show()
