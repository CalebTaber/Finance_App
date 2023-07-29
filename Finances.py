import pandas as pd
import numpy as np
from datetime import date, timedelta
import plotly.graph_objects as go


# Converts string in format YYYY-mm-dd into a date object
def iso_str_to_date(date_str: str):
    return date.fromisoformat(date_str)


# Returns a stringfied version of the given date object
# If monthly, returns in format bbbyy
# Else, returns in format mm/dd/yy
def to_plot_date(input_date: date, monthly: bool):
    return input_date.strftime("%y-%m") if monthly else input_date.strftime("%m/%d/%y")


# Read transactions from file and initialize columns correctly
def read_transactions(filename: str):
    transactions_df = pd.read_csv(filename, sep=';')
    transactions_df['Date'] = transactions_df['Date'].map(iso_str_to_date)
    transactions_df['Description Keywords'] = transactions_df['Description Keywords'].apply(str.split, sep=',')
    return transactions_df


# Write transactions to file
# NOTE: must call write_transactions(df.copy()). Otherwise, it will add a comma afer every char in the keywords
def write_transactions(transactions_df: pd.DataFrame):
    transactions_df['Description Keywords'] = transactions_df['Description Keywords'].map(lambda x: ','.join(x))
    transactions_df.sort_values(by='Date', inplace=True)
    transactions_df.to_csv('Transactions.csv', index=False, sep=';')


def input_transactions():
    txn_df = read_transactions('Transactions.csv')

    date_input = widgets.DatePicker()
    amt_input = widgets.FloatText()
    loc_input = widgets.Text(placeholder='Location')
    cat_input = widgets.Combobox(placeholder='Category', options=list(np.sort(txn_df['Category'].unique())))
    desc_input = widgets.Text(placeholder='Keywords')
    submit_button = widgets.Button(description='Submit')
    output = widgets.Output()

    def submit_txn(button):
        txn_date = date_input.value
        amount = amt_input.value
        location = loc_input.value if loc_input.value != '' else np.NaN
        category = cat_input.value
        keywords = [category.lower()] + desc_input.value.split(',')

        if txn_date == '' or amount == '' or category == '':
            with output:
                print('Must fill out date, amount, and category')
            return

        txn_df.loc[len(txn_df)] = [txn_date, amount, location, category, keywords]
        write_transactions(txn_df.copy())

        with output:
            sub_trans = txn_df.loc[len(txn_df) - 1]
            sub_date = sub_trans['Date']
            sub_amt = sub_trans['Amount']
            sub_loc = sub_trans['Location']
            sub_cat = sub_trans['Category']
            sub_desc = sub_trans['Description Keywords']
            print('Submitted:', str(sub_date), str(sub_amt), sub_loc, sub_cat, sub_desc, sep='\t')

    submit_button.on_click(submit_txn)
    display(txn_df.sort_values(by='Date').tail(15), date_input, amt_input, loc_input, cat_input, desc_input, submit_button, output)


# Returns a row of a dataframe that describes the period over period change in gross income, expenses, and net income
def calc_pop_change(period_begin: date, period_end: date, gross: float, expenses: float, net: float, last_period: pd.DataFrame):
    prev_gross = last_period['Gross_Income'].sum()
    prev_expenses = last_period['Expenses'].sum()
    prev_net = last_period['Net_Income'].sum()

    return [period_begin,
            period_end,
            gross,
            ((gross - prev_gross) / np.abs(prev_gross)) if prev_gross != 0 else 0,
            expenses,
            ((expenses - prev_expenses) / np.abs(prev_expenses)) if prev_expenses != 0 else 0,
            net,
            ((net - prev_net) / np.abs(prev_net)) if prev_net != 0 else 0]


# Returns DataFrame of values within the specified date range
def records_within_range(transactions_df: pd.DataFrame, start_date: date, end_date: date):
    return transactions_df[(transactions_df['Date'] >= start_date) & (transactions_df['Date'] < end_date)].reset_index(drop=True)


def generate_monthly_end_dates(begin_date: date, end_date: date):
    end_dates = list()

    for year in range(begin_date.year, end_date.year + 1):
        for month in range(1, 13):
            if (year == begin_date.year) and (month < begin_date.month + 1):
                continue;
            if (year == end_date.year) and (month > end_date.month + 1):
                break;  # Add 1 to end_date.month because we want to have the last end date be the first day of the next month without any recorded data

            end_dates.append(date(year=year, month=month, day=1))

    return end_dates


def generate_end_dates(begin_date: date, end_date: date, period_length: timedelta, monthly: bool):
    if (monthly):
        return generate_monthly_end_dates(begin_date, end_date)

    # Generate list of end dates for periods, based on period_length
    end_dates = list()
    next_end = begin_date + period_length
    while next_end < end_date:
        end_dates.append(next_end)
        next_end += period_length
    end_dates.append(end_date)

    return end_dates


def summarize_inc_exp(transactions_df: pd.DataFrame, begin_date: date, end_date: date, period_length: timedelta, monthly: bool):
    summary_df = pd.DataFrame(
        columns=['Period_Begin', 'Period_End', 'Gross_Income', 'Gross_Income_PoP', 'Expenses', 'Expenses_PoP', 'Net_Income', 'Net_Income_PoP'])

    end_dates = generate_end_dates(begin_date, end_date, period_length, monthly)

    # Iterate over periods and compute values for summary dataframe
    start = begin_date
    for end in end_dates:
        period_txns = records_within_range(transactions_df, start, end)

        # Calculate aggregate values for the period
        gross_income = period_txns[period_txns['Amount'] >= 0]['Amount'].sum()
        expenses = np.abs(period_txns[period_txns['Amount'] < 0]['Amount'].sum())
        net_income = gross_income - expenses

        # Calculate PoP values for the period
        prev_period = summary_df[summary_df['Period_End'] == start]
        if len(prev_period) == 0:
            summary_df.loc[len(summary_df)] = [start, end, gross_income, 0, expenses, 0, net_income, 0]
        else:
            summary_df.loc[len(summary_df)] = calc_pop_change(start, end, gross_income, expenses, net_income, prev_period)

        # Reset start for next iteration
        start = end

    if monthly:
        summary_df['Plot_Date'] = summary_df['Period_Begin'].apply(to_plot_date, monthly=monthly)
    else:
        summary_df['Plot_Date'] = summary_df['Period_End'].apply(to_plot_date, monthly=monthly)
    return summary_df


def agg_by_cat(txn_df: pd.DataFrame, start: date, end: date):
    trans_slice_df = records_within_range(txn_df, start, end).copy()
    trans_slice_df['Plot_Date'] = trans_slice_df['Date'].apply(to_plot_date, monthly=True)

    agged_df = pd.DataFrame(columns=['Plot_Date', 'Category', 'Sum'])

    for plotdate in trans_slice_df['Plot_Date'].unique():
        for cat in trans_slice_df['Category'].unique():
            sub_df = trans_slice_df[(trans_slice_df['Plot_Date'] == plotdate) & (trans_slice_df['Category'] == cat)]
            agged_df.loc[len(agged_df)] = [plotdate, cat, sub_df['Amount'].sum()]

    return agged_df


txns_plot_width = 1000
txns_plot_height = 500


def plot_raw_inc_exp(summary_stats: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=summary_stats['Plot_Date'], y=summary_stats['Gross_Income'], mode='lines', name='Gross Income', line=dict(color='blue', width=2)))
    fig.add_trace(go.Scatter(x=summary_stats['Plot_Date'], y=summary_stats['Expenses'], mode='lines', name='Expenses', line=dict(color='red', width=2)))
    fig.add_trace(go.Scatter(x=summary_stats['Plot_Date'], y=summary_stats['Net_Income'], mode='lines', name='Net Income', line=dict(color='green', width=2)))

    fig.update_layout(width=txns_plot_width, height=txns_plot_height, title='Income and Expenses', yaxis_title='Amount in USD',
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    fig.show()


def plot_inc_exp_pop(summary_stats: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=summary_stats['Plot_Date'], y=summary_stats['Gross_Income_PoP'], name='Gross Income', marker_color='blue'))
    fig.add_trace(go.Bar(x=summary_stats['Plot_Date'], y=summary_stats['Expenses_PoP'], name='Expenses', marker_color='red'))
    fig.add_trace(go.Bar(x=summary_stats['Plot_Date'], y=summary_stats['Net_Income_PoP'], name='Net Income', marker_color='green'))

    fig.update_layout(barmode='group', width=txns_plot_width, height=txns_plot_height, title='Income and Expenses PoP Change', yaxis_title='Percentage Change',
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    fig.show()


import plotly.express as px


def plot_agged_cats(agged_cat_df: pd.DataFrame):
    specific_to_general = {
        'Gas': 'Car',
        'Clothes': 'Personal',
        'Groceries': 'Food',
        'Dad': 'People',
        'Running': 'Personal',
        'Bike': 'Personal',
        'Gifts': 'Gifts',
        'ECM': 'Job',
        'Personal Care': 'Personal',
        'Spotify': 'Personal',
        'Car': 'Car',
        'Misc': 'Misc',
        'Entertainment': 'Personal',
        'Cashback': 'Investments',
        'College': 'School',
        'Food': 'Food',
        'Nonfood Groceries': 'Housing',
        'Mom': 'People',
        'Computer': 'Personal',
        'Stock Cashout': 'Investments',
        'Tax': 'Tax',
        'Interest': 'Investments',
        'M&T': 'Job',
        'Nathaniel': 'People',
        'Housing': 'Housing',
        'Travel': 'Personal',
        'Healthcare': 'Healthcare',
        'Housewares': 'Housing'
    }
    agged_cat_df = agged_cat_df.rename(columns={'Category': 'SpecificCategory'})
    agged_cat_df['GeneralCategory'] = agged_cat_df['SpecificCategory'].map(specific_to_general)

    # current_period_df = agged_cat_df[agged_cat_df['Plot_Date'] == max(agged_cat_df['Plot_Date'])]
    current_period_df = agged_cat_df[agged_cat_df['Plot_Date'] == '23-05']
    curr_inc_df = current_period_df[current_period_df['Sum'] >= 0]
    curr_exp_df = current_period_df[current_period_df['Sum'] < 0].copy()
    curr_exp_df['Sum'] = curr_exp_df['Sum'].map(abs)

    exp_fig = px.sunburst(curr_exp_df, path=['GeneralCategory', 'SpecificCategory'], values='Sum')
    exp_fig.show()

    inc_fig = px.sunburst(curr_inc_df, path=['GeneralCategory', 'SpecificCategory'], values='Sum')
    inc_fig.show()

    # Want to have a comparison to last period's income/expenses
    # Do another sunburst, but with percent changes for each category between the two periods?
    # Switch to go.sunburst and resize (https://plotly.com/python/sunburst-charts/#basic-sunburst-plot-with-gosunburst)
    # Show percentages in hover info (Branchvalues)


def get_acct_balances():
    acct_balances = pd.read_csv('AccountBalances.csv', sep=',')
    acct_balances['Date'] = acct_balances['Date'].map(iso_str_to_date)

    for d in acct_balances['Date'].unique():
        acct_balances.loc[len(acct_balances)] = ['Accounts Total', d, acct_balances[acct_balances['Date'] == d]['Balance'].sum()]

    acct_balances['Plot_Date'] = acct_balances['Date'].apply(to_plot_date, monthly=True)

    acct_balances.sort_values(by=['Date', 'Account'])

    return acct_balances


def calc_acct_balances_mom(acct_balances: pd.DataFrame):
    accts_mom = pd.DataFrame(columns=['Date', 'Account', 'mom_change'])

    for acct_name in acct_balances['Account'].unique():
        acct_logs = acct_balances[acct_balances['Account'] == acct_name]
        log_dates = np.sort(acct_logs['Date'].unique())

        accts_mom.loc[len(accts_mom)] = [log_dates[0], acct_name, 0]

        for i in range(1, len(log_dates)):
            last_amt = acct_logs[acct_logs['Date'] == log_dates[i - 1]]['Balance'].sum()
            curr_amt = acct_logs[acct_logs['Date'] == log_dates[i]]['Balance'].sum()
            mom_change = ((curr_amt - last_amt) / last_amt) if last_amt != 0 else 0
            accts_mom.loc[len(accts_mom)] = [log_dates[i], acct_name, mom_change]

    accts_mom['Plot_Date'] = accts_mom['Date'].apply(to_plot_date, monthly=True)
    return accts_mom


acct_colors = {'Chase Checking 1920': 'blue',
               'TD Ameritrade 5399': 'green',
               'Discover Savings 9401': 'orange',
               'Accounts Total': 'black'}
acct_plot_width = 1200
acct_plot_height = 600


def plot_acct_balances(acct_balances: pd.DataFrame):
    fig = go.Figure()

    for account in acct_balances['Account'].unique():
        records = acct_balances[acct_balances['Account'] == account]
        fig.add_trace(go.Scatter(x=records['Plot_Date'], y=records['Balance'], mode='lines', name=account, line=dict(color=acct_colors[account], width=2)))

    fig.update_layout(width=acct_plot_width, height=acct_plot_height, title='Account Balances', yaxis_title='Amount in USD', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.show()


def plot_acct_balances_mom(acct_balances: pd.DataFrame):
    accts_mom = calc_acct_balances_mom(acct_balances)

    fig = go.Figure()
    for acct_name in accts_mom['Account'].unique():
        records = accts_mom[accts_mom['Account'] == acct_name]
        fig.add_trace(go.Bar(x=records['Plot_Date'], y=records['mom_change'], name=acct_name, marker_color=acct_colors[acct_name]))

    fig.update_layout(barmode='group', width=acct_plot_width, height=acct_plot_height, title='Account Balances MoM Change', yaxis_title='Percentage Change',
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.show()


acct_balances_df = get_acct_balances()
plot_acct_balances(acct_balances_df)
plot_acct_balances_mom(acct_balances_df)


