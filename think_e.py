import numpy as np
rng = np.random.default_rng()

invest = 0
payout = 0
bet = 10000
for _ in range(100000):
    invest += bet
    if rng.random() < 0.7:
        payout += bet * 1.6

rate = payout/invest
print(round(rate, 2))