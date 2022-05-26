
import matplotlib.pyplot as plt
import numpy as np
import pickle

if __name__ == "__main__":
    

    filepath = "./data/april_test.pickle"
    with open(filepath, mode="rb") as f:
        srs = pickle.load(f)

    def ftime(s):
        a, b = s.split(":")
        return int(a) * 60 + float(b)


    x, y = [], []
    for i, sr in enumerate(srs):
        if sr["condition"] == "稍重":
            result = sr["result"]
            lasttime = sr["last_time"]
            if result and lasttime:
                x.append(lasttime)
                y.append(result)

    # x = [d[0] for d in data]
    # print(set(x))

    plt.plot(x, y, ".")
    plt.show()