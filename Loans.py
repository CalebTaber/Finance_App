import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta


# Converts string in format YYYY-mm-dd into a date object
def str_to_date(date_str: str):
    arr = date_str.split('-')
    return date(year=int(arr[0]), month=int(arr[1]), day=int(arr[2]))


def read_loans(path: str):
    loans = pd.read_csv(path, sep=',')
    loans['Disbursement_Date_1'] = loans['Disbursement_Date_1'].map(str_to_date)
    loans['Disbursement_Date_2'] = loans['Disbursement_Date_2'].map(str_to_date, na_action='ignore')
    loans['Disbursed_Amt_2'].fillna(0, inplace=True)
    loans['Due_Date'] = loans['Due_Date'].map(str_to_date)

    return loans


# Returns the length of the given month. If it is a leap year, 29 will be returned for February. If not, 28 will be returned
def days_in_month(year: int, month: int):
    month_lengths = [31, 0, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if month == 2:
        return 29 if (year % 4 == 0) else 28
    return month_lengths[month - 1]


loans = read_loans('Loans.csv')

loans_adjusted = loans.copy()
loans_adjusted['Due_Date'] = loans['Due_Date'].min()


class Loan:
    def __init__(self, ID, principal, interest_rate, accrued_interest):
        self.ID = ID
        self.principal = principal
        self.interest_rate = interest_rate
        self.accrued_interest = accrued_interest

    def __str__(self):
        return f"{self.ID}: ${self.principal} @ {self.interest_rate} (${self.accrued_interest} accrued)"

    def pay_principal(self, payment_amt):
        self.principal -= payment_amt

    def accrue_interest(self):
        self.accrued_interest += self.principal * (self.interest_rate / 12.0)


def monthly_interest(loan: Loan):
    return loan.principal * (loan.interest_rate / 12.0)


def optimize_loan_repayment(loans: list, monthly_payment: float, begin_date: date, deposit_amt: float):
    payment_df = pd.DataFrame(columns=['LoanID', 'Date', 'Amount', 'Outstanding_Balance'])
    balance_remaining = True
    num_periods = 0
    period_date = date(year=begin_date.year, month=begin_date.month, day=begin_date.day)
    remaining_deposit = deposit_amt

    while balance_remaining:
        num_periods += 1
        balance_remaining = False
        remaining_payment = monthly_payment
        pay_first_index = 0

        # Apply deposit to loans before accruing interest
        for i in range(len(loans) - 1, -1, -1):
            if remaining_deposit <= 0:
                break

            amt_to_apply = min(loans[i].principal, remaining_deposit)
            remaining_deposit -= amt_to_apply
            loans[i].pay_principal(amt_to_apply)
            payment_df.loc[len(payment_df)] = [loans[i].ID, period_date, amt_to_apply, loans[i].principal]

        for i in range(0, len(loans)):
            # Pay monthly interest payment on each loan
            loan_interest = monthly_interest(loans[i])
            if remaining_payment >= loan_interest:
                remaining_payment -= loan_interest
                payment_df.loc[len(payment_df)] = [loans[i].ID, period_date, loan_interest, loans[i].principal]
            else:
                print("MONTHLY PAYMENT TOO LOW")
                return

            # Check for a remaining balance
            if loans[i].principal > 0:
                balance_remaining = True

        if not balance_remaining:
            print('Payments:', num_periods)
            return payment_df

        # Sort loans by interest rate and principal
        loans.sort(key=lambda x: (x.interest_rate, x.principal))

        # Apply extra monthly payment to loans
        for i in range(len(loans) - 1, -1, -1):
            if remaining_payment <= 0:
                break

            amt_to_apply = min(loans[i].principal, remaining_payment)
            remaining_payment -= amt_to_apply
            loans[i].pay_principal(amt_to_apply)
            payment_df.loc[len(payment_df)] = [loans[i].ID, period_date, amt_to_apply, loans[i].principal]

        period_date += timedelta(days=days_in_month(period_date.year, period_date.month))

    return payment_df


def plot_loan_repayment_schedule():
    monthly_slider = widgets.IntSlider(value=1000, min=0, max=3000, step=100, description='Monthly Payment')
    deposit_slider = widgets.IntSlider(value=4000, min=0, max=10000, step=500, description='Deposit Amount')
    startdate_picker = widgets.DatePicker(value=date(year=2023, month=9, day=1), description='Start Date')
    plot_btn = widgets.Button(description='Plot')
    output = widgets.Output()


def plot_repayment(button):
    output.clear_output()

    loan_objs = list()
    for i in range(0, len(loans_adjusted)):
        loan_i = loans_adjusted.iloc[i]
        l = Loan(loan_i['LoanID'], loan_i['Principal_Balance'], loan_i['Interest_Rate'], loan_i['Accrued_Interest'])
        loan_objs.append(l)

    with output:
        repayment_schedule = optimize_loan_repayment(loans=loan_objs, monthly_payment=monthly_slider.value, begin_date=startdate_picker.value,
                                                     deposit_amt=deposit_slider.value)

    fig = go.Figure()

    for loanID in repayment_schedule['LoanID'].unique():
        plot_data = repayment_schedule[repayment_schedule['LoanID'] == loanID][['Date', 'Outstanding_Balance']]
        fig.add_trace(go.Scatter(x=plot_data['Date'], y=plot_data['Outstanding_Balance'], mode='lines', name=loanID))

    fig.update_layout(width=1500, height=500)

    with output:
        print('Total paid:', round(repayment_schedule['Amount'].sum(), 2))
        fig.show()


plot_btn.on_click(plot_repayment)
display(monthly_slider, deposit_slider, startdate_picker, plot_btn, output)
