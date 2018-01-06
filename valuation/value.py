""" Computes the valuation of the company based on the cashflows and other
    options """

import pandas as pd
import numpy as np
import sys
sys.path.append("..")

from data.scripts.simplified_finance_stats.fin_stats import fin_stats
from data.scripts.simplified_finance_stats.fin_stats_2 import fin_stats_2
from data.scripts.simplified_finance_stats.stock_stats import stock_stats
from input_params import get_inp_params

class valuation(object):
    """ Computes the intrinsic value of the company.

        Uses input parameters from input_params.py.


    """

    def __init__(self,fcf,tick,finances=None,fin_others=None,mkt_data=None):
        """ Instantiates using inp_parameters (from inp_params.py) and fcf.
        fcf is a dict containing non-terminal and terminal cashflows"""

        # If dataset if not loaded already, load the dataset
        if finances == None:

            print("Dataset not loaded, loading the dataset...")

            # Set path for data
            base_path = '../data/'
            sheets_path = 'combined_simplified/combined_all_us.csv'
            other_path = 'combined_simplified/others_all_us.csv'
            mkt_path = 'combined_simplified/stock_stats_all_us.csv'

            # setup all data
            finances = fin_stats(base_path + sheets_path)
            fin_others = fin_stats_2(base_path + other_path)
            mkt_data = stock_stats(base_path + mkt_path)

        self.inp_params = get_inp_params(tick,finances,fin_others,mkt_data)
        self.fcf = fcf
        self.n_years = int(self.fcf['non_terminal'].shape[0])

    def cost_of_capital(self):
        """ Returns the vector for cost of capital for each year in the fcf"""

        years = np.linspace(0,self.n_years-1,self.n_years)

        # cost of capital
        init_cc = self.inp_params['cost_of_capital']
        terminal_cc = self.inp_params['stable_cc_default'][1]

        # initialize cost of capital vector
        cc_vector = np.ones(self.n_years)*init_cc

        # linearly regress to achieve target or terminal cost of capital
        x = np.array([years[np.floor((self.n_years/2.)-1)],years[-1]])
        y = np.array([init_cc,terminal_cc])
        coeffs = np.polyfit(x,y,1)
        p = np.poly1d(coeffs) # regression line polynomial

        # Update the cc_vector with new cc values after mid point
        for i,rate in enumerate(cc_vector):
            if i > np.floor((self.n_years/2.)-1):
                cc_vector[i] = p(i)

        return cc_vector

    def cum_discount_factor(self):
        """ Returns the vector of cumulative discount factors for every year"""

        cc_vector = self.cost_of_capital()

        # Initialize cumulative discount factor vector
        cdf = np.ones(self.n_years)

        for i in range(self.n_years):
            if i == 0:
                cdf[i] = 1./(1+cc_vector[0])
            else:
                cdf[i] = cdf[i-1]*(1./(1. + cc_vector[i]))

        return cdf


    def pv_cf(self):
        """ Returns the present value of sum of all cashflows"""

        cc_vector = self.cost_of_capital()
        cdf = self.cum_discount_factor()

        # total present value of all future cash flows excluding terminal cash flow
        pv_fcf = np.dot(self.fcf['non_terminal'],cdf)

        # terminal Cashflow
        terminal_value = self.fcf['terminal']/ \
                (cc_vector[-1] - self.inp_params['stable_growth_rate_default'][1])

        pv_terminal_value = terminal_value*cdf[-1]

        # sum  of all present value
        sum_pv = pv_terminal_value + pv_fcf

        return sum_pv

    def val_eq(self):
        """ Returns the value of common equity per share and price as a % of vlaue """

        # sum of present values of all cash flows
        sum_pv = self.pv_cf()

        # Probability of failure
        fail_prob = self.inp_params['failure_prob']
        # Proceeds if firm fails
        proceeds = self.inp_params['proceeds']*self.inp_params['val_of_proceeds']

        # Value of operating assets
        val_oa = sum_pv*(1. - fail_prob)

        # Value of equity
        val_eq = val_oa - self.inp_params['bk_val_debt'] + self.inp_params['cash_eq']

        # Value of options
        #val_op = options_value()
        val_op = 643.8

        # common equity value or intrinsic value
        val_eq_common = val_eq  - val_op

        # common equity value per share
        val_per_share = val_eq_common/self.inp_params['outstanding_shares']

        # Price as a % of value
        p_to_val = self.inp_params['curr_stock_price']/val_per_share

        return val_per_share,p_to_val


if __name__ == '__main__':

    # Test
    fcf = {}
    fcf['non_terminal'] = np.array([16338.4,19126.57,22287.68,25833.92,
                                    29760.31,31996.11,32994.82,32598.71,
                                    30831.27,27902.47])

    fcf['terminal'] = 23336.29

    v = valuation(fcf,'FB')

    v1,p1 = v.val_eq()

    print v1,p1
