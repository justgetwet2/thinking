import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pickle


if __name__ == "__main__":

    filepath = "./data/april_c.pickle"
    with open(filepath, mode="rb") as f:
        races = pickle.load(f)

    for race in races[:1]:
        df = race[1]
        for i, r in df.iterrows():
            # print(r)
            print(i+1, r[2].split()[0], r[6].split()[0])