import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pickle



def class_count(racenames):
    race_class = "２歳", "３歳", "Ｃ", "Ｂ", "Ａ", "Ｊｐｎ", "オープン",
    each_class = []
    for racename in racenames:
        found = False
        for i, c in enumerate(race_class):
            if c in racename:
                if not found:
                    each_class.append(i)
                    found = True

    print("length:", len(racenames), "->", len(each_class))
    srs = []
    for i in range(len(race_class)):
        items = race_class[i], each_class.count(i)
        sr = pd.Series(items, index=["Class", "Count"])
        srs.append(sr)
    
    pd.set_option('display.unicode.east_asian_width', True)
    df = pd.DataFrame(srs)
    print(df)

def dist_count(racenames):
    c_racenames = [name for name in racenames if "Ｃ" in name]
    print("length:", len(c_racenames))
    dist_l = []
    for racename in c_racenames:
        s_dist = racename.split()[-2].strip("ダ").split("m")[0]
        dist = int(s_dist.replace(",", ""))
        dist_l.append(dist)
    distance = sorted(set(dist_l))
    srs = []
    for dist in distance:
        items = dist, dist_l.count(dist)
        sr = pd.Series(items, index=("Distance", "Count"))
        srs.append(sr)
    
    df = pd.DataFrame(srs)
    print(df)

def trio_hist(races):
    winnings = []
    w = 0
    for i, (racename, entry_df, odds_df, result_df, ret) in enumerate(races):

        if i > -1:
            odds_d = {}
            for idx, row in odds_df.iterrows():
                try:
                    odds = float(row["単勝"])
                    odds_d[row["馬番"]] = odds
                except:
                    pass
            favs = []
            b = 0
            for idx, row in result_df.iterrows():
                if idx < 3:
                    umaban, fav = row["馬番"], int(row["人気"])# 人気 1.0
                    winnings.append((umaban, row["馬名"], fav, odds_d[umaban])) 
                    favs.append(fav)
                    if fav < 6:
                        b += 1
            if b > 2:
                w += int(ret)
            # print("-".join([str(f) for f in favs]), b > 2, ret)

    res = w / (len(races) * 1000)
    print(round(res, 1))

    favs = [w[2] for w in winnings]

    x = len([fav for fav in favs if fav < 7])
    t = len(favs)
    print(round(x/t, 3), round((t-x)/t, 3))

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    ax.hist(favs, bins=50)
    ax.set_title('first histogram $\mu=100,\ \sigma=15$')
    ax.set_xlabel('favorite')
    ax.set_ylabel('freq')
    plt.show()

if __name__ == "__main__":
    
    filepath = "./data/april_racenames.pickle"
    with open(filepath, mode="rb") as f:
        racenames = pickle.load(f)

    # trio_hist(races)
    # class_count(racenames)
    dist_count(racenames)