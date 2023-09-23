import gi
import pandas as pd
import numpy as np
from datetime import date

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

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

    def add_transaction(self, values: list):
        (txn_date, amount, location, category, keywords) = values
        self.transaction_df.loc[len(self.transaction_df)] = [txn_date, amount, location, category, keywords]
        print('Added the following transaction:', values)

    def write_to_file(self):
        self.transaction_df['Description Keywords'] = self.transaction_df['Description Keywords'].map(lambda x: ','.join(x)).map(str.lower)
        self.transaction_df.sort_values(by='Date', inplace=True)
        self.transaction_df.to_csv(path_or_buf=self.file_path, index=False, sep=';')

    def display_list(self) -> Gtk.ScrolledWindow:
        window = Gtk.ScrolledWindow()
        window.set_size_request(430, 400)
        window.set_policy(hscrollbar_policy=Gtk.PolicyType.NEVER, vscrollbar_policy=Gtk.PolicyType.AUTOMATIC)

        vbox = Gtk.Box()
        vbox.set_orientation(Gtk.Orientation.VERTICAL)
        for i in range(len(self.transaction_df)):
            row = self.transaction_df.iloc[i]
            new_label = Gtk.Label()

            new_label.set_text(str(row['Date'].strftime("%m-%d-%y")) + "\t"
                               + str(row['Amount']) + "\t"
                               + str(row['Location']) + "\t"
                               + str(row['Category']))
            vbox.append(new_label)
            hseparator = Gtk.Separator()
            hseparator.set_orientation(Gtk.Orientation.HORIZONTAL)
            vbox.append(hseparator)

        window.set_child(vbox)
        return window
