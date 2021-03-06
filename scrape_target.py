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

    def ftime(s):
        a, b = s.split(":")
        return int(a) * 60 + float(b)

    def get_entries(info_url):
        sex_d = {"牡": 0, "牝": 1, "セ": 1}
        mark_d = {"-": -1, "―": -1, "＋": 1, "+": 1, "±": 1}
        entries = []
        entry_df = get_dfs(info_url)[0]
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
            jockey_qine_ratio = 0.0
            try:
                weight = int(weight_delta.split()[0])
                delta = weight_delta.split()[1]
                mark = delta[0]
                delta_weight = int(delta[1:]) * mark_d[mark]
                burden = float(row.負担重量)
                jockey_belong = row.騎手名所属
                jockey = jockey_belong.split()[0]
                ratio = jockey_d[jockey]
                jockey_qine_ratio = float(ratio.replace("%", ""))
            except:
                pass
            tp = name, sex, age, weight, delta_weight, burden, jockey_qine_ratio
            entries.append(tp)

        return entries

    def get_horses(info_url):
        racename = get_racename(info_url)
        race_condition = racename.split()[-2].split("/")[1]
        
        soup = get_soup(info_url)
        tags = soup.select("a.tx-mid")
        horses = []
        for tag in tags:
            # horse_name = tag.text
            url = nankan_url + tag.get("href")
            dfs = get_dfs(url)
            
            summary_df = dfs[2]
            col_name = summary_df.columns[-1] # 連対率
            horse_qine_ratio = 0.0
            try:
                horse_qine_ratio = float(summary_df[col_name][0])
            except:
                pass
            history_df = dfs[-1]
            last_time = 0
            last_3f = 0
            if history_df.columns[0] == "年月日":
                for i, row in history_df.iterrows():
                    if i > -1:
                        row.index = [s.replace(" ", "") for s in row.index]
                        weat_cond = row.天候馬場
                        each_condition = ""
                        try:
                            each_condition = weat_cond.split("/")[1]
                        except: # nan
                            pass                     
                        if race_condition == each_condition and row.距離 in racename:
                            try:
                                last_time = ftime(row.タイム)
                                last_3f = ftime(row.上3F)
                                break
                            except:
                                pass
            horses.append((horse_qine_ratio, last_time, last_3f))

        return horses

    races = april_races()
    # racenames = []
    srs = []
    for i, (dt, course, hold) in enumerate(races):
        if i > -1:
            for race in (srj(n) for n in range(1, 13)):
                target = dt + course_d[course] + hold + race + ".do"
                info_url = nankan_url + "/race_info/" + yyyy + target
                racename = get_racename(info_url)
                # print(racename)
                is_dist = [d for d in ("1500",) if d in racename]
                is_class = "Ｃ" in racename
                is_condition = not "雨" in racename and not "不良" in racename
                if is_dist and is_class and is_condition:
                    print(racename)
                    prize = racename.split()[-4]
                    race_prize = int(re.sub(",|円", "", prize))
                    race_condition = racename.split()[-2].split("/")[1]
                    num_horse = int(racename.split()[-1].strip("頭"))
                    
                    entries = get_entries(info_url)
                    horses = get_horses(info_url)

                    # odds_url = nankan_url + "/odds/" + yyyy + target.strip(".do") + "01.do"
                    # odds_dfs = get_dfs(odds_url)
                    # odds_df = [df for df in odds_dfs if df.columns[0] == "枠番"][0]
                    
                    result_url = nankan_url + "/result/" + yyyy + target
                    
                    result_df = get_dfs(result_url)[0]
                    result_d = {}
                    for i, row in result_df.iterrows():
                        time = 0.0
                        try:
                            time = ftime(row.タイム)
                        except:
                            pass
                        result_d[row.馬名] = time
                    for entry, horse in zip(entries, horses):
                        name = entry[0]
                        result_time = result_d[name]
                        sex = entry[1]
                        age = entry[2]
                        weight = entry[3]
                        delta_weight = entry[4]
                        burden = entry[5]
                        jockey_qine_raito = entry[6]
                        horse_qine_raito = horse[0]
                        last_time = horse[1]
                        last_3f = horse[2]

                        data = [racename, race_condition, name, result_time]
                        data += [num_horse, race_prize, sex, age, weight, delta_weight, burden]
                        data += [last_time, last_3f, horse_qine_raito, jockey_qine_raito]
                        idx = ["race", "condition", "horse_name", "result"]
                        idx += ["num_horse", "prize", "sex", "age", "weight", "delta_weight", "burden"] 
                        idx += ["last_time", "last_3f", "horse_qine_raito", "jockey_qine_raito"]
                        sr = pd.Series(data, index=idx)
                        print(name, result_time)
                        srs.append(sr)

    filename = "./data/" + "april_test.pickle"
    with open(filename, "wb") as f:
        pickle.dump(srs, f, pickle.HIGHEST_PROTOCOL)

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