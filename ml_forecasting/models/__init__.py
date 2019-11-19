from enum import Enum
from sklearn.base import BaseEstimator
import numpy as np


class Frequency(Enum):
    Day = 'D'
    Week = 'W'
    Month = 'M'

    def __str__(self):
        return self.value


class Forecaster(BaseEstimator):
    """
    Forecasting model wrapper
    """

    def __init__(self, estimator, s_type, freq=Frequency.Week):
        """
        Generate an instance for a specific (series type, granularity)
        :param estimator: Algorithm to estimate a single time series (sklearn signature)
        :param s_type: Kind of series to predict
        :param freq: Granularity of the periods: Enum(D, W, M)
        """
        self.estimator = estimator
        self.s_type = s_type
        self.freq = freq
        self.models = {}
        self.series = None

    def _split_time_series(self, X):
        """
        This method groups by (inventory, region) and calculates aggregations
        :param X: DataFrame with ETL columns
        :return: Dict of DataFrames indexed by group id, with the following cols:
                    date: Date point with proper granularity
                    y: Real demand for this Date point
        """
        return {}

    def _clean_serie(self, serie, upper_percentile=0.9, lower_percentile=0.1, upper_k__factor=1.2,
                     lower_k_factor=1, seas_cleaning=True,
                     seas_superior=1.1, seas_inferior=0.9):
        '''Applies outlier correction algorithm to serie.'''
        try:
            # Smooths serie
            self._smooth_time_series(serie, 3, 3)
            # sets data
            x = serie
            s = self._smooth_time_series(serie, 3, 3)
            # sets variables
            length = len(x)
            min_data_points = 5
            # num data points
            c = np.zeros((length,))
            o = np.zeros((length,))
            # calculate percentiles
            lower_per = np.percentile(x[:length], lower_percentile * 100.0) * lower_k_factor
            upper_per = np.percentile(x[:length], upper_percentile * 100.0) * upper_k__factor
            # find outliers
            o = np.logical_or(x[:length] < lower_per, x[:length] > upper_per) * 1
            if seas_cleaning:
                # get seasonality
                seas, m_avg = self._get_seasonality(serie)
                if not isinstance(seas, bool):
                    # check if higher than seas
                    o = np.logical_or(m_avg > seas * seas_superior, m_avg < seas * seas_inferior,
                                      o == 1) * 1
            # apply cleaning
            for i in range(0, length):
                # outlier detected
                if o[i] == 1 and length > min_data_points:
                    # first value
                    if i == 0:
                        c[i] = (2 * (o[i + 1] * s[i + 1] + (1 - o[i + 1]) * x[i + 1]) + (
                                o[i + 2] * s[i + 2] + (1 - o[i + 2]) * x[i + 2])) / 3
                    # second value
                    elif i == 1:
                        c[i] = (2 * (o[i - 1] * s[i - 1] + (1 - o[i - 1]) * x[i - 1]) + 2 * (
                                o[i + 1] * s[i + 1] + (1 - o[i + 1]) * x[i + 1]) + (
                                        o[i + 2] * s[i + 2] + (1 - o[i + 2]) * x[i + 2])) / 5
                    # next to last values
                    elif i == length - 2:
                        c[i] = ((o[i - 2] * s[i - 2] + (1 - o[i - 2]) * x[i - 2]) + 2 * (
                                o[i - 1] * s[i - 1] + (1 - o[i - 1]) * x[i - 1]) + 2 * (
                                        o[i + 1] * s[i + 1] + (1 - o[i + 1]) * x[i + 1])) / 5
                    # last value
                    elif i == length - 1:
                        c[i] = ((o[i - 2] * s[i - 2] + (1 - o[i - 2]) * x[i - 2]) + 2 * (
                                o[i - 1] * s[i - 1] + (1 - o[i - 1]) * x[i - 1])) / 3
                    # middle values
                    else:
                        c[i] = ((o[i - 2] * s[i - 2] + (1 - o[i - 2]) * x[i - 2]) + 2 * (
                                o[i - 1] * s[i - 1] + (1 - o[i - 1]) * x[i - 1]) + 2 * (
                                        o[i + 1] * s[i + 1] + (1 - o[i + 1]) * x[i + 1]) + (
                                        o[i + 2] * s[i + 2] + (1 - o[i + 2]) * x[i + 2])) / 6
                # no outlier
                else:
                    c[i] = x[i]
            return c

        except Exception as e:
            print('Error in outlier correction: ')
            raise Exception(e)

    def _smooth_time_series(self, serie, max_ant=4, max_post=4):
        """
        This method smooths the time series
        :return: self
        """
        try:
            # sets data
            x = serie
            # sets variables
            length = x.size
            # num data points
            s = np.zeros((length,))
            # set smoothing params
            x = x.values
            # loop through serie points
            for i in range(length):
                # initialize params
                params = []
                left = 1
                right = 1
                # set smoothing pattern left side
                for j in range(max_ant + 1, 0, -1):
                    # check for edge condition
                    if i - j + 1 < 0 or i + j - (max_ant + 1) >= length:
                        continue
                    # ok
                    else:
                        params.append(max_ant + 2 - j)
                        left -= 1
                # set smoothing pattern right side
                for j in range(0, max_post):
                    # check for edge condition
                    if i - j + max_post < 0 or i + j >= length - 1:
                        continue
                    # ok
                    else:
                        params.append(max_post - j)
                        right += 1
                # numpyfy and apply to serie
                p = np.array(params)
                s[i] = sum(x[left + i:right + i] * p) / sum(p)
            return s

        except Exception as e:
            print('Error smoothing serie: ')
            raise Exception(e)

    def _get_seasonality(self, serie):
        '''Implements an exponential smoothing algorithm to generate forecast.'''
        try:
            # sets data
            x = serie
            # num data points
            length = len(x)
            # cycle length --> 52 for weekly based forecast
            c = 52
            # seasonality series
            m_avg = np.ones((length,))
            s = np.zeros((c,))
            # check history
            if serie.completeCycles < 2:
                print(('SL: Not enough data. FU: ')  # + serie.fu.__str__()))
                return False, False
            # complete cycles
            cc = length // c
            a = np.zeros((cc,))
            # start date
            sd = length - c * cc
            # calcultes averages
            for i in range(0, cc):
                start = sd + c * i
                end = sd + c * (i + 1)
                a[i] = x[start:end].mean()
            # check if some cycle has average 0
            for cycle_average in a:
                if cycle_average <= 0:
                    print('SL: Cycle average <= 0. FU: ')  # + serie.fu.__str__())
                    return False, False
            # calculates seasonality
            j = 0
            k = 0
            for i in range(sd, length):
                m_avg[i] = x[i] / a[k]
                s[j] += x[i] / a[k]
                j += 1
                if j == c:
                    k += 1
                    j = 0
            s = s / cc
            # normalize to sum cycle length
            s = s / sum(s) * c
            # stack
            seas = s[c - sd:]
            for i in range(cc):
                seas = np.hstack((seas, s))
            return seas, m_avg

        except Exception as e:
            print('Error in seasonality calculation: ')
            raise Exception(e)

    def fit(self, X, y=None):
        """
        This method must fit N estimators and save the instances.
        One model for each (inventory, region)
        :param X: DataFrame with ETL columns
        :param y: Real demand (must be None in our case)
        :return: Forecaster instance
        """
        # THIS IS PSEUDO-CODE, JUST TO SHOW AN EXAMPLE OF THE IDEA!!
        self.series = self._split_time_series(X)
        for ts in self.series:
            model = self.estimator.fit(ts, y)
            # ts.id must be (inventory, region) or the group by key
            self.models[ts.id] = model

        return self

    def predict_one(self, inventory, region, start, periods=1):
        """
        Generate forecasting for an inventory in a region
        :param inventory: Id which represents an (item, variation, seller)
        :param region: Geographical region to estimate
        :param start: Starting date point
        :param periods: Number of next periods to forecast from `start`
        :return: DataFrame with the following cols:
                    date: Date point with proper granularity
                    y_hat: Estimated demand for this Date point
                    y_lower: Estimated lower bound for y_hat
                    y_lower: Estimated upper bound for y_hat
        """
        df_out = None

        return df_out

    def predict(self, pairs_to_predict, periods, start):
        '''

        :param pairs_to_predict: list of pairs (inventory_id, region)
        :param periods: int. Number of next periods to forecast from `start`
        :param start: int. Starting date point
        :return:
        '''
        # THIS IS PSEUDO-CODE, JUST TO SHOW AN EXAMPLE OF THE IDEA!!
        forecasts = []
        for inventory, region in pairs_to_predict:
            forecast = self.models[(inventory, region)].predict(start)
            forecasts.append(forecast[:periods])

        return forecasts
