import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class DatePicker(Gtk.Calendar):
    def __init__(self):
        super().__init__()
        self.connect("day-selected", self.on_date_chosen)

    def on_date_chosen(self, widget):
        print("Date chosen:", self.get_date())
