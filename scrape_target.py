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

    jockey_d = jocky_reading()

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
        prize = soup.select("span.tx-gray01")[1].text
        prize = prize.split()[1][2:]
        number_of_horses = len(soup.select("td.titi-haha"))
        dist_tag = soup.select_one("div#race-data01-a")
        distance = dist_tag.select_one("a").text
        distance = distance.strip().replace(",", "")
        title = soup.select_one("span.race-name").text
        title = re.sub("　| ", "", title)
        weather = get_weather(info_url)
        date = info_url[42:-11]
        racename = date + " " + course + " " + race + "R" + " " + title + " "
        racename += prize + " " + distance + " " + weather + " " + str(number_of_horses) + "頭"

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
        if i > -1:
            for race in (srj(n) for n in range(1, 13)):
                target = dt + course_d[course] + hold + race + ".do"
                info_url = nankan_url + "/race_info/" + yyyy + target
                racename = get_racename(info_url)
                # print(racename)
                is_dist = [d for d in ("1500",) if d in racename]
                # is_class = "Ｃ" in racename or "Ｂ" in racename
                is_class = "Ｃ" in racename
                is_condition = not "雨" in racename and not "不良" in racename
                if is_dist and is_class and is_condition:
                    print(racename)
                    prize = racename.split()[-4]
                    race_prize = int(re.sub(",|円", "", prize))

                    entry_data = []
                    entry_df = get_dfs(info_url)[0]
                    for i, row in entry_df.iterrows():
                        row.index = [re.sub(" |（|）|\(|\)", "", s) for s in row.index]
                        # print(row)
                        sexage_color = row.性齢毛色
                        sex_d = {"牡": 0, "牝": 1, "セ": 1}
                        sex_kanji = sexage_color.split()[0][0]
                        sex = sex_d[sex_kanji]
                        age = int(sexage_color.split()[0][1:])
                        weight_delta = row.馬体重増減
                        weight = 0
                        delta_weight = 0
                        try:
                            weight = int(weight_delta.split()[0])
                            delta = weight_delta.split()[1]
                            mark_d = {"-": -1, "ー": -1, "＋": 1, "+": 1, "±": 1}
                            mark = delta[0]
                            delta_weight = int(delta[1:])
                            delta_weight = delta_weight * mark_d[mark]
                        except:
                            pass
                        burden = 0.0
                        try:
                            burden = float(row.負担重量)
                        except:
                            pass
                        jockey_belong = row.騎手名所属
                        jockey = jockey_belong.split()[0]
                        jockey_qine_ratio = 0.0
                        try:
                            ratio = jockey_d[jockey]
                            jockey_qine_ratio = float(ratio.replace("%", ""))
                        except:
                            pass
                        tp = race_prize, sex, age, weight, delta_weight, burden, jockey_qine_ratio
                        entry_data.append(tp)

                    race_condition = racename.split()[-2].split("/")[1]

                    soup = get_soup(info_url)
                    tags = soup.select("a.tx-mid")
                    
                    horse_data = []
                    for tag in tags:
                        horse_name = tag.text
                        url = nankan_url + tag.get("href")
                        dfs = get_dfs(url)
                        
                        summary_df = dfs[2]
                        col_name = summary_df.columns[-1] # 連対率
                        qine_ratio = 0.0
                        if col_name == "連対率":
                            qine_ratio = float(summary_df[col_name][0])

                        history_df = dfs[-1]
                        last_time = ""
                        last_3f = ""
                        if history_df.columns[0] == "年月日":
                            for i, row in history_df.iterrows():
                                if i > -1:
                                    row.index = [s.replace(" ", "") for s in row.index]
                                    weat_cond = row.天候馬場
                                    try:
                                        each_condition = weat_cond.split("/")[1]
                                    except: # nan
                                        each_condition = ""
                                    if not type(row.タイム) == float and row.距離 in racename and race_condition == each_condition:
                                        last_time = row.タイム
                                        last_3f = row.上3F
                                        break
                        # print(last_time, last_3f)
                        tp = qine_ratio, last_time, last_3f
                        horse_data.append(tp)

                    # odds_url = nankan_url + "/odds/" + yyyy + target.strip(".do") + "01.do"
                    # odds_dfs = get_dfs(odds_url)
                    # odds_df = [df for df in odds_dfs if df.columns[0] == "枠番"][0]
                    
                    result_url = nankan_url + "/result/" + yyyy + target
                    
                    result_df = get_dfs(result_url)[0]
                    for (i, row), entry, horse in zip(result_df.iterrows(), entry_data, horse_data):
                        horse_name = row.馬名
                        result_time = row.タイム
                        prize = entry[0]
                        sex = entry[1]
                        age = entry[2]
                        weight = entry[3]
                        delta_weight = entry[4]
                        burden = entry[5]
                        
                        horse_qune_raito = horse[0]
                        jockey_qine_raito = entry[6]
                        
                        last_time = horse[1]
                        last_3f = horse[2]

                        tp = [horse_name, racename, race_condition]
                        tp += [result_time, prize, sex, age, weight, delta_weight, burden]
                        tp += [last_time, last_3f, horse_qune_raito, jockey_qine_raito]
                        print(tp)
                        data.append(tp)

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


    filename = "./data/" + "april_test.pickle"
    with open(filename, "wb") as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)