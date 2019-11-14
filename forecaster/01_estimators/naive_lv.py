import os
import pandas as pd
import numpy as np
import datetime
from sklearn.base import BaseEstimator


class NaiveLV(BaseEstimator):
    '''Implements a naiveLV forecast.'''

    def __init__(self, lag):
        self.lag = lag

    def fit(self, X, N):
        '''

        :param X: time series
        :param N: number of periods to predict
        :return: self
        '''
        self.N = N
        self.X = X
        length = len(X)
        self.forecast = np.zeros((length + self.N,))

        if length < self.lag:
            print('Naive LV: Not enough data')

            return False

        for i in range(0, length + self.N):
            if i >= self.lag:
                # ex-post
                if i <= length + self.lag - 1:
                    self.forecast[i] = X[i - self.lag]
                # ex-ante
                else:
                    self.forecast[i] = self.forecast[i - 1]

        return self

    def predict(self, first_date):
        return self.forecast[first_date:]


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    arr = np.sin(np.arange(0,stop=36)*6*np.pi/36)
    nv = NaiveLV(5)
    fitted = nv.fit(arr, 4)
    plt.plot(arr)
    plt.plot(nv.predict(0))
    plt.show()