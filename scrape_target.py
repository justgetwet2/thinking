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

if __name__ == "__main__":

    srj = lambda i: str(i).rjust(2, "0")
    # month = [("0401", "大井", "0101")] # 中止
    def april_races():
        month = [(f"04{srj(i+4)}", "川崎", f"01{srj(i+1)}") for i in range(5)]
        month += [(f"04{srj(i+11)}", "船橋", f"01{srj(i+1)}") for i in range(5)]
        month += [(f"04{srj(i+18)}", "大井", f"02{srj(i+1)}") for i in range(5)]
        month += [(f"04{srj(i+25)}", "浦和", f"01{srj(i+1)}") for i in range(5)]

        return month

    def get_racename(info_url):
        soup = get_soup(info_url)
        number_of_horses = len(soup.select("td.titi-haha"))
        dist_tag = soup.select_one("div#race-data01-a")
        distance = dist_tag.select_one("a").text.strip()
        title = soup.select_one("span.race-name").text
        title = re.sub("　| ", "", title)
        weather = get_weather(info_url)
        date = info_url[42:-11]
        racename = date + " " + course + " " + race + "R" + " " + title + " "
        racename += distance + " " + weather + " " + str(number_of_horses) + "頭"

        return racename

    def get_weather(info_url):
        url = info_url[:-5] + ".do"
        program_url = url.replace("/race_info/", "/program/")
        soup = get_soup(program_url)
        tag = soup.select_one("div#sts-bangumi")
        img1, img2 = tag.select("img")
        weat = img1.get("alt")
        cond = img2.get("alt")

        return weat.split("：")[1] + "/" + cond.split("：")[1]

    races = april_races()
    # racenames = []
    data = []
    for i, (dt, course, hold) in enumerate(races):
        if i == 0:
            for race in (srj(n) for n in range(1, 13)):
                target = dt + course_d[course] + hold + race + ".do"
                info_url = nankan_url + "/race_info/" + yyyy + target
                racename = get_racename(info_url)
                # print(racename)
                is_dist = [d for d in ("1,500",) if d in racename]
                if is_dist and "Ｃ" in racename:
                    print(racename)

                    entry_df = get_dfs(info_url)[0]
                    race_condition = racename.split()[-2].split("/")[1]

                    soup = get_soup(info_url)
                    tags = soup.select("a.tx-mid")
                    for tag in tags:
                        print(tag.text)
                        url = nankan_url + tag.get("href")
                        dfs = get_dfs(url)
                        df = dfs[-1]
                        if df.columns[0] == "年月日":
                            for i, row in df.iterrows():
                                if i == 0:
                                    row.index = [s.replace(" ", "") for s in row.index]
                                    weath_cond = row.天候馬場
                                    each_condition = weath_cond.split("/")[1]
                                    if race_condition == each_condition:
                                        print(row.タイム)

                    odds_url = nankan_url + "/odds/" + yyyy + target.strip(".do") + "01.do"
                    odds_dfs = get_dfs(odds_url)
                    odds_df = [df for df in odds_dfs if df.columns[0] == "枠番"][0]
                    
                    result_url = nankan_url + "/result/" + yyyy + target
                    
                    result_df = get_dfs(result_url)[0]

                    data.append((racename, entry_df, odds_df, result_df))

# 年月日              22/05/20
# 場名                     川崎
# R                      5R
# レース名          Ｃ３(一)(二)(三)
# 距離                  1400m
# 天候  馬場                晴/良
# 馬番                  11  番
# 人気                   4  人
# 着/頭数         1  着  /12  頭
# タイム                1:31.2
# 差/事故                  0.3
# 上3F                  39.7
# コーナー  通過順           4-3-3
# 体重                    480
# 騎手                    野畑凌
# 負担  重量               51.0
# 調教師                   八木喜
# 獲得賞金           800,000  円


    # filename = "./data/" + "april_c.pickle"
    # with open(filename, "wb") as f:
    #     pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)