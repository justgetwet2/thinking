
import matplotlib.pyplot as plt
import numpy as np
import pickle
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

if __name__ == "__main__":
    

    filepath = "./data/april_test.pickle"
    with open(filepath, mode="rb") as f:
        srs = pickle.load(f)

    def ftime(s):
        a, b = s.split(":")
        return int(a) * 60 + float(b)


    X, y = [], []
    for i, sr in enumerate(srs):
        if sr["condition"]: # == "稍重":
            result = sr["result"]
            lasttime = sr["last_time"]
            if result and lasttime:
                l = sr[3:].to_list()
                # del l[8]
                # print(l)
                X.append(l[1:])
                y.append(l[0])

    X_train, X_test, y_train, y_test = train_test_split(X, y)
    
    model = LinearRegression()
    model.fit(X_train, y_train)

    print(model.intercept_)
    print(model.score(X_train, y_train))
    print(model.score(X_test, y_test))

    x = model.predict(X_test)
    # x = [a[7] for a in X_test]

    # x = [d[0] for d in data]
    # print(set(x))
    plt.plot(x, y_test, ".")
    plt.show()


# race                 0428 浦和 05R Ｃ３(三)(四) 800,000円 ダ1500m（外） 晴/良 10頭
# condition                                                          良
# horse_name                                                      セコイア
# result                                                          99.7
# num_horse                                                         10
# prize                                                         800000
# sex                                                                1
# age                                                                5
# weight                                                           467
# delta_weight                                                       5
# burden                                                          54.0
# last_time                                                       98.6
# last_3f                                                            0
# horse_qine_raito                                                19.4
# jockey_qine_raito                                                6.0