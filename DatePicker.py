import gi
import datetime

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

DATE_DEFAULT = datetime.date(year=1970, month=1, day=1)

class DatePicker(Gtk.Box):
    calendar = Gtk.Calendar()
    selected_date = DATE_DEFAULT
    select_button = Gtk.Button(visible=False)

    def __init__(self):
        super().__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.calendar.set_visible(True)
        self.calendar.connect("day-selected", self.on_date_chosen)
        self.add(self.calendar)

        self.select_button.connect("clicked", self.on_choose_date)
        self.add(self.select_button)

    def on_choose_date(self, widget):
        self.select_button.set_visible(False)
        self.calendar.set_visible(True)

    def on_date_chosen(self, widget):
        date_tuple = self.calendar.get_date()
        selection = datetime.date(year=date_tuple[0], month=date_tuple[1] + 1, day=date_tuple[2])

        # If the user is not just changing the month in the calendar, set the current selection as the date
        if not (self.selected_date == DATE_DEFAULT or
                (selection.month == self.selected_date.month - 1 or
                 selection.year == self.selected_date.year - 1) or
                (selection.month == self.selected_date.month + 1 or
                 selection.year == self.selected_date.year + 1)):
            self.calendar.set_visible(False)
            self.select_button.set_label(selection.strftime("%b %d, %Y"))
            self.select_button.set_visible(True)

        self.selected_date = selection
