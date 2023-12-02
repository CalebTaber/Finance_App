import gi
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta


gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from gi.repository import Gio


acct_colors = {'Chase Checking 1920': 'blue',
               'TD Ameritrade 5399': 'green',
               'Discover Savings 9401': 'orange',
               'M&T Bank 5094': 'lightgreen',
               'HSA 4185': 'red',
               'Accounts Total': 'black',
               'Schwab 8407': 'lightblue'}


# Converts string in format YYYY-mm-dd into a date object
def iso_str_to_date(date_str: str):
    return date.fromisoformat(date_str)


# Returns a stringfied version of the given date object
# If monthly, returns in format bbbyy
# Else, returns in format mm/dd/yy
def to_plot_date(input_date: date, monthly: bool):
    return input_date.strftime("%y-%m") if monthly else input_date.strftime("%m/%d/%y")


def generate_monthly_end_dates(begin_date: date, end_date: date):
    end_dates = list()

    for year in range(begin_date.year, end_date.year + 1):
        for month in range(1, 13):
            if (year == begin_date.year) and (month < begin_date.month + 1):
                continue
            if (year == end_date.year) and (month > end_date.month + 1):
                break  # Add 1 to end_date.month because we want to have the last end date be the first day of the next month without any recorded data

            end_dates.append(date(year=year, month=month, day=1))

    return end_dates


# Returns DataFrame of values within the specified date range
def records_within_range(records_df: pd.DataFrame, start_date: date, end_date: date):
    return records_df[(records_df['Date'] >= start_date) & (records_df['Date'] < end_date)].reset_index(drop=True)


# Returns a row of a dataframe that describes the period over period change in gross income, expenses, and net income
def calculate_mom_change(period_begin: date, period_end: date, gross: float, expenses: float, net: float, last_period: pd.DataFrame):
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


def summarize_income_and_expenses(transactions_df: pd.DataFrame, begin_date: date, end_date: date):
    summary_df = pd.DataFrame(
        columns=['Month_Begin', 'Month_End', 'Gross_Income', 'Gross_Income_MoM', 'Expenses', 'Expenses_MoM', 'Net_Income', 'Net_Income_MoM'])

    end_dates = generate_monthly_end_dates(begin_date, end_date)

    # Iterate over periods and compute values for summary dataframe
    start = begin_date
    for end in end_dates:
        month_txns = records_within_range(transactions_df, start, end)

        # Calculate aggregate values for the period
        gross_income = month_txns[month_txns['Amount'] >= 0]['Amount'].sum()
        expenses = np.abs(month_txns[month_txns['Amount'] < 0]['Amount'].sum())
        net_income = gross_income - expenses

        # Calculate MoM values for the period
        prev_month = summary_df[summary_df['Month_End'] == start]
        if len(prev_month) == 0:
            summary_df.loc[len(summary_df)] = [start, end, gross_income, 0, expenses, 0, net_income, 0]
        else:
            summary_df.loc[len(summary_df)] = calculate_mom_change(start, end, gross_income, expenses, net_income, prev_month)

        # Reset start for next iteration
        start = end

    summary_df['Plot_Date'] = summary_df['Month_Begin'].apply(to_plot_date, monthly=True)
    return summary_df


def get_acct_balances(path: str):
    acct_balances = pd.read_csv(path, sep=',')
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


def agg_by_cat(txn_df: pd.DataFrame, start: date, end: date):
    trans_slice_df = records_within_range(txn_df, start, end).copy()
    trans_slice_df['Plot_Date'] = trans_slice_df['Date'].apply(to_plot_date, monthly=True)

    agged_df = pd.DataFrame(columns=['Plot_Date', 'Category', 'Sum'])

    for plotdate in trans_slice_df['Plot_Date'].unique():
        for cat in trans_slice_df['Category'].unique():
            sub_df = trans_slice_df[(trans_slice_df['Plot_Date'] == plotdate) & (trans_slice_df['Category'] == cat)]
            agged_df.loc[len(agged_df)] = [plotdate, cat, sub_df['Amount'].sum()]

    return agged_df


def plot_raw_inc_exp(summary_stats: pd.DataFrame, width: int, height: int) -> None:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=summary_stats['Plot_Date'], y=summary_stats['Gross_Income'], mode='lines', name='Gross Income', line=dict(color='blue', width=2)))
    fig.add_trace(go.Scatter(x=summary_stats['Plot_Date'], y=summary_stats['Expenses'], mode='lines', name='Expenses', line=dict(color='red', width=2)))
    fig.add_trace(go.Scatter(x=summary_stats['Plot_Date'], y=summary_stats['Net_Income'], mode='lines', name='Net Income', line=dict(color='green', width=2)))

    fig.update_layout(width=width, height=height, title='Income and Expenses', yaxis_title='Amount in USD',
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    fig.write_image("Figures/raw_inc_exp.png")


def plot_mom_inc_exp(summary_stats: pd.DataFrame, width: int, height: int):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=summary_stats['Plot_Date'], y=summary_stats['Gross_Income_MoM'], name='Gross Income', marker_color='blue'))
    fig.add_trace(go.Bar(x=summary_stats['Plot_Date'], y=summary_stats['Expenses_MoM'], name='Expenses', marker_color='red'))
    fig.add_trace(go.Bar(x=summary_stats['Plot_Date'], y=summary_stats['Net_Income_MoM'], name='Net Income', marker_color='green'))

    fig.update_layout(barmode='group', width=width, height=height, title='Income and Expenses MoM Change', yaxis_title='Percentage Change',
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    fig.write_image("Figures/mom_inc_exp.png")


def plot_agged_cats(agged_cat_df: pd.DataFrame, width: int, height: int):
    specific_to_general = {
        'Gas': 'Car',
        'Clothes': 'Personal',
        'Groceries': 'Food',
        'Dad': 'People',
        'Dates': 'Dates',
        'Gym': 'Personal',
        'Running': 'Personal',
        'Bike': 'Personal',
        'Gifts': 'Gifts',
        'ECM': 'Job',
        'Personal Care': 'Personal',
        'Spotify': 'Personal',
        'Car Insurance': 'Car',
        'Car Maintenance': 'Car',
        'Car Misc': 'Car',
        'Tolls': 'Car',
        'Parking': 'Car',
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
        'Housewares': 'Housing',
        'Student Loans': 'Loans',
        'Electric': 'Housing',
        'Rent': 'Housing',
        'Internet': 'Housing',
        'Water': 'Housing',
        'Furnishings': 'Housing',
        'Renters Insurance': 'Housing'
    }
    agged_cat_df = agged_cat_df.rename(columns={'Category': 'SpecificCategory'})
    agged_cat_df['GeneralCategory'] = agged_cat_df['SpecificCategory'].map(specific_to_general)

    current_period_df = agged_cat_df[agged_cat_df['Plot_Date'] == max(agged_cat_df['Plot_Date'])]
    current_period_df = agged_cat_df[agged_cat_df['Plot_Date'] == '23-11']

    # TODO don't get agged_cat_df from agg_by_cat(). It takes a simple sum of the category; it does not keep expenses and incomes separate

    curr_inc_df = current_period_df[current_period_df['Sum'] >= 0]
    curr_exp_df = current_period_df[current_period_df['Sum'] < 0].copy()
    curr_exp_df['Sum'] = curr_exp_df['Sum'].map(abs)

    exp_fig = px.sunburst(curr_exp_df, path=['GeneralCategory', 'SpecificCategory'], values='Sum', width=width, height=height)
    exp_fig.write_image("Figures/expenses_agged_by_cat.png")

    inc_fig = px.sunburst(curr_inc_df, path=['GeneralCategory', 'SpecificCategory'], values='Sum', width=width, height=height)
    inc_fig.write_image("Figures/income_agged_by_cat.png")


def plot_acct_balances(acct_balances: pd.DataFrame, width: int, height: int):
    fig = go.Figure()

    for account in acct_balances['Account'].unique():
        records = acct_balances[acct_balances['Account'] == account]
        fig.add_trace(go.Scatter(x=records['Plot_Date'], y=records['Balance'], mode='lines', name=account, line=dict(color=acct_colors[account], width=2)))

    fig.update_layout(width=width, height=height, title='Account Balances', yaxis_title='Amount in USD', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.write_image("Figures/raw_acct_balances.png")


def plot_acct_balances_mom(acct_balances: pd.DataFrame, width: int, height: int):
    accts_mom = calc_acct_balances_mom(acct_balances)

    fig = go.Figure()
    for acct_name in ['Accounts Total']: #accts_mom['Account'].unique():
        records = accts_mom[accts_mom['Account'] == acct_name]
        fig.add_trace(go.Bar(x=records['Plot_Date'], y=records['mom_change'], name=acct_name, marker_color=acct_colors[acct_name]))

    fig.update_layout(barmode='group', width=width, height=height, title='Account Balances MoM Change', yaxis_title='Percentage Change',
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.write_image("Figures/mom_acct_balances.png")


def show(transactions: pd.DataFrame, width: int, height: int):
    start_date = date(year=2023, month=7, day=1)
    end_date = transactions['Date'].max()

    # Income and Expenses
    inc_exp_summary = summarize_income_and_expenses(transactions, start_date, end_date)
    plot_raw_inc_exp(inc_exp_summary, width, height)
    plot_mom_inc_exp(inc_exp_summary, width, height)
    raw_inc_exp_linegraph = Gtk.Picture(file=Gio.File.new_for_path(path="./Figures/raw_inc_exp.png"))
    mom_inc_exp_barchart = Gtk.Picture(file=Gio.File.new_for_path(path="./Figures/mom_inc_exp.png"))

    agged_by_cat = agg_by_cat(transactions, date(year=2023, month=7, day=1), date(year=2023, month=12, day=1))
    plot_agged_cats(agged_by_cat, 600, 600)
    expenses_sunburst = Gtk.Picture(file=Gio.File.new_for_path(path="./Figures/expenses_agged_by_cat.png"))
    income_sunburst = Gtk.Picture(file=Gio.File.new_for_path(path="./Figures/income_agged_by_cat.png"))

    # Account Balances
    acct_balances = records_within_range(get_acct_balances('/home/caleb/Documents/Finances/Dashboard/AccountBalances.csv'), start_date, end_date)
    plot_acct_balances(acct_balances, width, height)
    plot_acct_balances_mom(acct_balances, width, height)
    raw_acct_balances_linegraph = Gtk.Picture(file=Gio.File.new_for_path(path="./Figures/raw_acct_balances.png"))
    mom_acct_balances_barchart = Gtk.Picture(file=Gio.File.new_for_path(path="./Figures/mom_acct_balances.png"))

    window = Gtk.ScrolledWindow(max_content_width=width, min_content_width=width, max_content_height=height, min_content_height=height)
    container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    container.set_size_request(width=width, height=height * 6) # Height factor is the number of plots being displayed

    container.append(raw_inc_exp_linegraph)
    container.append(mom_inc_exp_barchart)
    container.append(raw_acct_balances_linegraph)
    container.append(mom_acct_balances_barchart)
    container.append(expenses_sunburst)
    container.append(income_sunburst)

    window.set_child(container)

    return window
