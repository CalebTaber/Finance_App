import gi
from DatePicker import DatePicker
from TransactionList import TransactionList

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class TransactionInputForm(Gtk.Box):
    date_input = DatePicker()
    amount_input = Gtk.Entry(placeholder_text="Amount")
    submit = Gtk.Button(label="Submit")
    location_input = Gtk.ComboBoxText.new_with_entry()
    location_input.set_entry_text_column(0)
    category_input = Gtk.ComboBoxText.new_with_entry()
    category_input.set_entry_text_column(0)
    description_input = Gtk.Entry(placeholder_text="Description")

    def __init__(self, window_height, txn_list_path):
        super().__init__()
        self.set_size_request(225, window_height)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(5)
        self.set_homogeneous(False)

        self.append(self.date_input)
        self.append(self.amount_input)
        self.append(self.location_input)
        self.append(self.category_input)
        self.append(self.description_input)

        self.submit.connect("clicked", self.on_submit)
        self.append(self.submit)

        self.txn_list = TransactionList(txn_file_path=txn_list_path)

        loc_model = Gtk.ListStore(str)
        for loc in self.txn_list.locations():
            if loc != 'nan':
                self.location_input.append_text(str(loc))
                loc_model.append([loc])

        loc_completion = Gtk.EntryCompletion()
        loc_completion.set_model(loc_model)
        loc_completion.set_text_column(0)
        self.location_input.get_child().set_completion(loc_completion)

        categories = self.txn_list.categories()
        cat_model = Gtk.ListStore(str)
        for cat in categories:
            self.category_input.append_text(str(cat))
            cat_model.append([cat])

        cat_completion = Gtk.EntryCompletion()
        cat_completion.set_model(cat_model)
        cat_completion.set_text_column(0)
        self.category_input.get_child().set_completion(cat_completion)

    def on_submit(self, widget):
        self.txn_list.add_transaction([self.date_input.selected_date,
                                       self.amount_input.get_text(),
                                       self.location_input.get_active_text(),
                                       self.category_input.get_active_text(),
                                       [self.category_input.get_active_text().lower()] +
                                       self.description_input.get_text().split(',')])

    def close(self):
        self.txn_list.write_to_file()
