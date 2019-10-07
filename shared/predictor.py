import pickle

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from shared.exceptions import EvaluationError, FeaturesComputationError


class CellChargePredictor(Pipeline):
    """
    Model to predict if a user will use our platform to charge his cellphone.
    """

    def __init__(self):
        pipeline = [
            ('standardscaler', StandardScaler()),
            ('classifier', RandomForestClassifier()),
        ]
        super().__init__(pipeline)

    def evaluate(self, X_test, y_test):
        """
        Compute metrics on a trained model.
        `X_test` and `y_test` must be from the same domain as the train data.
        Returns a dict with metrics.
        """
        y_pred = self.predict(X_test)
        return classification_report(y_test, y_pred, output_dict=True)

    def serialize(self):
        """
        Serialize the current model instance into a bytes object.
        
        This object can be easily written to a file.
        
        """
        return pickle.dumps(self)

    def dump(self, output_path):
        """
        Utility to serialize the current model instance and save it to a file.
        
        """
        with open(output_path, 'wb') as out_file:
            pickle.dump(self, out_file)
            
    @classmethod
    def load(cls, dumped_instance):
        """
        Retrieve a serialized model instance from a file.
        
        """
        return pickle.load(open(dumped_instance, "rb"))