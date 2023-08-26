import gi
import DatePicker

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class TransactionInputForm(Gtk.Box):
    date_input = DatePicker.DatePicker()
    amount_input = Gtk.Entry(placeholder_text="Amount")
    submit = Gtk.Button(label="Submit")

    locations = ['Amazon', 'Giant', 'Wegmans', 'Shoprite']
    location_input = Gtk.ComboBoxText.new_with_entry()
    location_input.set_entry_text_column(0)
    for loc in locations:
        location_input.append_text(loc)

    categories = ['Groceries', 'Restaurants', 'Housing', 'M&T', 'Personal', 'Nonfood Groceries']
    category_input = Gtk.ComboBoxText.new_with_entry()
    category_input.set_entry_text_column(0)
    for cat in categories:
        category_input.append_text(cat)

    def __init__(self, window_height):
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

    def on_submit(self, widget):
        if self.date_input.isPicked:
            print(self.date_input.selected_date,
                  self.amount_input.get_text(),
                  self.location_input.get_active_text(),
                  self.category_input.get_active_text(),
                  sep='\t')
