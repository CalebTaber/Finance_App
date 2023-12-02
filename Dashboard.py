import gi
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date, timedelta


gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from gi.repository import Gio


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
def records_within_range(transactions_df: pd.DataFrame, start_date: date, end_date: date):
    return transactions_df[(transactions_df['Date'] >= start_date) & (transactions_df['Date'] < end_date)].reset_index(drop=True)


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


def show(transactions: pd.DataFrame, width: int, height: int):
    inc_exp_summary = summarize_income_and_expenses(transactions, date(year=2023, month=7, day=1), date(year=2023, month=12, day=1))
    plot_raw_inc_exp(inc_exp_summary, width, height)
    plot_mom_inc_exp(inc_exp_summary, width, height)

    raw_inc_exp_linegraph = Gtk.Picture(file=Gio.File.new_for_path(path="./Figures/raw_inc_exp.png"))
    mom_inc_exp_barchart = Gtk.Picture(file=Gio.File.new_for_path(path="./Figures/mom_inc_exp.png"))

    window = Gtk.ScrolledWindow(max_content_width=width, min_content_width=width, max_content_height=height, min_content_height=height)
    container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    container.set_size_request(width=width, height=height * 2)

    container.append(raw_inc_exp_linegraph)
    container.append(mom_inc_exp_barchart)

    window.set_child(container)

    return window
