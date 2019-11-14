import numpy as np
from sklearn.base import BaseEstimator
# TODO: fix this

class ExponentialSmoothing(BaseEstimator):
    '''Implements a naiveLV forecast.'''

    def __init__(self, alpha=0.3, truncate=True):
        self.truncate = truncate
        self.alpha = alpha
        self.N = 0
        self.X = np.array([])
        self.forecast = np.array([])
        self.periods = 0

    def fit(self, X, N):
        '''Implements an exponential smoothing algorithm to generate forecast.'''
        try:
            # sets data
            self.X = X
            self.N = N
            # sets variables
            length = len(self.X)
            self.forecast = np.zeros((length + self.N,))
            # initialize
            self.forecast[0] = self.X[0]
            # forecast
            for i in range(1, length + self.N):
                # ex-post
                if i <= length:
                    self.forecast[i] = self.alpha * self.X[i] + (1 - self.alpha) * (self.forecast[i - 1])
                # ex-ante
                else:
                    self.forecast[i] = self.forecast[i - 1]
            # truncate 0s
            if self.truncate:
                self.forecast[self.forecast < 0] = 0
            return self

        except Exception as e:
            print('Error in expo smoothing: ')
            raise Exception(e)

    def predict(self, first_date):
        return self.forecast[first_date:]


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    arr = np.sin(np.arange(0,stop=36)*6*np.pi/36)
    # arr = np.random.randint(0, 100, 36)
    # b = np.random.choice(arr, size=20, replace=False)
    # arr = np.array([i if i in b else 0 for i in arr])
    es = ExponentialSmoothing()
    fitted = es.fit(arr, 5)
    print(es.predict(5))
    plt.plot(arr)
    plt.plot(es.predict(0))
    plt.show()
