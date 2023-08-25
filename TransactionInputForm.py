import gi
import DatePicker

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class TransactionInputForm(Gtk.Box):
    datePicker = DatePicker.DatePicker()
    amountEntry = Gtk.Entry(placeholder_text="Amount")
    submitBtn = Gtk.Button(label="Submit")

    location_store = Gtk.ListStore(int, str)
    location_store.append([0, "Amazon"])
    location_store.append([1, "Giant"])
    location_store.append([2, "Wegmans"])
    location_store.append([3, "Shoprite"])
    locationEntry = Gtk.ComboBox.new_with_model_and_entry(location_store)
    locationEntry.set_entry_text_column(1)

    category_store = Gtk.ListStore(int, str)
    category_store.append([0, "Groceries"])
    category_store.append([1, "Restaurants"])
    category_store.append([2, "Housing"])
    category_store.append([3, "M&T"])
    category_store.append([4, "Personal"])
    category_store.append([5, "Nonfood Groceries"])
    categoryEntry = Gtk.ComboBox.new_with_model_and_entry(category_store)
    categoryEntry.set_entry_text_column(1)

    def __init__(self, window_height):
        super().__init__(self, width_request=225, height_request=window_height)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(5)
        self.set_homogeneous(False)

        self.add(self.datePicker)
        self.add(self.amountEntry)
        self.add(self.locationEntry)
        self.add(self.categoryEntry)

        self.submitBtn.connect("clicked", self.on_submit)
        self.add(self.submitBtn)

    def on_submit(self, widget):
        print("Submitted!")
