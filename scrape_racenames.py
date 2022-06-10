ua = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.57"}
from bs4 import BeautifulSoup
from datetime import datetime
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

    filename = "./data/" + "racenames_2022.pickle"
    with open(filename, "rb") as f:
        read_data = pickle.load(f)

    s = lambda i: str(i).rjust(2, "0")
    races = []
    # races += [(f"01{s(i)}", "川崎", f"11{s(i)}") for i in range(1, 5)]
    # races += [(f"01{s(i)}", "川崎", f"11{s(i-1)}") for i in range(6, 8)] # 雪で8Rから中止
    # races += [(f"01{s(i+9)}", "船橋", f"10{s(i)}") for i in range(1, 6)]
    # races += [(f"01{s(i+16)}", "浦和", f"11{s(i)}") for i in range(1, 6)]
    # races += [(f"01{s(i+23)}", "大井", f"16{s(i)}") for i in range(1, 6)]
    # races += [(f"01{s(i+30)}", "川崎", f"12{s(i)}") for i in range(1, 2)]
    # races += [(f"02{s(i-1)}", "川崎", f"12{s(i)}") for i in range(2, 6)]
    # races += [(f"02{s(i+6)}", "大井", f"17{s(i)}") for i in range(1, 6)]
    # races += [(f"02{s(i+13)}", "船橋", f"11{s(i)}") for i in range(1, 6)]
    # races += [(f"02{s(i+20)}", "浦和", f"12{s(i)}") for i in range(1, 6)]
    # races += [("0228", "川崎", "1301")]
    # races += [(f"03{s(i)}", "川崎", f"13{s(i+1)}") for i in range(1, 5)]
    # races += [(f"03{s(i+6)}", "大井", f"18{s(i)}") for i in range(1, 6)]
    # races += [(f"03{s(i+13)}", "浦和", f"13{s(i)}") for i in range(1, 6)]
    # races += [(f"03{s(i+20)}", "船橋", f"12{s(i)}") for i in range(1, 6)]
    # races += [(f"03{s(i+27)}", "大井", f"19{s(i)}") for i in range(1, 5)]
    # races += [("0401", "大井", "0101")] # コンディション不良で全て中止
    # races += [(f"04{s(i+3)}", "川崎", f"01{s(i)}") for i in range(1, 6)]
    # races += [(f"04{s(i+10)}", "船橋", f"01{s(i)}") for i in range(1, 6)]
    # races += [(f"04{s(i+17)}", "大井", f"02{s(i)}") for i in range(1, 6)]
    # races += [(f"04{s(i+24)}", "浦和", f"01{s(i)}") for i in range(1, 6)]
    # races += [(f"05{s(i+1)}", "船橋", f"02{s(i)}") for i in range(1, 6)]
    # races += [(f"05{s(i+8)}", "大井", f"03{s(i)}") for i in range(1, 6)]
    # races += [(f"05{s(i+15)}", "川崎", f"02{s(i)}") for i in range(1, 6)]
    # races += [(f"05{s(i+22)}", "大井", f"04{s(i)}") for i in range(1, 6)]
    races += [(f"05{s(i+29)}", "浦和", f"02{s(i)}") for i in range(1, 3)]
    races += [(f"06{s(i-2)}", "浦和", f"02{s(i)}") for i in range(3, 6)]

    data = []
    for i, (dt, course, hold) in enumerate(races):
        if i > -1:
            for race in (s(n) for n in range(1, 13)):
                target = dt + course_d[course] + hold + race

                result_url = nankan_url + "/result/" + yyyy + target + ".do"
                dfs = get_dfs(result_url)
                if not dfs: # レースなし
                    print(f"{df} {race}R no race...")
                    continue
                else:
                    df = dfs[0]
                    if not df.columns[0] == "着": # 結果なし
                        print(f"{dt} {race}R no result...")
                        continue

                info_url = nankan_url + "/race_info/" + yyyy + target + ".do"
                soup = get_soup(info_url)
                dist_tag = soup.select_one("div#race-data01-a")
                dist = dist_tag.select_one("a").text.strip()
                entry_df = get_dfs(info_url)[0]

                result_url = nankan_url + "/result/" + yyyy + target + ".do"
                dfs = get_dfs(result_url)
                df = [df for df in dfs if df.columns[0] == "天候"][0]
                condition = df["天候"][0] + "/" + df["馬場"][0].split()[1]

                racename = course + " " + race + "R " + soup.select_one("span.race-name").text
                racename += " " + dist + " " + str(len(entry_df)) + "頭 " + condition
                racename += " " + target
                
                print(racename)
                data.append(racename)

                # m = re.match("Ｃ３\(", racename.split()[2])

                # odds_url = nankan_url + "/odds/" + yyyy + target + "01.do"
                # odds_dfs = get_dfs(odds_url)
                # odds_df = [df for df in odds_dfs if df.co lumns[0] == "枠番"][0]
        
    # filename = "./data/" + "racenames_22.pickle"
    # with open(filename, "wb") as f:
    #     pickle.dump(races, f, pickle.HIGHEST_PROTOCOL)

    # https://returnofthecaferacers.com/kawasaki-cafe-racer/the-saint-kawasaki-w800/
    new_data = read_data + data

    filename = "./data/" + "_racenames_2022.pickle"
    with open(filename, "wb") as f:
        pickle.dump(new_data, f, pickle.HIGHEST_PROTOCOL)
