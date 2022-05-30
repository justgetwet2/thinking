import datetime
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import pickle
import re


filename = "./data/c3_1500.pickle"
with open(filename, mode="rb") as f:
    s = pickle.load(f)

print(s[0])