import gi
import pandas as pd
import numpy as np
from datetime import date

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class TransactionListItem(Gtk.Box):
    def set_editable(self, make_editable):
        if self.editable is False and make_editable is True:
            # Remove the label widgets
            self.remove(self.date_label)
            self.remove(self.amount_label)
            self.remove(self.location_label)
            self.remove(self.category_label)

            # Add the Entry widgets
            self.append(self.done_checkmark)
            self.append(self.date_input)
            self.append(self.amount_input)
            self.append(self.location_input)
            self.append(self.category_input)

            self.editable = True
        elif self.editable is True and make_editable is False:
            # Remove the Entry widgets
            self.remove(self.date_input)
            self.remove(self.amount_input)
            self.remove(self.location_input)
            self.remove(self.category_input)
            self.remove(self.done_checkmark)

            # Update the displayed values
            self.date_label.set_label(self.date_buffer.get_text())
            self.amount_label.set_label(self.amount_buffer.get_text())
            self.location_label.set_label(self.location_buffer.get_text())
            self.category_label.set_label(self.category_buffer.get_text())

            # Add the Label widgets
            self.append(self.date_label)
            self.append(self.amount_label)
            self.append(self.location_label)
            self.append(self.category_label)

            self.editable = False

    def __init__(self, fields):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=5, homogeneous=False)
        self.set_homogeneous(False)

        # These buffers will be shared between the Entry and Label widgets
        self.date_buffer = Gtk.EntryBuffer(text=str(fields[0]))
        self.amount_buffer = Gtk.EntryBuffer(text=str(fields[1]))
        self.location_buffer = Gtk.EntryBuffer(text=str(fields[2]))
        self.category_buffer = Gtk.EntryBuffer(text=str(fields[3]))

        # Label widgets
        self.date_label = Gtk.Label(label=self.date_buffer.get_text())
        self.amount_label = Gtk.Label(label=self.amount_buffer.get_text())
        self.location_label = Gtk.Label(label=self.location_buffer.get_text())
        self.category_label = Gtk.Label(label=self.category_buffer.get_text())

        # Entry widgets
        self.date_input = Gtk.Entry.new_with_buffer(buffer=self.date_buffer)
        self.amount_input = Gtk.Entry.new_with_buffer(buffer=self.amount_buffer)
        self.location_input = Gtk.Entry.new_with_buffer(buffer=self.location_buffer)
        self.category_input = Gtk.Entry.new_with_buffer(buffer=self.category_buffer)
        self.done_checkmark = Gtk.Label(label="  ✅ ")

        # Initialize as non-editable with the Label widgets displayed
        self.editable = False
        self.append(self.date_label)
        self.append(self.amount_label)
        self.append(self.location_label)
        self.append(self.category_label)


NO_ROW = -1


class TransactionList:
    def on_row_selected(self, box, row):
        print("previous selection:", self.selected_row_index)
        # If row is current selected, set to be non-editable and set current to NO_ROW
        # If row is not current selected, set current selected to non-editable, set current selected to be this row, and set this row to be editable

        # Set any previously edited rows as not editable
        if row is not None:
            if row.get_index() == self.selected_row_index:
                # If current selected row is selected again, set it to non-editable and change the selected row to NO_ROW
                box.get_row_at_index(self.selected_row_index).get_child().set_editable(False)
                self.selected_row_index = NO_ROW
            else:
                # If a different row is selected, set the currently selected row to non-editable and set the newly selected row to editable
                if self.selected_row_index != NO_ROW:
                    box.get_row_at_index(self.selected_row_index).get_child().set_editable(False)

                self.selected_row_index = row.get_index()
                print("row", self.selected_row_index, "selected")
                row.get_child().set_editable(True)

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

        self.list_box = Gtk.ListBox(width_request=width, height_request=height, show_separators=True, activate_on_single_click=False)
        for i in range(len(self.transaction_df)):
            row = self.transaction_df.iloc[i]

            row_item = TransactionListItem([str(row['Date'].strftime("%m-%d-%y")),
                                            str(row['Amount']),
                                            str(row['Location']),
                                            str(row['Category'])])

            self.list_box.prepend(row_item)

        self.selected_row_index = NO_ROW

        self.list_box.connect("row_selected", self.on_row_selected)
        self.list_widget.set_child(self.list_box)

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
