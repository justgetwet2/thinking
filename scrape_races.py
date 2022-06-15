ua = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.57"}
from bs4 import BeautifulSoup
import pandas as pd
import pickle
import re
import requests

def get_soup(url):
    try:
        res = requests.get(url, headers=ua)
    except requests.RequestException as e:
        print("Error: ", e)
    else:
        soup = BeautifulSoup(res.content, "html.parser")
        return soup

def get_dfs(url):
    dfs = []
    soup = get_soup(url)
    if soup:
        if soup.find("table"):
            dfs = pd.io.html.read_html(soup.prettify())
        else:
            print(f"It's no table! {url}")
    return dfs

def strj(x):
    return str(x).rjust(2, "0")
    
def race_tuples():
    races = []
    # races += [(f"01{strj(i)}", "川崎", f"11{strj(i)}") for i in range(1, 5)]
    # races += [(f"01{strj(i)}", "川崎", f"11{strj(i-1)}") for i in range(6, 8)] # 雪で8Rから中止
    # races += [(f"01{strj(i+9)}", "船橋", f"10{strj(i)}") for i in range(1, 6)]
    # races += [(f"01{strj(i+16)}", "浦和", f"11{strj(i)}") for i in range(1, 6)]
    # races += [(f"01{strj(i+23)}", "大井", f"16{strj(i)}") for i in range(1, 6)]
    # races += [(f"01{strj(i+30)}", "川崎", f"12{strj(i)}") for i in range(1, 2)]
    # races += [(f"02{strj(i-1)}", "川崎", f"12{strj(i)}") for i in range(2, 6)]
    # races += [(f"02{strj(i+6)}", "大井", f"17{strj(i)}") for i in range(1, 6)]
    # races += [(f"02{strj(i+13)}", "船橋", f"11{strj(i)}") for i in range(1, 6)]
    # races += [(f"02{strj(i+20)}", "浦和", f"12{strj(i)}") for i in range(1, 6)]
    # races += [("0228", "川崎", "1301")]
    # races += [(f"03{strj(i)}", "川崎", f"13{strj(i+1)}") for i in range(1, 5)]
    # races += [(f"03{strj(i+6)}", "大井", f"18{strj(i)}") for i in range(1, 6)]
    # races += [(f"03{strj(i+13)}", "浦和", f"13{strj(i)}") for i in range(1, 6)]
    # races += [(f"03{strj(i+20)}", "船橋", f"12{strj(i)}") for i in range(1, 6)]
    # races += [(f"03{strj(i+27)}", "大井", f"19{strj(i)}") for i in range(1, 5)]
    # races += [("0401", "大井", "0101")] # コンディション不良で全て中止
    # races += [(f"04{strj(i+3)}", "川崎", f"01{strj(i)}") for i in range(1, 6)]
    # races += [(f"04{strj(i+10)}", "船橋", f"01{strj(i)}") for i in range(1, 6)]
    # races += [(f"04{strj(i+17)}", "大井", f"02{strj(i)}") for i in range(1, 6)]
    # races += [(f"04{strj(i+24)}", "浦和", f"01{strj(i)}") for i in range(1, 6)]
    # races += [(f"05{strj(i+1)}", "船橋", f"02{strj(i)}") for i in range(1, 6)]
    # races += [(f"05{strj(i+8)}", "大井", f"03{strj(i)}") for i in range(1, 6)]
    # races += [(f"05{strj(i+15)}", "川崎", f"02{strj(i)}") for i in range(1, 6)]
    # races += [(f"05{strj(i+22)}", "大井", f"04{strj(i)}") for i in range(1, 6)]
    # races += [(f"05{strj(i+29)}", "浦和", f"02{strj(i)}") for i in range(1, 3)]
    # races += [(f"06{strj(i-2)}", "浦和", f"02{strj(i)}") for i in range(3, 6)]
    # races += [(f"06{strj(i+5)}", "大井", f"05{strj(i)}") for i in range(1,  6)]

    return races

if __name__ == "__main__":

    nankan_url =  "https://www.nankankeiba.com"
    yyyy = "2022"
    course_d = { "浦和": "18", "船橋": "19", "大井": "20", "川崎": "21" }

    filename = "./data/" + "races_2022.pickle"
    with open(filename, "rb") as f:
        read_data = pickle.load(f)

    races = race_tuples()

    data = []
    for i, (dt, course, hold) in enumerate(races):
        for n in range(1, 13):
            race = str(n).rjust(2, "0")
            target_code = dt + course_d[course] + hold + race

            result_url = nankan_url + "/result/" + yyyy + target_code + ".do"
            dfs = get_dfs(result_url)
            if not dfs: # レースなし
                print(f"{dt} {race}R is nothing..")
                continue
            else:
                df = dfs[0]
                if not df.columns[0] == "着": # 結果なし
                    print(f"{dt} {race}R has no result..")
                    continue
            df = [df for df in dfs if df.columns[0] == "天候"][0]
            condition = df["天候"][0] + "/" + df["馬場"][0].split()[1]

            raceno = course + " " + race + "R"

            info_url = nankan_url + "/race_info/" + yyyy + target_code + ".do"
            soup = get_soup(info_url)
            racename = soup.select_one("span.race-name").text
            racename = re.sub("\u3000", " ", racename).strip()

            tag = soup.select_one("div#race-data01-a")
            dist = tag.select_one("a").text.strip()
            dist = dist.strip("ダ")
            
            entry_df = get_dfs(info_url)[0]
            head_count = str(len(entry_df)) + "頭"
            
            t = dt, raceno, racename, dist, head_count, condition, target_code
            print(t)
            data.append(t)

    data = read_data + data

    filepath = "./data/" + "races_2022.pickle"
    with open(filepath, "wb") as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

