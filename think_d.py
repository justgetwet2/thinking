import datetime
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import pickle
import re


filename = "./data/c3_1500.pickle"
with open(filename, mode="rb") as f:
    srs = pickle.load(f)

print(" ".join(srs[0].index.to_list()))
print(srs[0].to_list(), "\n")

l = [sr.to_list()[1:-1:] for sr in srs if sr["time"]]
print(len(l))
y = np.array([v[0] for v in l])
x = np.array([v[-1] for v in l])

plt.plot(x, y, ".")
# plt.hist(y)
plt.show()