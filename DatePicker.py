import gi
from datetime import date

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class DatePicker(Gtk.Box):
    calendar = Gtk.Calendar(visible=True)

    def __init__(self):
        super().__init__()
        self.selected_date = date.today()
        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.calendar.connect("day-selected", self.on_date_chosen)
        self.append(self.calendar)

    def on_date_chosen(self, widget):
        selection = date(year=self.calendar.get_date().get_year(),
                         month=self.calendar.get_date().get_month(),
                         day=self.calendar.get_date().get_day_of_month())

        self.selected_date = selection
