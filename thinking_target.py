
import matplotlib.pyplot as plt
import numpy as np
import pickle

if __name__ == "__main__":
    

    filepath = "./data/april_test.pickle"
    with open(filepath, mode="rb") as f:
        data = pickle.load(f)

    def ftime(s):
        a, b = s.split(":")
        return int(a) * 60 + float(b)


    x, y = [], []
    for d in data:
        print(d)
        if d[1] == "良" and not d[3] == "-" and not d[4] == "":
            print(d)
            # x.append(ftime(d[3]))
            # y.append(ftime(d[4]))

    # x = [d[0] for d in data]
    # print(set(x))

    # plt.plot(x, y, ".")
    # plt.show()