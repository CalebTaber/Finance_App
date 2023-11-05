import gi
import pandas as pd
import numpy as np
from datetime import date

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class TransactionListItem(Gtk.Box):
    def __init__(self, fields):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, homogeneous=False)

        for item in fields:
            self.append(Gtk.Label(label=item))


class TransactionList:
    def __init__(self, width, height, txn_file_path: str):
        self.file_path = txn_file_path
        self.transaction_df = pd.read_csv(filepath_or_buffer=txn_file_path, sep=';')

        # Ensure the input file has the correct schema
        for col_name in ['Date', 'Amount', 'Location', 'Category', 'Description Keywords']:
            if col_name not in self.transaction_df.columns:
                raise Exception("Invalid data file schema input to TransactionList object constructor:", self.transaction_df.columns)

        # Format columns after reading from file
        self.transaction_df['Date'] = self.transaction_df['Date'].map(lambda x: date.fromisoformat(x))
        self.transaction_df['Description Keywords'] = self.transaction_df['Description Keywords'].apply(str.split, sep=',')

        # Set up list widget
        self.list_widget = Gtk.ScrolledWindow(width_request=width,
                                              height_request=height,
                                              hscrollbar_policy=Gtk.PolicyType.NEVER,
                                              vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
                                              max_content_height=height)

        list_box = Gtk.ListBox(width_request=width, height_request=height, show_separators=True)
        for i in range(len(self.transaction_df)):
            row = self.transaction_df.iloc[i]

            row_item = TransactionListItem([str(row['Date'].strftime("%m-%d-%y")),
                                            str(row['Amount']),
                                            str(row['Location']),
                                            str(row['Category'])])

            list_box.prepend(row_item)

        self.list_widget.set_child(list_box)

    def categories(self):
        return np.sort(self.transaction_df['Category'].unique())

    def locations(self):
        locations = self.transaction_df['Location'].unique()
        return np.sort([loc for loc in locations if loc != np.NaN])

    def add_transaction(self, values: list):
        self.transaction_df.loc[len(self.transaction_df)] = values
        self.list_widget.get_child().get_child().prepend(TransactionListItem(values[:-1]))

    def write_to_file(self):
        self.transaction_df['Description Keywords'] = self.transaction_df['Description Keywords'].map(lambda x: ','.join(x)).map(str.lower)
        self.transaction_df.sort_values(by='Date', inplace=True)
        self.transaction_df.to_csv(path_or_buf=self.file_path, index=False, sep=';')
