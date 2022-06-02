ua = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.57"}
from bs4 import BeautifulSoup
import datetime
import numpy as np
import matplotlib.pyplot as plt
import math
import os
import pandas as pd
import pickle
import re
import requests
import warnings
warnings.simplefilter('ignore') # np.mean() -> nan

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

def today():
    dt = datetime.datetime.now()
    return str(dt.month).rjust(2, "0") + str(dt.day).rjust(2, "0")

def jocky_leading():

    mmdd = today()
    filename = "./data/jockey_leading_" + mmdd + "_.pickle"
    if not os.path.exists(filename):
        print("create jockey data ..")
        nankan_url =  "https://www.nankankeiba.com"
        jokeky_url = "/ltd/leading_kis/000000002022011.do"
        url = nankan_url + jokeky_url
        df = get_dfs(url)[0]
        d = {}
        for i, row in df.iterrows():
            jockey = row.騎手名
            count = row.騎乗回数
            ratio = row.連対率
            if count > 10:
                d[jockey] = float(ratio.replace("%", ""))

        with open(filename, "wb") as f:
            pickle.dump(d, f, pickle.HIGHEST_PROTOCOL)
    else:
        with open(filename, mode="rb") as f:
            d = pickle.load(f)

    return d

def get_entries(racename):
    target = racename.split()[-1]
    info_url = nankan_url + "/race_info/" + yyyy + target + ".do"
    jockey_d = jocky_leading()

    result_url = nankan_url + "/result/" + yyyy + target + ".do"
    
    result_df = get_dfs(result_url)[0]
    time_d = {}
    for i, row in result_df.iterrows():
        time = 0.0
        try:
            time = ftime(row.タイム)
        except:
            pass
        time_d[row.馬名] = time


    sex_d = {"牡": 0, "牝": 1, "セ": 1}
    mark_d = {"-": -1, "―": -1, "＋": 1, "+": 1, "±": 1}
    entry_df = get_dfs(info_url)[0]
    entries = []
    for i, row in entry_df.iterrows():
        row.index = [re.sub(" |（|）|\(|\)", "", s) for s in row.index]
        # print(row)
        name_birth = row.馬名生年月日
        name = name_birth.split()[0]
        sexage_color = row.性齢毛色
        sex_kanji = sexage_color.split()[0][0]
        sex = sex_d[sex_kanji]
        age = int(sexage_color.split()[0][1:])
        weight_delta = row.馬体重増減
        weight = 0
        delta_weight = 0
        burden = 0.0
        jockey_ratio = 0.0
        try:
            time = time_d[name]
            weight = int(weight_delta.split()[0])
            delta = weight_delta.split()[1]
            mark = delta[0]
            delta_weight = int(delta[1:]) * mark_d[mark]
            burden = float(row.負担重量)
            jockey_belong = row.騎手名所属
            jockey = jockey_belong.split()[0]
            jockey_ratio = jockey_d[jockey]
        except:
            pass
        data = name, time, sex, age, weight, delta_weight, burden, jockey_ratio
        index = "name", "time", "sex", "age", "weight", "delta_weight", "burden", "jokey_ratio"
        sr = pd.Series(data, index=index)
        entries.append(sr)

    return entries

JRA = "札幌", "函館", "福島", "新潟", "中山", "東京", "中京", "京都", "阪神", "小倉"
NANKAN = "大井", "船橋", "川崎", "浦和" # night race 大井⭐️

def get_time(condition, stime):
    time = None
    if type(condition) == str and type(stime) == str:
        if condition == "良":
            time = ftime(stime)
        if condition == "稍重":
            time = ftime(stime) + 0.2
        if condition == "重":
            time = ftime(stime) + 0.1
    return time

def get_horses(racename):
    print(racename)
    info_url = nankan_url + "/race_info/" + yyyy + racename.split()[-1] + ".do"
    race_condition = racename.split()[-2].split("/")[1]
    dist = racename.split()[-4]
    race_distance = dist.split("m")[0].strip("ダ").replace(",", "") + "m"

    soup = get_soup(info_url)
    tags = soup.select("a.tx-mid")
    srs = []
    for tag in tags:
        name = tag.text
        url = nankan_url + tag.get("href")
        dfs = get_dfs(url)
        
        summary_df = dfs[2]
        col_name = summary_df.columns[-1] # 連対率
        horse_ratio = 0.0
        try:
            horse_ratio = float(summary_df[col_name][0])
        except:
            pass

        history_df = dfs[-1]
        prev_time, prev_last3f, prev_time_diff = None, None, None
        if history_df.columns[0] == "年月日":
            last_race = None
            d1400_times, d1500_times, d1600_times = [], [], []
            for i, row in history_df.iterrows():
                if i > -1 and not row["場名"] in JRA:
                    weat_cond = row["天候  馬場"]
                    condition, stime = None, None
                    if type(weat_cond) == str:
                        condition = weat_cond.split("/")[1]
                        stime = row["タイム"]
                    if not last_race:
                        if type(stime) == str and row["距離"] == race_distance and condition == race_condition:
                            try:
                                prev_time = ftime(stime)
                                prev_last3f = ftime(str(row["上3F"])) # float or str
                                prev_time_diff = float(row["差/事故"])
                                last_race = 1
                            except:
                                pass
                    if row["距離"] == "1400m":
                        time = get_time(condition, stime)
                        if time: d1400_times.append(time)
                    if row["距離"] == "1500m":
                        time = get_time(condition, stime)
                        if time: d1500_times.append(time)
                    if row["距離"] == "1600m":
                        time = get_time(condition, stime)
                        if time: d1600_times.append(time)

        t1 = name, horse_ratio, prev_time
        t2 = len(d1400_times), np.mean(d1400_times), len(d1500_times), np.mean(d1500_times), len(d1600_times), np.mean(d1600_times)
        t3 = prev_last3f, prev_time_diff
        index = "name", "horse_ratio", "prev_time", "len_1400", "mean_1400", "len_1500", "mean_1500", "len_1600", "mean_1600", "prev_last3f", "prev_time_diff"
        sr = pd.Series(t1 + t2 + t3, index=index)
        srs.append(sr)

    return srs

if __name__ == "__main__":

    filepath = "./data/racenames_22.pickle"
    with open(filepath, mode="rb") as f:
        races = pickle.load(f)

    # b = [race for race in races if re.match("Ｂ", race.split()[2])]
    # c1 = [race for race in races if re.match("Ｃ１\(", race.split()[2])]
    # c2 = [race for race in races if re.match("Ｃ２\(", race.split()[2])]
    c3 = [race for race in races if re.match("Ｃ３\(", race.split()[2])]
    
    # print("all", "B", "C1", "C2", "C3")
    # print(len(races), len(b), len(c1), len(c2), len(c3))

    c3_1500 = [race for race in c3 if "1,500m" in race.split()[-4]]
    c3_1500_dry = [race for race in c3_1500 if "/良" in race.split()[-2]]
    c3_1500_wet = [race for race in c3_1500 if "/稍重" in race.split()[-2]]
    c3_1500_hvy = [race for race in c3_1500 if "/重" in race.split()[-2]]

    print(len(c3_1500), len(c3_1500_dry), len(c3_1500_wet), len(c3_1500_hvy))

# all B C1 C2 C3
# 708 9 39 107 92
# 14 5 2 3

# all B C1 C2 C3
# 948 10 52 136 126
# 19 9 2 3

    srs = []
    drys, wets, hvys = [], [], []
    for i, racename in enumerate(c3_1500_dry):
        if i == 0:
            entries = get_entries(racename)
            horses = get_horses(racename)
            for entry, horse in zip(entries, horses):
                sr = pd.concat([entry, horse[1:]])
                print(sr[0])
                srs.append(sr)
    df = pd.DataFrame(srs)
    # print(df)


    # filename = "./data/c3_1500.pickle"
    # with open(filename, "wb") as f:
    #     pickle.dump(srs, f, pickle.HIGHEST_PROTOCOL)
