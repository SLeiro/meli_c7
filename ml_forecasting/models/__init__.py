from enum import Enum
from sklearn.base import BaseEstimator


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

    def predict(self, X):
        # THIS IS PSEUDO-CODE, JUST TO SHOW AN EXAMPLE OF THE IDEA!!
        return [self.predict_one(inventory, region, start, periods) for inventory, region, start, periods in X]
