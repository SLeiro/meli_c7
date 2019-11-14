from sklearn.base import BaseEstimator


class movingAverage(BaseEstimator):
    '''Implements a moving average.'''

    def __init__(self, lag):
        self.lag = lag

def movingAverage(self, periods=5):
    '''Implements a naiveLV forecast.'''
    try:
        # sets data
        x = self.data['Values']
        d = self.data.index
        # sets variables
        N = x.size
        f = np.zeros((N,))
        p = int(periods)
        # check history
        if self.length < p:
            print('Moving Average: Not enough data for %s periods' % str(p))
            return False
        # forecast
        f[0:p] = x[0:p]
        for i in range(p, N):
            # ex-post
            if d[i] <= self.maxDate:
                f[i] = x[i - p:i].mean()
            # ex-ante
            else:
                f[i] = f[i - 1]
        # truncate 0s
        if self.truncate:
            f[f < 0] = 0
        # set name
        colName = 'Moving Average %s' % p
        # add to data
        self.data[colName] = f
        return True

    except Exception, e:
        self.raiseError('Error in Moving Average: ' + str(e))