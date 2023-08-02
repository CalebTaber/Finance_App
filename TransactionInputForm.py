import gi
import DatePicker

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class TransactionInputForm(Gtk.Box):
    datePicker = DatePicker.DatePicker()
    amountEntry = Gtk.Entry(placeholder_text="Amount")
    locationEntry = Gtk.Entry(placeholder_text="Location")
    categoryEntry = Gtk.ComboBox()
    submitBtn = Gtk.Button(label="Submit")

    def __init__(self):
        super().__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.add(self.datePicker)
        self.add(self.amountEntry)
        self.add(self.locationEntry)
        self.add(self.categoryEntry)

        self.submitBtn.connect("clicked", self.on_submit)
        self.add(self.submitBtn)
        print(self.get_window())

    def on_submit(self, widget):
        print("Submitted!")
