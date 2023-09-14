import gi
import DatePicker
import pandas as pd
import numpy as np

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class TransactionInputForm(Gtk.Box):
    date_input = DatePicker.DatePicker()
    amount_input = Gtk.Entry(placeholder_text="Amount")
    submit = Gtk.Button(label="Submit")
    location_input = Gtk.ComboBoxText.new_with_entry()
    location_input.set_entry_text_column(0)
    category_input = Gtk.ComboBoxText.new_with_entry()
    category_input.set_entry_text_column(0)

    transactions_df = pd.DataFrame()

    def __init__(self, window_height, txn_list_path):
        super().__init__(self, width_request=225, height_request=window_height)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(5)
        self.set_homogeneous(False)

        self.add(self.date_input)
        self.add(self.amount_input)
        self.add(self.location_input)
        self.add(self.category_input)

        self.submit.connect("clicked", self.on_submit)
        self.add(self.submit)

        self.transactions_df = pd.read_csv(txn_list_path, sep=';')

        locations = self.transactions_df['Location'].unique()
        loc_model = Gtk.ListStore(str)
        for loc in np.sort([l for l in locations if str(l) != 'nan']):
            if loc != 'nan':
                self.location_input.append_text(str(loc))
                loc_model.append([loc])

        loc_completion = Gtk.EntryCompletion()
        loc_completion.set_model(loc_model)
        loc_completion.set_text_column(0)
        self.location_input.get_child().set_completion(loc_completion)

        categories = np.sort(self.transactions_df['Category'].unique())
        cat_model = Gtk.ListStore(str)
        for cat in categories:
            self.category_input.append_text(str(cat))
            cat_model.append([cat])

        cat_completion = Gtk.EntryCompletion()
        cat_completion.set_model(cat_model)
        cat_completion.set_text_column(0)
        self.category_input.get_child().set_completion(cat_completion)

    def on_submit(self, widget):
        if self.date_input.isPicked:
            print(self.date_input.selected_date,
                  self.amount_input.get_text(),
                  self.location_input.get_active_text(),
                  self.category_input.get_active_text(),
                  sep='\t')
