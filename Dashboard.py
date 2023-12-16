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
                break
                # Add 1 to end_date.month because we want to have the last end date be the first day of the next month without any recorded data

            end_dates.append(date(year=year, month=month, day=1))

        if (year == end_date.year) and (end_date.month == 12):
            end_dates.append(date(year=end_date.year + 1, month=1, day=1))

    return end_dates


# Returns DataFrame of values within the specified date range
def records_within_range(records_df: pd.DataFrame, start_date: date, end_date: date):
    return records_df[(records_df['Date'] >= start_date) & (records_df['Date'] < end_date)].reset_index(drop=True)


# Returns a row of a dataframe that describes the period over period change in gross income, expenses, and net income
def income_and_expenses_mom(period_begin: date, period_end: date, gross: float, expenses: float, net: float, last_period: pd.DataFrame):
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


def summarize_income_and_expenses(transactions_df: pd.DataFrame):
    summary_df = pd.DataFrame(
        columns=['Month_Begin', 'Month_End', 'Gross_Income', 'Gross_Income_MoM', 'Expenses', 'Expenses_MoM', 'Net_Income', 'Net_Income_MoM'])

    end_dates = generate_monthly_end_dates(transactions_df['Date'].min(), transactions_df['Date'].max())

    # Iterate over periods and compute values for summary dataframe
    start = transactions_df['Date'].min()
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
            summary_df.loc[len(summary_df)] = income_and_expenses_mom(start, end, gross_income, expenses, net_income, prev_month)

        # Reset start for next iteration
        start = end

    summary_df['Plot_Date'] = summary_df['Month_Begin'].apply(to_plot_date, monthly=True)
    return summary_df


def read_account_balances(path: str):
    acct_balances = pd.read_csv(path, sep=',')
    acct_balances['Date'] = acct_balances['Date'].map(iso_str_to_date)

    for d in acct_balances['Date'].unique():
        acct_balances.loc[len(acct_balances)] = ['Accounts Total', d, acct_balances[acct_balances['Date'] == d]['Balance'].sum()]

    acct_balances['Plot_Date'] = acct_balances['Date'].apply(to_plot_date, monthly=True)

    acct_balances.sort_values(by=['Date', 'Account'])

    return acct_balances


def account_balances_mom(acct_balances: pd.DataFrame):
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


def aggregate_by_category(txn_df: pd.DataFrame) -> pd.DataFrame:
    txn_slice_df = txn_df.copy()
    txn_slice_df['Plot_Date'] = txn_slice_df['Date'].apply(to_plot_date, monthly=True)

    agged_by_cat = pd.DataFrame(columns=['Plot_Date', 'Category', 'Sum'])

    for plot_date in txn_slice_df['Plot_Date'].unique():
        for category in txn_slice_df['Category'].unique():
            sub_df = txn_slice_df[(txn_slice_df['Plot_Date'] == plot_date) & (txn_slice_df['Category'] == category)]
            agged_by_cat.loc[len(agged_by_cat)] = [plot_date, category, sub_df['Amount'].sum()]

    return agged_by_cat


def plot_income_and_expenses(summary_stats: pd.DataFrame, width: int, height: int) -> None:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=summary_stats['Plot_Date'], y=summary_stats['Gross_Income'], mode='lines', name='Gross Income', line=dict(color='blue', width=2)))
    fig.add_trace(go.Scatter(x=summary_stats['Plot_Date'], y=summary_stats['Expenses'], mode='lines', name='Expenses', line=dict(color='red', width=2)))
    fig.add_trace(go.Scatter(x=summary_stats['Plot_Date'], y=summary_stats['Net_Income'], mode='lines', name='Net Income', line=dict(color='green', width=2)))

    fig.update_layout(width=width, height=height, title='Income and Expenses', yaxis_title='Amount in USD',
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    fig.write_image("Figures/raw_inc_exp.png")


def plot_income_and_expenses_mom(summary_stats: pd.DataFrame, width: int, height: int) -> None:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=summary_stats['Plot_Date'], y=summary_stats['Gross_Income_MoM'], name='Gross Income', marker_color='blue'))
    fig.add_trace(go.Bar(x=summary_stats['Plot_Date'], y=summary_stats['Expenses_MoM'], name='Expenses', marker_color='red'))
    fig.add_trace(go.Bar(x=summary_stats['Plot_Date'], y=summary_stats['Net_Income_MoM'], name='Net Income', marker_color='green'))

    fig.update_layout(barmode='group', width=width, height=height, title='Income and Expenses MoM Change', yaxis_title='Percentage Change',
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    fig.write_image("Figures/mom_inc_exp.png")


def plot_income_expenses_sunbursts(agged_cat_df: pd.DataFrame, width: int, height: int) -> None:
    agged_cat_df = agged_cat_df.rename(columns={'Category': 'SpecificCategory'})
    agged_cat_df['GeneralCategory'] = agged_cat_df['SpecificCategory'].map(specific_to_general)

    current_period_df = agged_cat_df[agged_cat_df['Plot_Date'] == agged_cat_df['Plot_Date'].max()]

    # TODO don't get agged_cat_df from agg_by_cat(). It takes a simple sum of the category; it does not keep expenses and incomes separate

    curr_inc_df = current_period_df[current_period_df['Sum'] >= 0]
    curr_exp_df = current_period_df[current_period_df['Sum'] < 0].copy()
    curr_exp_df['Sum'] = curr_exp_df['Sum'].map(abs)

    exp_fig = px.sunburst(curr_exp_df, path=['GeneralCategory', 'SpecificCategory'], values='Sum', width=width, height=height)
    exp_fig.update_traces(textinfo="label+percent parent+value")
    exp_fig.write_image("Figures/expenses_agged_by_cat.png")

    inc_fig = px.sunburst(curr_inc_df, path=['GeneralCategory', 'SpecificCategory'], values='Sum', width=width, height=height)
    inc_fig.update_traces(textinfo="label+percent parent+value")
    inc_fig.write_image("Figures/income_agged_by_cat.png")


def plot_account_balances(acct_balances: pd.DataFrame, width: int, height: int) -> None:
    fig = go.Figure()

    for account in acct_balances['Account'].unique():
        records = acct_balances[acct_balances['Account'] == account]
        fig.add_trace(go.Scatter(x=records['Plot_Date'], y=records['Balance'], mode='lines', name=account, line=dict(color=acct_colors[account], width=2)))

    fig.update_layout(width=width, height=height, title='Account Balances', yaxis_title='Amount in USD',
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.write_image("Figures/raw_acct_balances.png")


def plot_account_balances_mom(acct_balances: pd.DataFrame, width: int, height: int) -> None:
    accounts_mom = account_balances_mom(acct_balances)

    fig = go.Figure()
    for acct_name in ['Accounts Total']:
        records = accounts_mom[accounts_mom['Account'] == acct_name]
        fig.add_trace(go.Bar(x=records['Plot_Date'], y=records['mom_change'], name=acct_name, marker_color=acct_colors[acct_name]))

    fig.update_layout(barmode='group', width=width, height=height, title='Account Balances MoM Change', yaxis_title='Percentage Change',
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.write_image("Figures/mom_acct_balances.png")


def replace_plots(period_transactions: pd.DataFrame, plot_box: Gtk.Box, width: int, height: int):
    # Remove any old plots
    while plot_box.get_first_child() is not None:
        plot_box.remove(plot_box.get_first_child())

    # Income and Expenses
    inc_exp_summary = summarize_income_and_expenses(period_transactions)
    plot_income_and_expenses(inc_exp_summary, width, height)
    plot_income_and_expenses_mom(inc_exp_summary, width, height)
    raw_inc_exp_linegraph = Gtk.Picture(file=Gio.File.new_for_path(path="./Figures/raw_inc_exp.png"), can_shrink=False)
    mom_inc_exp_barchart = Gtk.Picture(file=Gio.File.new_for_path(path="./Figures/mom_inc_exp.png"), can_shrink=False)
    plot_box.append(raw_inc_exp_linegraph)
    plot_box.append(mom_inc_exp_barchart)

    agged_by_cat = aggregate_by_category(period_transactions)
    plot_income_expenses_sunbursts(agged_by_cat, width, width)
    expenses_sunburst = Gtk.Picture(file=Gio.File.new_for_path(path="./Figures/expenses_agged_by_cat.png"), can_shrink=False)
    income_sunburst = Gtk.Picture(file=Gio.File.new_for_path(path="./Figures/income_agged_by_cat.png"), can_shrink=False)
    plot_box.append(expenses_sunburst)
    plot_box.append(income_sunburst)

    # Account Balances
    acct_balances = records_within_range(read_account_balances('/home/caleb/Documents/Finances/Dashboard/AccountBalances.csv'),
                                         date(year=period_transactions['Date'].min().year, month=period_transactions['Date'].min().month, day=1),
                                         date(year=period_transactions['Date'].max().year, month=period_transactions['Date'].max().month, day=1))
    plot_account_balances(acct_balances, width, height)
    plot_account_balances_mom(acct_balances, width, height)
    raw_acct_balances_linegraph = Gtk.Picture(file=Gio.File.new_for_path(path="./Figures/raw_acct_balances.png"), can_shrink=False)
    mom_acct_balances_barchart = Gtk.Picture(file=Gio.File.new_for_path(path="./Figures/mom_acct_balances.png"), can_shrink=False)
    plot_box.append(raw_acct_balances_linegraph)
    plot_box.append(mom_acct_balances_barchart)


def show(transactions: pd.DataFrame, width: int, height: int):
    years = [str(year_num) for year_num in range(transactions['Date'].min().year, transactions['Date'].max().year + 2)]
    months = [str(month_num) for month_num in range(1, 13)]

    plots_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    replace_plots(records_within_range(transactions, date(year=2023, month=7, day=1), transactions['Date'].max()), plots_container, width, height)

    start_year = Gtk.DropDown.new_from_strings(years)
    start_year.set_selected(1) # auto-select 2023
    start_month = Gtk.DropDown.new_from_strings(months)
    start_month.set_selected(6) # auto-select July

    end_year = Gtk.DropDown.new_from_strings(years)
    end_year.set_selected(years.index(str(transactions['Date'].max().year)) + 1 if transactions['Date'].max().month == 12 else years.index(str(transactions['Date'].max().year))) # default to last year in transactions df
    end_month = Gtk.DropDown.new_from_strings(months)
    end_month.set_selected(0 if transactions['Date'].max().month == 12 else transactions['Date'].max().month - 1) # default to last month in transactions df

    plot_button = Gtk.Button(label="Plot")
    plot_button.connect("clicked", lambda button: replace_plots(records_within_range(transactions,
                                                                                     max(date(year=int(start_year.get_selected_item().get_string()),
                                                                                              month=int(start_month.get_selected_item().get_string()),
                                                                                              day=1), transactions['Date'].min()),
                                                                                     min(date(year=int(end_year.get_selected_item().get_string()),
                                                                                              month=int(end_month.get_selected_item().get_string()),
                                                                                              day=1), transactions['Date'].max())
                                                                                     ), plots_container, width, height))

    dropdown_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    dropdown_box.append(Gtk.Label(label="Start: "))
    dropdown_box.append(start_month)
    dropdown_box.append(start_year)
    dropdown_box.append(Gtk.Label(label="End: "))
    dropdown_box.append(end_month)
    dropdown_box.append(end_year)
    dropdown_box.append(plot_button)

    window = Gtk.ScrolledWindow(max_content_width=width, min_content_width=width, max_content_height=height * 2, min_content_height=height * 2)
    container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False)
    container.set_size_request(width=width, height=height * 6)  # Height factor is the number of plots being displayed

    container.append(dropdown_box)
    container.append(plots_container)
    window.set_child(container)

    return window
