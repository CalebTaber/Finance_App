import gi
import datetime

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

DATE_DEFAULT = datetime.date(year=1970, month=1, day=1)


class DatePicker(Gtk.Box):
    calendar = Gtk.Calendar(visible=True)
    selected_date = DATE_DEFAULT
    select_button = Gtk.Button(visible=True)
    isPicked = False

    def __init__(self):
        super().__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.calendar.connect("day-selected", self.on_date_chosen)
        self.add(self.calendar)

        self.select_button.connect("clicked", self.on_choose_date)

    def on_choose_date(self, widget):
        self.remove(self.select_button)
        self.add(self.calendar)
        self.isPicked = False

    def on_date_chosen(self, widget):
        (year, month, day) = self.calendar.get_date()
        selection = datetime.date(year=year, month=month + 1, day=day)

        prev_selection = datetime.date.today() if self.selected_date == DATE_DEFAULT else self.selected_date
        month_changed = abs(selection.month - prev_selection.month) == 1 or abs(selection.year - prev_selection.year) == 1

        # Prevent automatically selecting a date when the user changes the month in the calendar
        if not month_changed:
            self.remove(self.calendar)
            self.select_button.set_label(selection.strftime("%B %d, %Y"))
            self.add(self.select_button)
            self.isPicked = True

        self.selected_date = selection
