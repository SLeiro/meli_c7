import numpy as np
from pytest import approx

import ml_forecasting.metrics.forecasting as metrics


class TestMetrics:
    def test_mse(self):
        y = np.ones(10)
        yhat = np.zeros(10)
        result = metrics.mse(y, yhat)
        assert result == 1

    def test_rmse(self):
        y = np.random.randint(1, 500, 10)
        yhat = y + np.random.randint(-10, 10, 10)

        r1 = metrics.rmse(y, yhat)
        r2 = metrics.mse(y, yhat) ** .5

        assert approx(r1) == approx(r2)

    def test_nrmse(self):
        y = np.random.randint(1, 500, 10)
        yhat = y + np.random.randint(-10, 10, 10)

        r1 = metrics.nrmse(y, yhat)
        r2 = metrics.rmse(y, yhat) / (y.max() - y.min())

        assert approx(r1) == approx(r2)

    def test_me(self):
        y = np.ones(10)
        yhat = np.zeros(10)
        result = metrics.me(y, yhat)
        assert approx(result) == 1

    def test_mape(self):
        y = np.ones(3)
        yhat = np.array([1.5, 1.5, 1.5])
        result = metrics.mape(y, yhat)
        assert approx(result) == 0.5

    def test_smape(self):
        y = np.ones(3)
        yhat = np.array([1.5, 1.5, 1.5])
        result = metrics.smape(y, yhat)
        assert approx(result) == 0.4

    def test_smdape(self):
        y = np.ones(3)
        yhat = np.array([1.5, 1.5, 1.5])
        result = metrics.smdape(y, yhat)
        assert approx(result) == 0.4

    def test_wmape(self):
        y = np.ones(3)
        yhat = np.array([1.5, 1.5, 1.5])
        result = metrics.wmape(y, yhat)
        assert approx(result) == 0.5

    def test_mae(self):
        y = np.ones(3)
        yhat = np.array([1.5, 1.5, 1.5])
        result = metrics.mae(y, yhat)
        assert approx(result) == 0.5

    def test_mase(self):
        y = np.array([1,2,1])
        yhat = np.array([1.5, 1.5, 1.5])
        result = metrics.mase(y, yhat)
        assert approx(result) == 0.5
