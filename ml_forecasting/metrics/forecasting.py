import numpy as np

epsilon = 1e-10


def percentage_error(y: np.ndarray, yhat: np.ndarray):
    """
    Percentage error
    Nota: El resultado NO esta multiplicado por 100
    """
    return (y - yhat) / (y + epsilon)


def mse(y: np.ndarray, yhat: np.ndarray):
    """ Mean Squared Error """
    return np.mean(np.square(y - yhat))


def rmse(y: np.ndarray, yhat: np.ndarray):
    """ Root Mean Squared Error """
    return np.sqrt(mse(y, yhat))


def nrmse(y: np.ndarray, yhat: np.ndarray):
    """ Normalized Root Mean Squared Error """
    return rmse(y, yhat) / (y.max() - y.min())


def me(y: np.ndarray, yhat: np.ndarray):
    """ Mean Error """
    return np.mean(y - yhat)


def mape(y: np.ndarray, yhat: np.ndarray):
    """
    Mean Absolute Percentage Error
    
    Propiedades:
        + Facil de interpretar
        + Independiente de la escala
        - No es simetrica
        - No esta definida cuando y[t] == 0
        - NO es muy buena para series intermitentes
    """
    return np.mean(np.abs(percentage_error(y, yhat)))


def smape(y: np.ndarray, yhat: np.ndarray):
    """ Symmetric Mean Absolute Percentage Error 
    
    Propiedades:
        + Facil de interpretar
        + Independiente de la escala
        - No esta definida cuando y[t] == 0
    
    """
    return np.mean(2.0 * np.abs(y - yhat) / ((np.abs(y) + np.abs(yhat)) + epsilon))


def smdape(y: np.ndarray, yhat: np.ndarray):
    """ Symmetric Median Absolute Percentage Error """
    return np.median(2.0 * np.abs(y - yhat) / ((np.abs(y) + np.abs(yhat)) + epsilon))


def wmape(y: np.array, yhat: np.array, w=None):
    """"
    weighted mape
    
    Propiedades:
        + Facil de intepretar
        + No la afectan tanto las series intermitentes
        - No esta definida cuando y[t] == 0
    """
    if w is None:
        w = np.ones(y.shape[0])
    mape_vector = w * np.abs(y-yhat)
    weighted_mape_vector = w * mape_vector
    return weighted_mape_vector.sum(axis=0)/np.dot(w, y)


def mae(y: np.array, yhat: np.array):
    """ Mean Absolute Error """
    return np.mean(np.abs(y - yhat))


def mase(y: np.array, yhat: np.array, seasonality=1):
    """ Mean Absolute Scaled Error """
    return mae(y, yhat) / mae(y[seasonality:], y[:-seasonality])


def smdape(y: np.array, yhat: np.array):
    """ Symmetric Median Absolute Percentage Error """
    return np.median(2.0 * np.abs(y - yhat) / ((np.abs(y) + np.abs(yhat)) + epsilon))


def wape(y: np.array, yhat: np.array):
    return wmape(y, yhat)
