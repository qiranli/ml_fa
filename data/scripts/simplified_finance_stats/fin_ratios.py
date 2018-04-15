# Fundamental Data
# Financial ratios and other metrics such as fcf
import pandas as pd
import numpy as np

def get_ratios(b_sheet,i_sheet,c_sheet,o_sheet,mrkt_sheet):
    """ Returns financial ratios and other metrics. Including but not
        limited to
        1. Margins
        2. Cashflow ratios
        3. Return on A, I etc
        4. Price ratios
        """

    # s: df_stats
    s = pd.concat([b_sheet,i_sheet,c_sheet,o_sheet,mrkt_sheet])
    # r: df_ratios
    r = pd.DataFrame(columns = s.columns.tolist())

    # Gross Margin
    r.loc['gross_mrgn'] = (1.*s.loc['revt'] - s.loc['cogs'])/s.loc['revt']
    # Profit Margin
    r.loc['prft_mrgn'] = (1.*s.loc['niadj']/s.loc['revt'])
    # Pre-tax operating margin
    r.loc['oper_mrgn'] = (1.*s.loc['oiadp']/s.loc['revt'])
    # Capx to revenue
    r.loc['capx_to_rev'] = (1.*s.loc['capx']/s.loc['revt'])
    # net investment to revenue
    r.loc['ni_to_rev'] = (1.*(s.loc['capx']-s.loc['dpc'])/s.loc['revt'])
    # ROE
    r.loc['roe'] = (1.*s.loc['niadj']/s.loc['seq'])
    # ROA
    r.loc['roa']=(1.*s.loc['niadj']/s.loc['at'])
    # Return on oeprating assets
    r.loc['rooa']=(1.*s.loc['niadj']/(s.loc['at']-s.loc['intan']-\
                    s.loc['che'] - s.loc['ivaeq'] - s.loc['ivao']))
    # revt to assets (capital intensity)
    r.loc['revt_to_asts']=(1.*s.loc['revt']/s.loc['at'])
    # ROC
    r.loc['roc'] = (1.*s.loc['niadj']/(s.loc['dltt']+s.loc['seq']))
    # ROIC
    invested_cap = s.loc['act'] - s.loc['lct'] - s.loc['che'] - s.loc['ivaeq']
    r.loc['roic']=(1.*s.loc['niadj']/invested_cap)
    # tax rate
    r.loc['tax_rate']=(1.*s.loc['txt']/s.loc['pi'])

    # Free cash flow
    # fcf = net_income + depreciation + amortization -
    #       change_in_net_working_capital - capx
    #              or
    # fcf = cash_from_operations - cpax
    r.loc['fcf'] = s.loc['niadj'] + s.loc['dpc'] - s.loc['wcapch'] - \
                    s.loc['capx']

    # fcf ratios
    # cash flow from operations
    r.loc['cfo'] = s.loc['niadj'] + s.loc['dpc'] - s.loc['wcapch']
    # fcf to revenue
    r.loc['fcf_to_revt'] = 1.0*(r.loc['fcf']/s.loc['revt'])
    # Asset efficiency ratio
    r.loc['cfo_to_assets'] = 1.0*(s.loc['oancf']/r.loc['roa'])
    # Current liability coverage ratio - test of solvency
    r.loc['cfo_to_curr_liab'] = 1.0*(s.loc['oancf']/s.loc['lct'])
    # long term debt ratio
    r.loc['cfo_long_term_debt'] = 1.0*(s.loc['oancf']/s.loc['dltt'])
    # cash generating power ratio from operations
    r.loc['cfo_power'] = 1.0*(s.loc['oancf']/(s.loc['oancf'] + \
                                s.loc['ivncf'] + s.loc['fincf']))
    # External financing index ratio - dependency on external financing
    r.loc['ext_fin_ratio'] = 1.0*(s.loc['fincf']/s.loc['oancf'])

    # Debt ratios
    # leverage
    r.loc['liab_to_assets'] = 1.0*(s.loc['dltt']/s.loc['at'])
    # debt to equity
    r.loc['debt_to_equity'] = 1.0*(s.loc["dltt"] + s.loc['lct'])/s.loc['seq']

    # Price ratios
    # Price to earnings
    r.loc['pe'] = 1.0*(s.loc['mkvalt']/s.loc['niadj'])
    # Price to book
    r.loc['pb'] = 1.0*(s.loc['mkvalt']/s.loc['seq'])

    return r
