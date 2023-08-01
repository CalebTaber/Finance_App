import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class TransactionInputForm(Gtk.Box):
    dateEntry = Gtk.Entry(placeholder_text="Date")
    amountEntry = Gtk.Entry(placeholder_text="Amount")
    locationEntry = Gtk.Entry(placeholder_text="Location")
    categoryEntry = Gtk.ComboBox()
    submitBtn = Gtk.Button(label="Submit")

    def __init__(self):
        super().__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.add(self.dateEntry)
        self.add(self.amountEntry)
        self.add(self.locationEntry)
        self.add(self.categoryEntry)

        self.submitBtn.connect("clicked", self.on_submit)
        self.add(self.submitBtn)

    def on_submit(self, widget):
        print("Submitted!")
