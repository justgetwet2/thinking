import datetime
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import pickle
import re
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


filename = "./data/c3_1500.pickle"
with open(filename, mode="rb") as f:
    srs = pickle.load(f)

print(" ".join(srs[0].index.to_list()))
print(srs[0].to_list(), "\n")

l = [sr.to_list()[1:-1:] for sr in srs if sr["time"] and sr["last3F"]]
print(len(l))
y = np.array([v[0] for v in l])
X = np.array([v[1:-1:] for v in l])

X_train, X_test, y_train, y_test = train_test_split(X, y)

model = LinearRegression()
model.fit(X_train, y_train)

print("intercept", model.intercept_)
print("train", model.score(X_train, y_train))
print("test", model.score(X_test, y_test))

x = model.predict(X_test)
# x = [x[-1] for x in X_test]

# plt.plot(x, y_test, ".")
# plt.hist(y)
# plt.show()