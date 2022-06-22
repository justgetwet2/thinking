ua = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.57"}
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
fpath = "./fonts/Hiragino-Sans-GB-W3.ttf"
# fpath = "./fonts/NotoSansJP-Regular.otf"
fprop = fm.FontProperties(fname=fpath, size=10)
# print(fprop.get_name())
# plt.rcParams["font.family"] = fprop.get_name()
import numpy as np
import pandas as pd
import pickle
import pprint
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

def left(digit, msg):
    import unicodedata
    for c in msg:
        digit -= 1
        if unicodedata.east_asian_width(c) in "FWA":
            digit -= 1
    return msg + ' '*digit

def times_for_boxplot(race):
    nankan_url =  "https://www.nankankeiba.com"
    yyyy = "2022"
    racename = " ".join(race[:5])
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
        # print(i+1, uma_name)
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
        
        race_ftimes = []
        median = 0
        if ftimes:
            all_equidistant_ftimes, all_neardistant_ftimes = [], []
            for distance, ftime in ftimes:
                if distance == race_distance:
                    all_equidistant_ftimes.append(ftime)
                else:
                    a = abs(race_distance - distance)
                    if a <= 100:
                        ftime = ftime * (race_distance / distance)
                        all_neardistant_ftimes.append(ftime)
            
            equidistant_ftimes = [ftime for i, ftime in enumerate(all_equidistant_ftimes) if i < 10]
            neardistant_ftimes = []
            x = 10 - len(equidistant_ftimes)
            if x > 0:
                neardistant_ftimes = [ftime for i, ftime in enumerate(all_neardistant_ftimes) if i < x]
            race_ftimes = equidistant_ftimes + neardistant_ftimes
            # if not race_ftimes:
            #     continue
            last_time = race_ftimes[0]
            race_ftimes.append(last_time)
            median = np.percentile(race_ftimes, 50)

            print(f"{i+1:2} {left(20, uma_name)} {len(equidistant_ftimes):2} {len(race_ftimes):2} {round(median, 1):7} {round(last_time, 1):7}")

        data.append((i+1, median, race_ftimes))

    sorted_data = sorted(data, key=lambda x: x[1]) # sort with median
    plots = [t[2] for t in sorted_data]
    xlabels = [str(t[0]) for t in sorted_data]

    return racename, plots, xlabels

if __name__ == "__main__":

    filename = "../nankan/data/today_races.pickle"
    # filename = "./data/races_2022.pickle"
    with open(filename, mode="rb") as f:
        races = pickle.load(f)

    r = 4
    race = races[r-1]
    racename, plots, xlabels = times_for_boxplot(race)

    import warnings
    warnings.simplefilter('ignore', UserWarning)
    # UserWarning: FixedFormatter should only be used together with FixedLocator
    fig, ax = plt.subplots()
    ax.set_title(racename, fontproperties=fprop)
    ax.set_xticklabels(xlabels)
    ax.boxplot(plots)

    last_times = [x[0] for x in plots]
    ax.plot(range(1, len(xlabels)+1), last_times, "o")

    medians = [np.percentile(x, 50) for x in plots]
    plt.axhline(y=sorted(medians)[5], color="y", linestyle="--")

    plt.show()
