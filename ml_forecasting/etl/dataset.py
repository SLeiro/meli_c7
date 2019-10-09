import os
import warnings
import logging
import pathlib

import pandas as pd
import numpy as np

from datetime import timedelta, datetime

from ml_forecasting.config import required_cols

logger = logging.getLogger(__name__)


def date_parser(date_str):
    if pd.isnull(date_str):
        return None
    return np.datetime64(date_str)


class DataPreparation:

    # instead of a site, a configuration
    def __init__(self, config):
        """
        Create dataset from a CSV file.
        :param config: configuration to read csv.
        """
        self.configs = config
        self.types = self.configs['DTYPES']
        self.parse_dates = self.configs['PARSE_DATES']
        self.required_cols = required_cols(self.configs)

    def _is_data_file(self, filename):
        exists = False
        ext = ''

        if isinstance(filename, pathlib.Path):
            ext = filename.suffix
            exists = filename.exists()
        else:
            _, ext = os.path.splitext(filename)
            exists = os.path.exists(filename)

        return exists and ext == '.csv'

    def _read_csv_kwargs(self, cols=None):
        if cols:
            types = {k: v
                     for k, v in self.types.items()
                     if k in cols or k.lower() in cols}

            parse_dates = [x
                           for x in self.parse_dates
                           if x in cols or x.lower() in cols]
        else:
            types = self.types
            parse_dates = self.parse_dates

        return {'usecols': list(types.keys()),
                'dtype': types,
                'parse_dates': parse_dates,
                'date_parser': date_parser}

    def _read_csv(self, filename, **kwargs):
        df = pd.read_csv(filename, **kwargs)
        df.columns = df.columns.str.lower()
        return df

    def load_one(self, filename, cols=None, nrows=None):
        """
        Load dataset from the csv.
        """

        kwargs = self._read_csv_kwargs(cols)
        if nrows is not None:
            kwargs['nrows'] = nrows

        return self._read_csv(filename, **kwargs)

    def load(self, source, cols=None):
        """
        Load the dataset from the source csv.
        """
        frames = []
        for filename in source:

            # Maybe it should actually fail, or check existance before load?
            if not self._is_data_file(filename):
                warnings.warn('{filename} is not a data file'.format(filename=filename))
                continue

            df = self.load_one(filename, cols=cols)

            frames.append(df)

        df = pd.concat(frames, ignore_index=True)
        return df
