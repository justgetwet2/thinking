import datetime
import pandas as pd
import pickle
import re


filepath = "./data/" + "test_2022.pickle"
with open(filepath, "rb") as f:
    races = pickle.load(f)

l = [race for race in races if race[0] == "06/24"]
for race in l:
    print(race[:-1])
