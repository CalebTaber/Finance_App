import gi
import Utilities
from TransactionList import TransactionList
from datetime import date

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class TransactionInputForm(Gtk.FlowBox):
    def __init__(self, window_width, window_height, txn_list_path):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        input_controls_container = Gtk.Box(width_request=225, height_request=window_height, orientation=Gtk.Orientation.VERTICAL, spacing=5, homogeneous=False)

        self.txn_list = TransactionList(width=window_width-225-45, height=window_height, txn_file_path=txn_list_path)

        self.date_input = Gtk.Calendar(visible=True)
        self.amount_input = Gtk.Entry(placeholder_text="Amount")
        self.submit = Gtk.Button(label="Submit")
        self.location_input = Utilities.combobox_text_with_entry_completion(completion_values=[x for x in self.txn_list.locations() if x != 'nan'], text_column_index=0)
        self.category_input = Utilities.combobox_text_with_entry_completion(completion_values=[x for x in self.txn_list.categories() if x != 'nan'], text_column_index=0)
        self.description_input = Gtk.Entry(placeholder_text="Description")

        input_controls_container.append(self.date_input)
        input_controls_container.append(self.amount_input)
        input_controls_container.append(self.location_input)
        input_controls_container.append(self.category_input)
        input_controls_container.append(self.description_input)

        self.submit.connect("clicked", self.on_submit)
        input_controls_container.append(self.submit)

        self.append(input_controls_container)
        self.append(self.txn_list.list_widget)

    def on_submit(self, widget):
        input_date = self.date_input.get_date()
        txn_date = date(year=input_date.get_year(),
                        month=input_date.get_month(),
                        day=input_date.get_day_of_month())

        self.txn_list.add_transaction([txn_date,
                                       self.amount_input.get_text(),
                                       self.location_input.get_active_text(),
                                       self.category_input.get_active_text(),
                                       self.category_input.get_active_text().lower() +
                                       self.description_input.get_text()])

    def close(self):
        self.txn_list.write_to_file()
