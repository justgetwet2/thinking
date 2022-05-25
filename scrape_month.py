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

    s = lambda i: str(i).rjust(2, "0")
    # month = [("0401", "大井", "0101")] # 中止
    month = [(f"04{s(i+4)}", "川崎", f"01{s(i+1)}") for i in range(5)]
    month += [(f"04{s(i+11)}", "船橋", f"01{s(i+1)}") for i in range(5)]
    month += [(f"04{s(i+18)}", "大井", f"02{s(i+1)}") for i in range(5)]
    month += [(f"04{s(i+25)}", "浦和", f"01{s(i+1)}") for i in range(5)]
    # print(month)
    races = []
    for i, (dt, course, hold) in enumerate(month):
        if i > -1:
            for race in (s(n) for n in range(1, 13)):
                target = dt + course_d[course] + hold + race + ".do"
                info_url = nankan_url + "/race_info/2022" + target
                soup = get_soup(info_url)
                # print(soup)
                dist_tag = soup.select_one("div#race-data01-a")
                dist = dist_tag.select_one("a").text.strip()
                info_df = get_dfs(info_url)[0]
                racename = course + " " + race + "R" + " " + soup.select_one("span.race-name").text
                racename +=  " " + dist + " " + str(len(info_df)) + "頭"
                print(racename)
                odds_url = nankan_url + "/odds/2022" + target.strip(".do") + "01.do"
                odds_dfs = get_dfs(odds_url)
                odds_df = [df for df in odds_dfs if df.columns[0] == "枠番"][0]
                
                result_url = nankan_url + "/result/2022" + target
                # print(trio_ret)
                result_df = get_dfs(result_url)[0]

                dfs = get_dfs(result_url)
                df = dfs[-1]
                ret = [r["三連複.1"]for idx, r in df.iterrows() if idx == 1][0]
                trio_ret = re.sub(",|円", "", ret)

                races.append((racename, info_df, odds_df, result_df, trio_ret))
        
    filename = "./data/" + "april" + "_data.pickle"
    with open(filename, "wb") as f:
        pickle.dump(races, f, pickle.HIGHEST_PROTOCOL)