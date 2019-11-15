import numpy as np
from sklearn.base import BaseEstimator


class MovingAverage(BaseEstimator):
    '''Implements a moving average.'''

    def __init__(self, truncate=True):
        self.truncate = truncate
        self.N = 0
        self.X = np.array([])
        self.forecast = np.array([])
        self.periods = 0

    def fit(self, X, N, periods=5):
        '''Implements a Moving Average forecast.'''
        try:
            # sets variables
            self.N = N
            self.X = X
            length = len(self.X)
            self.forecast = np.zeros((length + self.N,))
            self.periods = int(periods)
            # check history
            if length < self.periods:
                print('Moving Average: Not enough data for %s periods' % str(self.periods))
                return False
            # forecast
            self.forecast[:self.periods] = self.X[:self.periods]
            for i in range(self.periods, length + self.N):
                # ex-post
                if i <= length:
                    self.forecast[i] = self.X[i - self.periods:i].mean()
                # ex-ante
                else:
                    self.forecast[i] = self.forecast[i - 1]
            # truncate 0s
            if self.truncate:
                self.forecast[self.forecast < 0] = 0
            # set name
            return self

        except Exception as e:
            print('Error in Moving Average: ')
            raise Exception(e)

    def predict(self, first_date):
        return self.forecast[first_date:]


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    # arr = np.sin(np.arange(0,stop=36)*6*np.pi/36)
    arr = np.random.randint(0, 100, 36)
    b = np.random.choice(arr, size=20, replace=False)
    arr = np.array([i if i in b else 0 for i in arr])
    ma = MovingAverage()
    fitted = ma.fit(arr, 10)
    print(ma.predict(0))
    plt.plot(arr)
    plt.plot(ma.predict(0))
    plt.show()
