import os
import pandas as pd
import numpy as np
import datetime
from sklearn.base import BaseEstimator


class Croston(BaseEstimator):
    '''Implements a naiveLV forecast.'''

    def __init__(self, alpha=0.3, truncate=True):
        self.alpha = alpha
        self.truncate = truncate
        self.forecast = np.array([])

    def fit(self, X, N):
        # sets variables
        periods_with_data = X.size
        self.forecast = np.zeros((periods_with_data + N,))
        y = np.zeros((periods_with_data + N,))
        l = np.zeros((periods_with_data + N,))

        # initialize
        self.forecast[0] = X[0]
        l[0] = X[0]
        y[0] = 1
        q = 1
        # forecast
        for i in range(1, periods_with_data + N):
            # ex-post
            if i < periods_with_data:
                if X[i] <= 0:
                    l[i] = l[i - 1]
                    y[i] = y[i - 1]
                    q += 1
                else:
                    l[i] = (1 - self.alpha) * l[i - 1] + self.alpha * X[i]
                    y[i] = (1 - self.alpha) * y[i - 1] + self.alpha * q
                    q = 1
                self.forecast[i] = l[i] / y[i]
            # ex-ante
            else:
                self.forecast[i] = self.forecast[i - 1]
        # truncate 0s
        if self.truncate:
            self.forecast[self.forecast < 0] = 0

        return self

    def predict(self, first_date):
        return self.forecast[first_date:]


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    # arr = np.sin(np.arange(0,stop=36)*6*np.pi/36)
    arr = np.random.randint(0,100,36)
    b = np.random.choice(arr, size=20, replace=False)
    arr = np.array([i if i in b else 0 for i in arr])
    cr = Croston()
    fitted = cr.fit(arr, 4)
    print(cr.predict(5))
    plt.plot(arr)
    plt.plot(cr.predict(0))
    plt.show()