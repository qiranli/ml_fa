""" Input parameters to calculate the intrinsic valuation of a business"""

import pandas as pd
import sys
sys.path.append('..')


def get_inp_params(tick,finances,fin_others,mkt_data):
    """ Returns the dictionary of input parameters"""

    # Get the fundamental data
    b = finances.get_sheet(tick,"balance_sheet")
    i = finances.get_sheet(tick,"income_sheet")
    c = finances.get_sheet(tick,"cashflow_sheet")
    o = fin_others.get_sheet(tick)
    mk = mkt_data.get_stock_data(tick)

    inp_params = {}
    inp_params['inc_country'] = 'USA'
    inp_params['industry'] = 'default'
    inp_params['revenue'] = i.loc['revt'].iloc[-1] # latest revenue
    inp_params['ebit'] = i.loc['pi'].iloc[-1]
    inp_params['interest_expense'] = i.loc['xint'].iloc[-1]
    inp_params['bk_val_equity'] = b.loc['seq'].iloc[-1]
    inp_params['bk_val_debt'] = b.loc['dlc'].iloc[-1] + b.loc['dltt'].iloc[-1]
    inp_params['R_D_expenses'] = False
    inp_params['lease_commit'] = False
    inp_params['cash_eq'] = b.loc['che'].iloc[-1]
    inp_params['outstanding_shares'] = mk.loc['csho'].iloc[-1]
    inp_params['curr_stock_price'] = mk.loc['prcc_c'].iloc[-1]
    inp_params['eff_tax_r'] = (1.0*i.loc['txt'].iloc[-1])/i.loc['pi'].iloc[-1]
    inp_params['marg_tax_r'] = .28

    # Drivers
    # Compounded annual growth rate over future 5 years, growth driver
    inp_params['rev_growth_f'] = .25
    # Target pre-tax operating margin or EBIT wrt to revenue, profitability Driver
    inp_params['target_ebit'] = .25
    # reinvestment, efficiency driver
    inp_params['sales_to_capital'] = 5

    # Market parameters
    # Risk-free rate (rf_rate), US 10 year note
    inp_params['rf_rate'] = 0.02405
    # Initial cost of capital
    inp_params['cost_of_capital'] = 0.08

    # Other params
    # Employee stock options (ESO) outstanding
    inp_params['ESO'] = True
    inp_params['number_of_ESO'] = 4.4
    inp_params['avg_strike_price'] = 6.05
    inp_params['avg_maturity'] = 2.6
    inp_params['std_stock'] = .3

    # Assumptions

    # 1. In stable growth, cost of capital = risk_free_rate + 4.5%
    cc_default = inp_params['rf_rate'] + 0.045
    inp_params['stable_cc_default'] = [False,0.085]
    # To use other cc value, use False and cc after year 10

    # 2. After year 10, return on capital = cost of capital after year 10.
    # Competitive advantage fades over time
    roc_base = inp_params['cost_of_capital']
    inp_params['roc_default'] = [False,14]
    # To use other, set the values to False and expected ROC after year 10

    # 3. Chance of failure in the forseeable future
    inp_params['failure_prob'] = 0.0
    inp_params['proceeds'] = inp_params['bk_val_equity']
    inp_params['val_of_proceeds'] = 0.5 # % of value of proceeds if the firm fails

    # 4.  Effective tax rate normalizes to marginal tax rate
    inp_params['tax_normalization'] = False

    # 5. Growth assumptions
    # After 10 year, growth  = risk free rate
    # Ensures that unreasonalble growth rates are not used
    stable_avg_growth_rate = inp_params['rf_rate']
    inp_params['stable_growth_rate_default'] = [False,0.03]
    # To use other values, use False and growth rate after year 10

    # 6. Cash in other countries
    inp_params['foreign_cash'] = 0.0
    inp_params['avg_tx_rate_foreign'] = 0.15

    return inp_params
