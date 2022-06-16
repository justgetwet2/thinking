import pickle

filename = "./data/" + "races_2022.pickle"
with open(filename, "rb") as f:
    races = pickle.load(f)

print(len(races))
print(races[0])
print(races[-1])

# new_races = []
# for i, race in enumerate(races):
#     # if i: continue
#     dt = race[0]
#     dt = dt[:2] + "/" + dt[2:]
#     c, r = race[1].split()
#     new_race = (dt, c, r) + race[2:]
#     new_races.append(new_race)

# filename = "./data/" + "races_2022.pickle"
# with open(filename, "wb") as f:
#     pickle.dump(new_races, f, pickle.HIGHEST_PROTOCOL)
