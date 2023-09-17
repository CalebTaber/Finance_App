import gi
import datetime

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

DATE_DEFAULT = datetime.date(year=1970, month=1, day=1)


class DatePicker(Gtk.Box):
    calendar = Gtk.Calendar(visible=True)
    selected_date = DATE_DEFAULT
    select_button = Gtk.Button(visible=True)

    def __init__(self):
        super().__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.calendar.connect("day-selected", self.on_date_chosen)
        self.append(self.calendar)

        self.select_button.connect("clicked", self.on_choose_date)

    def on_choose_date(self, widget):
        self.remove(self.select_button)
        self.append(self.calendar)

    def on_date_chosen(self, widget):
        selection = datetime.date(year=self.calendar.get_date().get_year(),
                                  month=self.calendar.get_date().get_month(),
                                  day=self.calendar.get_date().get_day_of_month())

        self.remove(self.calendar)
        self.select_button.set_label(selection.strftime("%B %d, %Y"))
        self.append(self.select_button)
        self.selected_date = selection
