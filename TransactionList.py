import pandas as pd
import numpy as np


class TransactionList:
    def __init__(self, txn_file_path):
        self.transaction_df = pd.read_csv(filepath_or_buffer=txn_file_path, sep=';')
        for col_name in ['Date', 'Amount', 'Location', 'Category', 'Description Keywords']:
            assert col_name in self.transaction_df.columns

    def categories(self):
        return np.sort(self.transaction_df['Category'].unique())

    def locations(self):
        locations = self.transaction_df['Location'].unique()
        return np.sort([loc for loc in locations if loc != np.NaN])

    def add_transaction(self, values):
        print('Adding the following transaction:', values)
        # TODO: Append the transaction to the transaction dataframe
