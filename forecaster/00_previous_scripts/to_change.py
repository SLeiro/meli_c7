# Python Modules
import os
import pandas as pd
import numpy as np
import statsmodels.formula.api as sm
import statsmodels.tools.tools as sm_tools
import datetime
from dateutil.relativedelta import relativedelta
# SQL
# User Modules


class Serie():
    '''Instances Serie Object
    fu: FU instance

    '''
    # Forecast Settings

    fcstLag = 1

    def __init__(self, fu, dbName, dataTable, outputTable = None, kbiTable = None, timeInterval='month', \
                 truncate=True, maxDate=None, logger=None, warning_logger = None, django = False,
                 forecast_serie = False, fecha0 = None, fwdLags = 18, schema = None):
        '''Variables needed for Functions and DAO'''
        # Base Path
        self.basePath = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        # Sets logger
        self.logger = logger
        self.warning_logger = warning_logger
        # DB Variables
        self.dbName = dbName
        self.dataTable = dataTable
        self.outputTable = outputTable
        self.kbiTable = kbiTable
        # Loads Functions
        Functions.__init__(self,'Forecastia', self.dbName)

        # sets fu
        self.fu = fu
        # Initializes

        # loads data
        self.original_data = self.get_series_data(django, schema)
        # adds column with original values
        self.original_data['Original Values'] = self.original_data['Values']

        # sets variables
        self.truncate = truncate
        self.timeInterval = timeInterval
        self.forecast_serie = forecast_serie
        self.fecha0 = fecha0
        self.fwdLags = fwdLags
        # sets other variables
        self.setOtherProperties(maxDate, timeInterval=timeInterval)

        # Initialization Behavior
        self.innovation = False
        self.seasonality = False
        self.trend = False
        self.volatility = False
        self.sparsity = False
        # model
        self.model_name = None
        self.model_kwargs = {}

    ''' ---------------------------------------------- '''
    ''' DB FUNCTIONS '''
    ''' ---------------------------------------------- '''

    def get_series_data(self, django = False, schema=None):
        '''Returns DF with series.'''
        try:
            if django:
                data = list(self.dataTable.objects.filter(fu = self.fu).
                                       values('fu', 'time', 'fecha', 'valor'))
                cols = ['fu', 'time', 'fecha', 'valor']
                df = pd.DataFrame(data, columns=cols)
            else:
                sql = select([self.dataTable.uvin_fu_id, self.dataTable.uvin_ti_id,
                              self.dataTable.uvin_fecha, self.dataTable.uvin_valor]).where(
                    self.dataTable.fu == self.fu
                ).order_by(
                    self.dataTable.uvin_fecha
                )
                with self.engine.connect() as conn:
                    conn.execute("SET search_path TO " + schema + "")
                    df = pd.read_sql(sql, conn)
                df.columns = ['FU', 'Time ID', 'Fecha', 'Values']
            return df
        except Exception, e:
            self.raiseError('Error fetching series data: ' + str(e))

    def upload_series_data(self):
        '''Uploads DF with series data'''
        try:
            df = self.data.copy()
            cols = [str(col).replace(str(self.outputTable.__tablename__) + '.', '') for col in self.outputTable.__table__.columns]
            df.columns = cols
            df.to_sql(self.outputTable.__tablename__, self.engine, if_exists = 'append', index = False, schema = 'cleaner')
            return
        except Exception as e:
            self.raiseError('Error uploading Serie: ' + str(e))

    def upload_kbi_data(self):
        '''Uploads DF with KBI data'''
        try:
            with self.engine.connect() as conn:
                conn.execute("SET search_path TO analyzer")
                cols = ['fukbi_fu_id', 'fukbi_kbi_id', 'fukbi_valor']
                df = self.kbis.copy()
                df = df.drop('kbi_nombre', axis = 1)
                df.columns = cols
                df.to_sql('a01_fu_kbi', conn, if_exists='append', index=False)
            return
        except Exception as e:
            print (e)
            self.raiseError('Error uploading KBI: ' + str(e))

    def upload_forecast_data(self):
        '''Uploads DF with KBI data'''
        try:
            with self.engine.connect() as conn:
                conn.execute("SET search_path TO analyzer")
                df = self.forecast.copy()
                cols = ['uvout_fu_id', 'uvout_ti_id', 'uvout_fecha', 'uvout_valor', 'uvout_lag']
                df.columns = cols
                df.to_sql('a01_uv_out', conn, if_exists='append', index=False)
            return
        except Exception as e:
            self.raiseError('Error uploading Analyzer Output: ' + str(e))


    ''' ---------------------------------------------- '''
    ''' HELPER FUNCTIONS '''
    ''' ---------------------------------------------- '''

    def setOtherProperties(self, maxDate=None, timeInterval='month'):
        '''Sets other variables.'''
        try:
            # ok to run
            self.ok_to_run = True
            # data
            self.data = self.original_data.copy()
            # max date
            self.setMaxDate(maxDate)
            if not self.ok_to_run:
                return
            # series length
            self.setSeriesLength()
            # cycle length
            self.setCycleLength(timeInterval=timeInterval)
            # complete cycles
            self.setCompleteCycles()
            # cycles
            self.setSeriesCycles()
            return
        except Exception, e:
            self.raiseError('Error setting variables: ' + str(e))

    def setMaxDate(self, maxDate=None):
        '''Sets series max date and lags.'''
        try:
            # Checks if data available
            if len(self.data) == 0:
                print('No data available. FU: ' + self.fu.__str__())
                self.ok_to_run = False
                return False
            # initial set up
            if maxDate == None:
                self.maxDate = max(self.data.index)
            # checks if min date available and changes flag to false
            elif min(self.data.index) > maxDate:
                print('Not enough history to run forecast with max date '
                                            + str(maxDate) + '. FU: ' + self.fu.__str__())
                self.ok_to_run = False
            else:
                self.maxDate = maxDate

            # Compares dates id's
            if self.forecast_serie:
                # Add ceros up to fecha0
                while int(self.data.loc[self.maxDate, 'Time ID']) < int(self.fecha0):
                    newDate = self.maxDate + 1
                    fu = self.fu.fu_id
                    ti = self.data.loc[newDate - 1, 'Time ID'] + 1
                    fecha = self.data.loc[newDate - 1, 'Fecha']
                    if self.timeInterval == 'month':
                        fecha += relativedelta(months=1)
                    elif self.timeInterval == 'week':
                        fecha += relativedelta(weeks=1)
                    self.data.loc[newDate] = [fu, ti, fecha, 0, 0]
                    self.maxDate = newDate
                # Set lags
                self.lags = []
                # adds dates to data for forecast
                for lag in xrange(self.fwdLags):
                    newDate = self.maxDate + (lag + 1)
                    self.lags.append(lag + 1)
                    # checks if date exists
                    if newDate not in self.data.index:
                        fu = self.fu.fu_id
                        ti = self.data.loc[newDate - 1, 'Time ID'] + 1
                        fecha = self.data.loc[newDate - 1, 'Fecha']
                        if self.timeInterval == 'month':
                            fecha += relativedelta(months=1)
                        elif self.timeInterval == 'week':
                            fecha += relativedelta(weeks=1)
                        self.data.loc[newDate] = [fu, ti, fecha, None, None]

            return True
        except Exception, e:
            print (e)
            self.raiseError('Error setting maximum date: ' + str(e))

    ''' ---------------------------------------------- '''
    ''' ESSENTIALS '''
    ''' ---------------------------------------------- '''

    def setSeriesLength(self):
        try:
            # sets data
            d = self.data.index
            # num data points
            self.length = d[d <= self.maxDate].size
            return self.length
        except Exception, e:
            self.raiseError('Error in series length: ' + str(e))

    def setCycleLength(self, timeInterval='month'):
        try:
            # cycleLength
            if timeInterval == 'month':
                self.cycleLength = 12
            elif timeInterval == 'week':
                self.cycleLength = 52
            else:
                raise ValueError('Error setting time interval.')

            return self.cycleLength
        except Exception, e:
            self.raiseError('Error in cycle length: ' + str(e))

    def setCompleteCycles(self):
        try:
            # completeCycles
            self.completeCycles = self.length / self.cycleLength
            return self.completeCycles
        except Exception, e:
            self.raiseError('Error in complete cycles: ' + str(e))

    def setSeriesCycles(self):
        try:
            # total cycles
            self.seriesCycles = float(self.length) / float(self.cycleLength)
            return self.seriesCycles
        except Exception, e:
            self.raiseError('Error setting cycles: ' + str(e))

    ''' ---------------------------------------------- '''
    ''' TIME SERIES '''
    ''' ---------------------------------------------- '''
    ''' ---------------------------------------------- '''
    ''' General '''
    ''' ---------------------------------------------- '''
    def run_forecast(self):
        if self.model_name != None:
            # Get forecast function
            model = getattr(self, self.model_name)
            # Run
            model(**self.model_kwargs)
            return True
        else:
            self.raiseError('No model selected!')

    def make_forecast(self):
        '''Makes forecast DF from self.data'''
        try:
            # gets dates
            d = self.data.index
            # creates forecast
            self.forecast = self.data[d > self.maxDate]
            for colName in self.forecast.columns:
                if 'Values' in colName:
                    self.forecast = self.forecast.drop(colName, axis=1)
            # adds lags
            self.forecast['Lag'] = self.lags
            return True
        except Exception, e:
            self.raiseError('Error making forecast DF:' + str(e))
    ''' ---------------------------------------------- '''
    ''' CONSTANT MODELS '''
    ''' ---------------------------------------------- '''

    def naiveLV(self, lag=None):
        '''Implements a naiveLV forecast.'''
        try:
            # sets data
            x = self.data['Values']
            d = self.data.index
            # sets variables
            N = x.size
            f = np.zeros((N,))
            # sets lag
            if lag == None:
                lag = self.fcstLag
            # Check data
            if self.length < lag:
                print('Naive LV: Not enough data')
                return False
            # forecast
            for i in range(0, N):
                if i >= lag:
                    # ex-post
                    if i <= self.length + lag - 1:
                        f[i] = x[i - lag]
                    # ex-ante
                    else:
                        f[i] = f[i - 1]
            # truncate 0s
            if self.truncate:
                f[f < 0] = 0
            # set name
            colName = 'Naive LV'
            # add to data
            self.data[colName] = f
            return True

        except Exception, e:
            self.raiseError('Error in naive LV: ' + str(e))

    def naiveLY(self, cycleLength=None):
        '''Implements a naiveLV forecast.'''
        try:
            # sets data
            x = self.data['Values']
            d = self.data.index
            # sets variables
            N = x.size
            f = np.zeros((N,))
            # cycle lngth
            if cycleLength == None:
                c = self.cycleLength
            else:
                c = cycleLength
            # check history
            if self.completeCycles < 1:
                print('Naive LY: Not enough data')
                return False
            # forecast
            for i in range(0, N):
                # ex-post
                if d[i] <= self.maxDate:
                    f[i] = x[i]
                # ex-ante
                else:
                    f[i] = f[i - c]
            # truncate 0s
            if self.truncate:
                f[f < 0] = 0
            # set name
            colName = 'Naive LY'
            # add to data
            self.data[colName] = f
            return True

        except Exception, e:
            self.raiseError('Error in naive LY: ' + str(e))

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

    def expoSmoothing(self, alpha=0.3):
        '''Implements an exponential smoothing algorithm to generate forecast.'''
        try:
            # sets data
            x = self.data['Values']
            d = self.data.index
            # sets variables
            N = x.size
            f = np.zeros((N,))
            # initialize
            f[0] = x[0]
            # forecast
            for i in range(1, N):
                # ex-post
                if d[i] <= self.maxDate:
                    f[i] = alpha * x[i] + (1 - alpha) * (f[i - 1])
                # ex-ante
                else:
                    f[i] = f[i - 1]
            # truncate 0s
            if self.truncate:
                f[f < 0] = 0
            # set name
            colName = 'Expo %s' % str(alpha)
            # add to data
            self.data[colName] = f
            return True

        except Exception, e:
            self.raiseError('Error in expo smoothing: ' + str(e))

    def croston(self, alpha=0.3):
        '''Implements an croston smoothing algorithm to generate forecast.'''
        try:
            # sets data
            x = self.data['Values']
            d = self.data.index
            # sets variables
            N = x.size
            f = np.zeros((N,))
            y = np.zeros((N,))
            l = np.zeros((N,))

            # initialize
            f[0] = x[0]
            l[0] = x[0]
            y[0] = 1
            q = 1
            # forecast
            for i in range(1, N):
                # ex-post
                if d[i] <= self.maxDate:
                    if x[i] <= 0:
                        l[i] = l[i - 1]
                        y[i] = y[i - 1]
                        q += 1
                    else:
                        l[i] = (1 - alpha) * l[i - 1] + alpha * x[i]
                        y[i] = (1 - alpha) * y[i - 1] + alpha * q
                        q = 1
                    f[i] = l[i] / y[i]
                # ex-ante
                else:
                    f[i] = f[i - 1]
            # truncate 0s
            if self.truncate:
                f[f < 0] = 0
            # set name
            colName = 'Croston %s' % str(alpha)
            # add to data
            self.data[colName] = f
            return True

        except Exception, e:
            self.raiseError('Error in croston: ' + str(e))

    ''' ---------------------------------------------- '''
    ''' TREND MODELS '''
    ''' ---------------------------------------------- '''
    def holt(self, alpha=0.3, beta=0.1):
        '''Implements an exponential smoothing algorithm to generate forecast.'''
        try:
            # sets data
            x = self.data['Values']
            d = self.data.index
            # sets variables
            N = x.size
            f = np.zeros((N,))
            l = np.zeros((N,))
            t = np.zeros((N,))
            # checks history
            if self.length <= 3:
                print("Holt's: Not enough data")
                return False
            # initialize
            t[2] = (x[2] - x[0]) / 2
            l[2] = x[0:3].mean() + t[2]
            # forecast
            for i in range(3, N):
                # ex-post
                if d[i] <= self.maxDate:
                    l[i] = alpha * x[i] + (1 - alpha) * (l[i - 1] + t[i - 1])
                    t[i] = beta * (l[i] - l[i - 1]) + (1 - beta) * t[i - 1]
                    f[i] = l[i] + t[i]
                    j = i
                # ex-ante
                else:
                    f[i] = l[j] + (i - j) * t[j]
            # truncate 0s
            if self.truncate:
                f[f < 0] = 0
            # set name
            colName = 'Holts a=%s b=%s' % (str(alpha), str(beta))
            # add to data
            self.data[colName] = f
            return True

        except Exception, e:
            self.raiseError("Error in Holt's: " + str(e))

    def linearRegression(self):
        '''Implements an exponential smoothing algorithm to generate forecast.'''
        try:
            # sets data
            x = self.data['Values']
            d = self.data.index
            # sets variables
            N = x.size
            M = self.length
            f = np.zeros((N,))

            z = [i + 1 for i in xrange(N)]
            z = np.array(z)

            # initialize
            z = sm_tools.add_constant(z)
            model = sm.OLS(x[:M], z[:M], missing='drop')
            results = model.fit()
            params = results.params.values
            # forecast
            for i in range(0, N):
                f[i] = sum(z[i] * params)
            # truncate 0s
            if self.truncate:
                f[f < 0] = 0
            # set name
            colName = 'Linear Regression'
            # add to data
            self.data[colName] = f
            return True

        except Exception, e:
            self.raiseError("Error in Linear Regression: " + str(e))

    ''' ---------------------------------------------- '''
    ''' SEASONAL MODELS '''
    ''' ---------------------------------------------- '''
    def winter(self, alpha=0.3, gamma=0.5, cycleLength=None):
        '''Implements an exponential smoothing algorithm to generate forecast.'''
        try:
            # sets data
            x = self.data['Values']
            d = self.data.index
            # sets variables
            N = x.size
            f = np.zeros((N,))
            l = np.zeros((N,))
            s = np.zeros((N,))
            # cycle lngth
            if cycleLength == None:
                c = self.cycleLength
            else:
                c = cycleLength
            # checks history
            if self.completeCycles < 2:
                print("Winter's: Not enough data")
                return False
            # initialize
            l[0:c + 1] = x[0:c + 1].mean()
            for i in range(0, c):
                if x[i] <= 0.0:
                    s[i] = 1
                else:
                    s[i] = x[i] / l[i]
            s[c] = (1 - gamma) * s[0] + gamma * x[c] / l[c]
            # forecast
            for i in range(c + 1, N):
                # ex-post
                if d[i] <= self.maxDate:
                    l[i] = alpha * x[i - 1] / s[i - 1] + (1 - alpha) * l[i - 1]
                    s[i] = (1 - gamma) * s[i - c] + gamma * x[i] / l[i]

                # ex-ante
                else:
                    l[i] = l[i - 1]
                    s[i] = s[i - c]

                f[i] = l[i] * s[i]
            # truncate 0s
            if self.truncate:
                f[f < 0] = 0
            # set name
            colName = 'Winters a=%s g=%s' % (str(alpha), str(gamma))
            # add to data
            self.data[colName] = f
            return True

        except Exception, e:
            self.raiseError("Error in Winter's: " + str(e))

    ''' ---------------------------------------------- '''
    ''' SEASONAL TREND MODELS '''
    ''' ---------------------------------------------- '''
    def holtWinter(self, alpha=0.3, beta=0.1, gamma=0.5, cycleLength=None):
        '''Implements an exponential smoothing algorithm to generate forecast.'''
        try:
            # sets data
            x = self.data['Values']
            d = self.data.index
            # sets variables
            N = x.size
            f = np.zeros((N,))
            l = np.zeros((N,))
            t = np.zeros((N,))
            s = np.zeros((N,))
            # cycle lngth
            if cycleLength == None:
                c = self.cycleLength
            else:
                c = cycleLength
            # check history
            if self.completeCycles < 2:
                print("Holt Winter's: Not enough data")
                return False
            # initialize
            t[c + 3] = (x[c:c + 3].sum() - x[0:3].sum()) / (3 * c)
            l[c + 3] = x[3:c + 3].mean() + (c - 1) / 2.0 * t[c + 3]
            for i in range(3, c + 3):
                if x[i] <= 0.0:
                    s[i] = 1
                else:
                    s[i] = x[i] / (l[c + 3] - t[c + 3] * (c - i + 2.0))

            s[c + 3] = (1 - gamma) * s[3] + gamma * x[c + 3] / l[c + 3]
            # forecast
            for i in range(c + 4, N):
                # ex-post
                if d[i] <= self.maxDate:
                    l[i] = alpha * x[i] / s[i - c] + (1 - alpha) * (l[i - 1] + t[i - 1])
                    t[i] = beta * (l[i] - l[i - 1]) + (1 - beta) * t[i - 1]
                    s[i] = (1 - gamma) * s[i - c] + gamma * x[i] / l[i]
                    f[i] = (l[i] + t[i]) * s[i]
                    j = i

                # ex-ante
                else:
                    l[i] = l[i - 1]
                    t[i] = t[i - 1]
                    s[i] = s[i - c]
                    f[i] = (l[i] + (i - j) * t[i]) * s[i]

            # truncate 0s
            if self.truncate:
                f[f < 0] = 0
            # set name
            colName = 'Holt Winters a=%s b=%s g=%s' % (str(alpha), str(beta), str(gamma))
            # add to data
            self.data[colName] = f
            return True

        except Exception, e:
            self.raiseError("Error in Holt Winter's:" + str(e))


    def seasonalLinearRegression(self, cycleLength=None):
        '''Implements an exponential smoothing algorithm to generate forecast.'''
        try:
            # sets data
            x = self.data['Values']
            d = self.data.index
            # sets variables
            N = x.size
            # num data points
            M = self.length

            # cycle lngth
            if cycleLength == None:
                c = self.cycleLength
            else:
                c = cycleLength
            # check history
            if self.completeCycles < 2:
                print('SL: Not enough data')
                return False
            y = np.zeros((M,))
            # regresor series
            z = [i + 1 for i in xrange(N)]
            z = np.array(z)
            f = np.zeros((N,))
            s = np.zeros((c,))
            # complete cycles
            cc = self.completeCycles
            a = np.zeros((cc,))
            # start date
            sd = M - c * cc
            # start seasonality
            if c - sd == 12:
                ss = 0
            else:
                ss = c - sd
            # calcultes averages
            for i in range(0, cc):
                start = sd + c * i
                end = sd + c * (i + 1)
                a[i] = x[start:end].mean()
            # check if some cycle has average 0
            for cycle_average in a:
                if cycle_average <= 0:
                    print('SL: Cycle average <= 0')
                    return False
            # calculates seasonality
            j = 0
            k = 0
            for i in range(sd, M):
                s[j] += x[i] / a[k]
                j += 1
                if j == c:
                    k += 1
                    j = 0
            s = s / cc
            # calculates deseasonalized data
            j = ss
            for i in range(0, M):
                if s[j] == 0:
                    y[i] = 0
                else:
                    y[i] = x[i] / s[j]
                j += 1
                if j == c:
                    j = 0
            # initialize
            z = sm_tools.add_constant(z)
            model = sm.OLS(y, z[:M], missing='drop')
            results = model.fit()
            params = results.params
            # forecast
            j = ss
            for i in range(0, N):
                f[i] = sum(z[i] * params) * s[j]
                j += 1
                if j == c:
                    j = 0
            # truncate 0s
            if self.truncate:
                f[f < 0] = 0
            # set name
            colName = 'Seasonal Linear Regression'
            # add to data
            self.data[colName] = f
            return True

        except Exception, e:
            self.raiseError("Error in Seasonal Linear Regression: " + str(e))


    ''' ---------------------------------------------- '''
    ''' ---------------------------------------------- '''
    ''' ---------------------------------------------- '''

    ''' ---------------------------------------------- '''
    ''' KBIS '''
    ''' ---------------------------------------------- '''
    ''' ---------------------------------------------- '''
    ''' General '''
    ''' ---------------------------------------------- '''

    def prep_kbis(self, kbis):
        '''Function to load empty DF into KBI attribute'''
        try:
            # Set columns
            cols = ['fu_id', 'kbi_id', 'valor', 'kbi_nombre']
            # Set length of DF
            num_kbis = len(kbis)
            # Load empty DF
            self.kbis = pd.DataFrame(columns=cols, index=range(num_kbis))
            # Insert FU ID
            self.kbis[cols[0]] = [int(id) for id in  np.ones((num_kbis,)) * self.fu.fu_id]
            # Insert KBIs
            self.kbis[cols[1]] = [kbi.kbi_id for kbi in kbis]
        except Exception, e:
            self.raiseError('Error preparing KBIs: ' + str(e))

    def run_kbi(self, kbi_name, kbi = None):
        '''Function to run specific KBI by name'''
        try:
            # Get kbi function
            kbi_func = getattr(self, kbi_name)
            # Get KBI value
            kbi_value = kbi_func()
            # Load into DF if a table is provided
            if not kbi == None:
                # ID Col
                kbi_id_col = self.kbis.columns[1]
                # Value Col
                kbi_value_col = self.kbis.columns[2]
                # Name Col
                kbi_name_col = self.kbis.columns[3]
                # ID
                kbi_id = kbi.kbi_id
                # Set value
                self.kbis.loc[self.kbis[kbi_id_col]==kbi_id, kbi_value_col] = kbi_value
                # Set name
                self.kbis.loc[self.kbis[kbi_id_col] == kbi_id, kbi_name_col] = kbi_name
            return kbi_value
        except Exception, e:
            self.raiseError('Error running KBIs: ' + str(e))

    def get_kbi_value(self, kbi_id):
        # ID Col
        kbi_id_col = self.kbis.columns[1]
        # Value Col
        kbi_value_col = self.kbis.columns[2]
        return self.kbis.loc[self.kbis[kbi_id_col]==kbi_id, kbi_value_col].values[0]


    ''' ---------------------------------------------- '''
    ''' Volatility '''
    ''' ---------------------------------------------- '''
    def kurtosis(self):
        '''Kurtosis.'''
        try:
            # sets data
            x = self.data['Values']
            # num data points
            M = self.length
            # useful data
            x = pd.Series(x[:M])
            kurtosisValue = x.kurtosis()
            return kurtosisValue
        except Exception, e:
            self.raiseError('Error calculating Kurtosis: ' + str(e))

    def naiveError(self):
        # num data points
        M = self.length
        # sets data limiting length
        x = self.data['Values'][:M]
        # lag
        lag = self.fcstLag
        # check length
        if M <= lag:
            print('Naive Error: Not enough data')
            return np.nan
        # check denominator diferent from 0
        if sum(x[:M - lag].values) == 0:
            return np.nan
        # forecast acc
        naiveErrorValue = sum(abs(x[:M - lag].values - x[lag:M].values)) / sum(x[:M - lag].values)
        return naiveErrorValue

    def naiveLastCycleError(self):
        '''Naive last year error.'''
        try:
            # num data points
            M = self.length
            # sets data
            x = self.data['Values'][:M]
            # cyclelength
            c = self.cycleLength
            # check length
            if M <= c:
                print('Naive Last Year Error: Not enough data')
                return np.nan
            # forecast
            naiveLYErrorValue = sum(abs(x[:M - c].values - x[c:M].values)) / sum(x[:M - c].values)
            return naiveLYErrorValue
        except Exception, e:
            self.raiseError('Error calculating Naive LY Error: ' + str(e))

    def naiveLVxNaiveLY(self):
        '''Naive last value x Naive last year error.'''
        try:
            naive_error = self.naiveError()
            naive_ly_error = self.naiveLastCycleError()
            if naive_error == False or naive_ly_error == False:
                print('Naive LV x LY: Some error in Naives.')
                return False
            # KBI
            naiveLVxNaiveLYValue = naive_error * naive_ly_error
            return naiveLVxNaiveLYValue
        except Exception, e:
            self.raiseError('Error calculating Naive last value x Naive last year error: ' + str(e))

    ''' ---------------------------------------------- '''
    ''' Seasonality '''
    ''' ---------------------------------------------- '''
    def acc(self):
        '''Calculates ACC coeficient.'''
        try:
            # checks if enough data is available
            if self.seriesCycles < 2:
                print('ACC: Not enough data')
                return False
            # sets data
            x = self.data['Values']
            # num data points
            M = self.length
            # useful data
            x = x[:M]
            # cycle lngth
            c = self.cycleLength
            # remove first cycle
            acc01start = c
            acc01end = M
            # remove last cycle
            acc02start = 0
            acc02end = M - c
            # sets data
            acc01 = x[acc01start:acc01end]
            acc02 = x[acc02start:acc02end]
            # checks if data not 0s
            if sum(acc01) == 0 or sum(acc02) == 0:
                print('ACC: Some sum is 0')
                return False
            # calculate correl coef
            accValue = np.corrcoef(acc01, acc02)[0, 1]
            return accValue
        except Exception, e:
            self.raiseError('Error calculating ACC: ' + str(e))

    def accComp(self):
        '''Calculates ACC Comp coeficient.'''
        try:
            # checks if enough data is available
            if self.seriesCycles < 2:
                print('ACC Comp: Not enough data')
                return False
            # sets data
            x = self.data['Values']
            # num data points
            M = self.length
            # useful data
            x = x[:M]
            # cycle lngth
            c = self.cycleLength
            # ACC full cycle
            # remove first cycle
            acc01start = c
            acc01end = M
            # remove last cycle
            acc02start = 0
            acc02end = M - c
            # sets data
            acc01 = x[acc01start:acc01end]
            acc02 = x[acc02start:acc02end]
            # checks if data not 0s
            if sum(acc01) == 0 or sum(acc02) == 0:
                print('ACC Comp: Some sum is 0')
                return False
            # calculate correl coef
            accCoef0 = np.corrcoef(acc01, acc02)[0, 1]
            # ACC half cycle
            # remove first half cycle
            acc11start = c / 2
            acc11end = M
            # remove last half cycle
            acc12start = 0
            acc12end = M - c / 2
            # sets data
            acc11 = x[acc11start:acc11end]
            acc12 = x[acc12start:acc12end]
            # checks if data not 0s
            if sum(acc11) == 0 or sum(acc12) == 0:
                print('ACC Comp: Some sum is 0')
                return False
            # calculates correl coef for new data
            accCoef1 = np.corrcoef(acc11, acc12)[0, 1]
            # calculates compensated acc
            accCompValue = (accCoef0 - accCoef1) / 2
            return accCompValue
        except Exception, e:
            self.raiseError('Error calculating Compensated ACC:' + str(e))

    def accCompSI(self):
        '''Calculates ACC SI Comp coeficient.'''
        try:
            # checks if enough data is available
            if self.seriesCycles < 2 or self.seriesCycles / self.completeCycles < 1:
                print('ACC Comp SI: Not enough data')
                return False
            # sets data
            x = self.data['Values']
            # num data points
            M = self.length
            # useful data
            x = x[:M]
            # first difs
            y = np.zeros((M - 1,))
            for i in xrange(1, M):
                y[i - 1] = x[i] - x[i - 1]
            # cycle lngth
            c = self.cycleLength
            # ACC full cycle
            # remove first cycle
            acc01start = c
            acc01end = M - 1
            # remove last cycle
            acc02start = 0
            acc02end = M - 1 - c
            # sets data
            acc01 = y[acc01start:acc01end]
            acc02 = y[acc02start:acc02end]
            # checks if data not 0s
            if sum(acc01) == 0 or sum(acc02) == 0:
                print('ACC Comp SI: Some sum is 0')
                return False
            # calculate correl coef
            accCoef0 = np.corrcoef(acc01, acc02)[0, 1]
            # ACC half cycle
            # remove first half cycle
            acc11start = c / 2
            acc11end = M - 1
            # remove last half cycle
            acc12start = 0
            acc12end = M - 1 - c / 2
            # sets data
            acc11 = y[acc11start:acc11end]
            acc12 = y[acc12start:acc12end]
            # checks if data not 0s
            if sum(acc11) == 0 or sum(acc12) == 0:
                print('ACC Comp SI: Some sum is 0')
                return False
            # calculates correl coef for new data
            accCoef1 = np.corrcoef(acc11, acc12)[0, 1]
            # calculates compensated acc
            accCompSIValue = (accCoef0 - accCoef1) / 2
            return accCompSIValue
        except Exception as e:
            self.raiseError('Error calculating Compensated ACC: ' + str(e))

    ''' ---------------------------------------------- '''
    ''' Trend '''
    ''' ---------------------------------------------- '''
    def rot(self):
        '''Relative Order Trend.'''
        try:
            # sets data
            x = self.data['Values']
            # num data points
            M = self.length
            # useful data
            x = x[:M]
            # cycle length
            c = self.cycleLength
            # rot periods
            rotPeriods = c / 6
            # check length
            if self.length < c + rotPeriods:
                print('ROT: Not enough history')
                return False
            # initialize
            rotInitial = 0
            rotFinal = 0
            rotAvg = 0
            # loop through data
            for i in xrange(0, M):
                if i > (M - c - rotPeriods - 1) and i <= (M - c - 1):
                    rotInitial += x[i]
                elif i > (M - c - 2):
                    rotAvg += x[i]
                    if i > (M - rotPeriods - 1):
                        rotFinal += x[i]
            # check > 0
            if rotAvg <= 0 or rotFinal <= 0 or rotInitial <= 0 or rotInitial == rotFinal:
                print('ROT: Division by 0')
                return False
            # avg
            rotAvg = rotAvg / c
            # rot
            rotValue = abs((rotFinal - rotInitial) / (rotPeriods * rotAvg))
            return rotValue
        except Exception, e:
            self.raiseError('Error calculating ROT:' + str(e))

    def oot(self):
        '''Ordinal Order Trend.'''
        try:
            # length
            if self.length <= 1:
                print('OOT: Not enough history')
                return False
            # sets data
            x = self.data['Values']
            # num data points
            M = self.length
            # useful data
            x = x[:M]
            # cycle length
            c = self.cycleLength
            # regresor series
            z = [i + 1 for i in xrange(M)]
            z = np.array(z)
            # initialize
            z = sm_tools.add_constant(z)
            model = sm.OLS(x, z, missing='drop')
            results = model.fit()
            params = results.params
            # calculates oot
            slope = params[1]
            int = params[0]
            if int == 0:
                print('OOT: Division by 0')
                return False
            ootValue = float(slope) / float(int)
            return ootValue

        except Exception, e:
            self.raiseError('Error calculating OOT: ' + str(e))

    def fTest(self):
        '''Fischer Probability Test.'''
        try:
            # length
            if self.length <= 1:
                print('F Test: Not enough history')
                return False
            # sets data
            x = self.data['Values']
            # num data points
            M = self.length
            # useful data
            x = x[:M]
            # cycle length
            c = self.cycleLength
            # regresor series
            z = [i + 1 for i in xrange(M)]
            z = np.array(z)
            # initialize
            z = sm_tools.add_constant(z)
            model = sm.OLS(x, z, missing='drop')
            results = model.fit()
            # f test
            fValue = results.f_pvalue
            return fValue

        except Exception, e:
            self.raiseError('Error calculating F Prob: ' + str(e))

    ''' ---------------------------------------------- '''
    ''' Sparsity '''
    ''' ---------------------------------------------- '''
    def sparsityKBIs(self):
        '''Returns all sparsity indicators.'''
        try:
            # sets data
            x = self.data['Original Values']
            # sets variables
            M = self.length
            alpha = 0.3
            # check length
            if M <= 1:
                print('Sparsity: Not enough data.')
                return [False, False, False]
            p = np.zeros((M,))
            y = np.zeros((M,))
            l = np.zeros((M,))
            # initialize
            q = 0
            if x[0] > 0:
                p[0] = 1
                q += 1
            else:
                p[0] = 2
            y[0] = 0
            # loops through serie
            for i in range(1, M):
                if x[i] > 0:
                    p[i] = 1
                    y[i] = alpha * p[i - 1] + (1 - alpha) * y[i - 1]
                    q += 1
                else:
                    p[i] = p[i - 1] + 1
                    y[i] = y[i - 1]

            dataSpValue = float(q) / float(M)
            yEstValue = y[-1]
            sigmaPValue = np.std(p)

            return [dataSpValue, yEstValue, sigmaPValue]

        except Exception as e:
            self.raiseError('Error calculating sparsity KBIs: ' + str(e))

    def dataSparsity(self):
        '''Data sparsity.'''
        try:
            dataSparsityValue = self.sparsityKBIs()[0]
            return dataSparsityValue
        except Exception, e:
            self.raiseError('Error calculating data sparsity: ' + str(e))

    def yEstSparsity(self):
        '''y Estimator sparsity.'''
        try:
            yEstSparsityValue = self.sparsityKBIs()[1]
            return yEstSparsityValue
        except Exception, e:
            self.raiseError('Error calculating y Est sparsity: ' + str(e))

    def sigmaSparsity(self):
        '''Sigma sparsity.'''
        try:
            sigmaSparsityValue = self.sparsityKBIs()[2]
            return sigmaSparsityValue
        except Exception, e:
            self.raiseError('Error calculating sigma sparsity: ' + str(e))

    ''' ---------------------------------------------- '''
    ''' Behavioral Change '''
    ''' ---------------------------------------------- '''
    def fTestChange(self):
        '''F Test for Behavioral Change'''
        try:
            # length
            if self.length <= 2:
                print('F Test Change: Not enough history')
                return False
            # sets data
            x = self.data['Values']
            # num data points
            M = self.length
            # useful data
            x = x[:M]
            # abs diference
            x = abs(x - x.shift(periods=1, freq=None, axis=0))
            x = x[1:]
            # regresor series
            z = [i + 1 for i in xrange(M-1)]
            z = np.array(z)
            # initialize
            z = sm_tools.add_constant(z)
            model = sm.OLS(x, z, missing='drop')
            results = model.fit()
            # f test
            fValue = results.f_pvalue
            return fValue
        except Exception, e:
            self.raiseError('Error calculating fTestChange: ' + str(e))