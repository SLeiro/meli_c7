import os
import pandas as pd
import numpy as np
import statsmodels.formula.api as sm
import statsmodels.tools.tools as sm_tools
import datetime
from dateutil.relativedelta import relativedelta


class KBIs(object):

    def __init__(self):
        pass

    def set_time_series(self, time_series):
        self.data = time_series
        self.length = len(time_series)
        self.max_index = self.length

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
            self.kbis[cols[0]] = [int(id) for id in np.ones((num_kbis,)) * self.fu.fu_id]
            # Insert KBIs
            self.kbis[cols[1]] = [kbi.kbi_id for kbi in kbis]
        except Exception as e:
            self.raiseError('Error preparing KBIs: ' + str(e))

    def run_kbi(self, kbi_name, kbi=None):
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
                self.kbis.loc[self.kbis[kbi_id_col] == kbi_id, kbi_value_col] = kbi_value
                # Set name
                self.kbis.loc[self.kbis[kbi_id_col] == kbi_id, kbi_name_col] = kbi_name
            return kbi_value
        except Exception as e:
            self.raiseError('Error running KBIs: ' + str(e))

    def get_kbi_value(self, kbi_id):
        # ID Col
        kbi_id_col = self.kbis.columns[1]
        # Value Col
        kbi_value_col = self.kbis.columns[2]
        return self.kbis.loc[self.kbis[kbi_id_col] == kbi_id, kbi_value_col].values[0]

    ''' ---------------------------------------------- '''
    ''' ESSENTIALS '''
    ''' ---------------------------------------------- '''

    def set_cycle_length(self, time_interval='month'):
        try:
            # cycle_length
            if time_interval == 'month':
                self.cycle_length = 12
            elif time_interval == 'week':
                self.cycle_length = 52
            else:
                raise ValueError('Error setting time interval.')

            return self.cycle_length
        except Exception as e:
            self.raiseError('Error in cycle length: ' + str(e))

    def set_series_cycles(self):
        try:
            # total cycles
            self.series_cycles = float(self.length) / float(self.cycle_length)
            return self.series_cycles
        except Exception as e:
            self.raiseError('Error setting cycles: ' + str(e))

    def set_complete_cycles(self):
        try:
            # completeCycles
            self.complete_cycles = self.length / self.cycle_length
            return self.complete_cycles
        except Exception as e:
            self.raiseError('Error in complete cycles: ' + str(e))

    ''' ---------------------------------------------- '''
    ''' Volatility '''
    ''' ---------------------------------------------- '''

    def kurtosis(self):
        '''Kurtosis.'''
        try:
            # sets data
            x = self.data['values']
            # num data points
            m = self.length
            # useful data
            x = pd.Series(x[:m])
            kurtosis_value = x.kurtosis()
            return kurtosis_value
        except Exception as e:
            self.raiseError('Error calculating Kurtosis: ' + str(e))

    def naive_error(self, lag=12):
        # num data points
        m = self.length
        # sets data limiting length
        x = self.data['values'][:m]
        # check length
        if m <= lag:
            print('Naive Error: Not enough data')
            return np.nan
        # check denominator diferent from 0
        if sum(x[:m - lag].values) == 0:
            return np.nan
        # forecast acc
        naive_error_value = sum(abs(x[:m - lag].values - x[lag:m].values)) / sum(x[:m - lag].values)
        return naive_error_value

    def naive_last_cycle_error(self):
        '''Naive last year error.'''
        try:
            # num data points
            m = self.length
            # sets data
            x = self.data['values'][:m]
            # cycle_length
            c = self.cycle_length
            # check length
            if m <= c:
                print('Naive Last Year Error: Not enough data')
                return np.nan
            # forecast
            naive_last_cycle_error_value = sum(abs(x[:m - c].values - x[c:m].values)) / sum(
                x[:m - c].values)
            return naive_last_cycle_error_value
        except Exception as e:
            self.raiseError('Error calculating Naive LY Error: ' + str(e))

    def naive_lv_times_naive_ly(self):
        '''Naive last value x Naive last year error.'''
        try:
            naive_error = self.naive_error()
            naive_ly_error = self.naive_last_cycle_error()
            if naive_error == False or naive_ly_error == False:
                print('Naive LV x LY: Some error in Naives.')
                return False
            # KBI
            naive_lv_times_naive_ly_value = naive_error * naive_ly_error
            return naive_lv_times_naive_ly_value
        except Exception as e:
            self.raiseError('Error calculating Naive last value x Naive last year error: ' + str(e))

    ''' ---------------------------------------------- '''
    ''' Seasonality '''
    ''' ---------------------------------------------- '''

    def acc(self):
        '''Calculates ACC coeficient.'''
        try:
            # checks if enough data is available
            if self.series_cycles < 2:
                print('ACC: Not enough data')
                return False
            # sets data
            x = self.data['values']
            # num data points
            m = self.length
            # useful data
            x = x[:m]
            # cycle lngth
            c = self.cycle_length
            # remove first cycle
            acc_01_start = c
            acc_01_end = m
            # remove last cycle
            acc_02_start = 0
            acc_02_end = m - c
            # sets data
            acc_01 = x[acc_01_start:acc_01_end]
            acc_02 = x[acc_02_start:acc_02_end]
            # checks if data not 0s
            if sum(acc_01) == 0 or sum(acc_02) == 0:
                print('ACC: Some sum is 0')
                return False
            # calculate correl coef
            acc_value = np.corrcoef(acc_01, acc_02)[0, 1]
            return acc_value
        except Exception as e:
            self.raiseError('Error calculating ACC: ' + str(e))

    def acc_comp(self):
        '''Calculates ACC Comp coeficient.'''
        try:
            # checks if enough data is available
            if self.series_cycles < 2:
                print('ACC Comp: Not enough data')
                return False
            # sets data
            x = self.data['values']
            # num data points
            m = self.length
            # useful data
            x = x[:m]
            # cycle lngth
            c = self.cycle_length
            # ACC full cycle
            # remove first cycle
            acc_01_start = c
            acc_01_end = m
            # remove last cycle
            acc_02_start = 0
            acc_02_end = m - c
            # sets data
            acc_01 = x[acc_01_start:acc_01_end]
            acc_02 = x[acc_02_start:acc_02_end]
            # checks if data not 0s
            if sum(acc_01) == 0 or sum(acc_02) == 0:
                print('ACC Comp: Some sum is 0')
                return False
            # calculate correl coef
            acc_coef_0 = np.corrcoef(acc_01, acc_02)[0, 1]
            # ACC half cycle
            # remove first half cycle
            acc_11_start = c / 2
            acc_11_end = m
            # remove last half cycle
            acc_12_start = 0
            acc_12_end = m - c / 2
            # sets data
            acc_11 = x[acc_11_start:acc_11_end]
            acc_12 = x[acc_12_start:acc_12_end]
            # checks if data not 0s
            if sum(acc_11) == 0 or sum(acc_12) == 0:
                print('ACC Comp: Some sum is 0')
                return False
            # calculates correl coef for new data
            acc_coef_1 = np.corrcoef(acc_11, acc_12)[0, 1]
            # calculates compensated acc
            acc_comp_value = (acc_coef_0 - acc_coef_1) / 2
            return acc_comp_value
        except Exception as e:
            self.raiseError('Error calculating Compensated ACC:' + str(e))

    def acc_comp_si(self):
        '''Calculates ACC SI Comp coeficient.'''
        try:
            # checks if enough data is available
            if self.series_cycles < 2 or self.series_cycles / self.complete_cycles < 1:
                print('ACC Comp SI: Not enough data')
                return False
            # sets data
            x = self.data['values']
            # num data points
            m = self.length
            # useful data
            x = x[:m]
            # first difs
            y = np.zeros((m - 1,))
            for i in range(1, m):
                y[i - 1] = x[i] - x[i - 1]
            # cycle lngth
            c = self.cycle_length
            # ACC full cycle
            # remove first cycle
            acc_01_start = c
            acc_01_end = m - 1
            # remove last cycle
            acc_02_start = 0
            acc_02_end = m - 1 - c
            # sets data
            acc_01 = y[acc_01_start:acc_01_end]
            acc_02 = y[acc_02_start:acc_02_end]
            # checks if data not 0s
            if sum(acc_01) == 0 or sum(acc_02) == 0:
                print('ACC Comp SI: Some sum is 0')
                return False
            # calculate correl coef
            acc_coef_0 = np.corrcoef(acc_01, acc_02)[0, 1]
            # ACC half cycle
            # remove first half cycle
            acc_11_start = c / 2
            acc_11_end = m - 1
            # remove last half cycle
            acc_12_start = 0
            acc_12_end = m - 1 - c / 2
            # sets data
            acc_11 = y[acc_11_start:acc_11_end]
            acc_12 = y[acc_12_start:acc_12_end]
            # checks if data not 0s
            if sum(acc_11) == 0 or sum(acc_12) == 0:
                print('ACC Comp SI: Some sum is 0')
                return False
            # calculates correl coef for new data
            acc_coef_1 = np.corrcoef(acc_11, acc_12)[0, 1]
            # calculates compensated acc
            acc_comp_si_value = (acc_coef_0 - acc_coef_1) / 2
            return acc_comp_si_value
        except Exception as e:
            self.raiseError('Error calculating Compensated ACC: ' + str(e))

    ''' ---------------------------------------------- '''
    ''' Trend '''
    ''' ---------------------------------------------- '''

    def rot(self):
        '''Relative Order Trend.'''
        try:
            # sets data
            x = self.data['values']
            # num data points
            m = self.length
            # useful data
            x = x[:m]
            # cycle length
            c = self.cycle_length
            # rot periods
            rot_periods = c / 6
            # check length
            if self.length < c + rot_periods:
                print('ROT: Not enough history')
                return False
            # initialize
            rot_initial = 0
            rot_final = 0
            rot_avg = 0
            # loop through data
            for i in range(0, m):
                if i > (m - c - rot_periods - 1) and i <= (m - c - 1):
                    rot_initial += x[i]
                elif i > (m - c - 2):
                    rot_avg += x[i]
                    if i > (m - rot_periods - 1):
                        rot_final += x[i]
            # check > 0
            if rot_avg <= 0 or rot_final <= 0 or rot_initial <= 0 or rot_initial == rot_final:
                print('ROT: Division by 0')
                return False
            # avg
            rot_avg = rot_avg / c
            # rot
            rot_value = abs((rot_final - rot_initial) / (rot_periods * rot_avg))
            return rot_value
        except Exception as e:
            self.raiseError('Error calculating ROT:' + str(e))

    def oot(self):
        '''Ordinal Order Trend.'''
        try:
            # length
            if self.length <= 1:
                print('OOT: Not enough history')
                return False
            # sets data
            x = self.data['values']
            # num data points
            m = self.length
            # useful data
            x = x[:m]
            # cycle length
            c = self.cycle_length
            # regresor series
            z = [i + 1 for i in range(m)]
            z = np.array(z)
            # initialize
            z = sm_tools.add_constant(z)
            model = sm.OLS(x, z, missing='drop')
            results = model.fit()
            params = results.params
            # calculates oot
            slope = params[1]
            intersection = params[0]
            if int == 0:
                print('OOT: Division by 0')
                return False
            oot_value = float(slope) / float(intersection)
            return oot_value

        except Exception as e:
            self.raiseError('Error calculating OOT: ' + str(e))

    def f_test(self):
        '''Fischer Probability Test.'''
        try:
            # length
            if self.length <= 1:
                print('F Test: Not enough history')
                return False
            # sets data
            x = self.data['values']
            # num data points
            m = self.length
            # useful data
            x = x[:m]
            # cycle length
            c = self.cycle_length
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

        except Exception as e:
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
            m = self.length
            alpha = 0.3
            # check length
            if m <= 1:
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
        except Exception as e:
            self.raiseError('Error calculating data sparsity: ' + str(e))

    def yEstSparsity(self):
        '''y Estimator sparsity.'''
        try:
            yEstSparsityValue = self.sparsityKBIs()[1]
            return yEstSparsityValue
        except Exception as e:
            self.raiseError('Error calculating y Est sparsity: ' + str(e))

    def sigmaSparsity(self):
        '''Sigma sparsity.'''
        try:
            sigmaSparsityValue = self.sparsityKBIs()[2]
            return sigmaSparsityValue
        except Exception as e:
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
            x = self.data['values']
            # num data points
            m = self.length
            # useful data
            x = x[:m]
            # abs diference
            x = abs(x - x.shift(periods=1, freq=None, axis=0))
            x = x[1:]
            # regresor series
            z = [i + 1 for i in xrange(M - 1)]
            z = np.array(z)
            # initialize
            z = sm_tools.add_constant(z)
            model = sm.OLS(x, z, missing='drop')
            results = model.fit()
            # f test
            fValue = results.f_pvalue
            return fValue
        except Exception as e:
            self.raiseError('Error calculating fTestChange: ' + str(e))
