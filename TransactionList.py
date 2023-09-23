import pandas as pd
import numpy as np
from datetime import date

class TransactionList:
    def __init__(self, txn_file_path):
        self.file_path = txn_file_path
        self.transaction_df = pd.read_csv(filepath_or_buffer=txn_file_path, sep=';')
        for col_name in ['Date', 'Amount', 'Location', 'Category', 'Description Keywords']:
            assert col_name in self.transaction_df.columns
        self.transaction_df['Date'] = self.transaction_df['Date'].map(lambda x: date.fromisoformat(x))
        self.transaction_df['Description Keywords'] = self.transaction_df['Description Keywords'].apply(str.split, sep=',')

    def categories(self):
        return np.sort(self.transaction_df['Category'].unique())

    def locations(self):
        locations = self.transaction_df['Location'].unique()
        return np.sort([loc for loc in locations if loc != np.NaN])

    def add_transaction(self, values):
        (date, amt, loc, cat, kwds) = values
        self.transaction_df.loc[len(self.transaction_df)] = [date, amt, loc, cat, kwds]
        print('Added the following transaction:', values)

    def write_to_file(self):
        self.transaction_df['Description Keywords'] = self.transaction_df['Description Keywords'].map(lambda x: ','.join(x)).map(str.lower)
        self.transaction_df.sort_values(by='Date', inplace=True)
        self.transaction_df.to_csv(path_or_buf=self.file_path, index=False, sep=';')
