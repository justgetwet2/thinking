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
        date = info_url[42:-11]
        racename = date + " " + course + " " + race + "R" + " " + title
        racename +=  " " + distance + " " + str(number_of_horses) + "頭"

        return racename

    races = april_races()
    # racenames = []
    data = []
    for i, (dt, course, hold) in enumerate(races):
        if i > -1:
            for race in (srj(n) for n in range(1, 13)):
                target = dt + course_d[course] + hold + race + ".do"
                info_url = nankan_url + "/race_info/" + yyyy + target
                racename = get_racename(info_url)
                is_dist = [d for d in ("1,400", "1,500", "1,600") if d in racename]
                if is_dist and "Ｃ" in racename:
                    print(racename)

                    entry_df = get_dfs(info_url)[0]

                    odds_url = nankan_url + "/odds/" + yyyy + target.strip(".do") + "01.do"
                    odds_dfs = get_dfs(odds_url)
                    odds_df = [df for df in odds_dfs if df.columns[0] == "枠番"][0]
                    
                    result_url = nankan_url + "/result/" + yyyy + target
                    
                    result_df = get_dfs(result_url)[0]

                    data.append((racename, entry_df, odds_df, result_df))

    #             racenames.append(racename)

    filename = "./data/" + "april_c.pickle"
    with open(filename, "wb") as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)