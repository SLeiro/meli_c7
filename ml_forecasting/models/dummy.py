from sklearn.base import BaseEstimator


class Dummy(BaseEstimator):
    """
    Dummy model to test the interface
    """
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X

    def predict(self, X, y=None):
        return X
