import pandas as pd

from shared.predictor import CellChargePredictor


def predict(model, data):
    df = pd.DataFrame(data)
    return model.predict(df).tolist()


def load(path):
    return CellChargePredictor.load(path)
