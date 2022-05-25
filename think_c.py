import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pickle


if __name__ == "__main__":

    filepath = "./data/april_c.pickle"
    with open(filepath, mode="rb") as f:
        races = pickle.load(f)

    # print(pd.__version__)
    favs = []
    for i, (racename, entry_df, odds_df, result_df) in enumerate(races):
        # print(racename)
        if i > -1:
            odds_d = {}
            for idx, row in odds_df.iterrows():
                try:
                    odds = float(row["単勝"])
                    odds_d[row["馬番"]] = odds
                except:
                    pass
            # print(odds_d)        
            for idx, row in result_df.iterrows():
                if idx < 2:
                    umaban, fav = row["馬番"], int(row["人気"])# 人気 1.0
                    # winnings.append((umaban, row["馬名"], fav, odds_d[umaban])) 
                    favs.append(fav)
                    # print(umaban, row["馬名"], fav, odds_d[umaban])

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    ax.hist(favs, bins=50)
    ax.set_title('tri histogram')
    ax.set_xlabel('favorite')
    ax.set_ylabel('freq')
    plt.show()
