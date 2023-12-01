import gi
from datetime import date

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


def combobox_text_with_entry_completion(completion_values: list, text_column_index: int) -> Gtk.ComboBoxText:
    """Create and return a Gtk.ComboBoxText with completion"""
    combobox = Gtk.ComboBoxText.new_with_entry()

    model = Gtk.ListStore(str)
    for value in completion_values:
        model.append([value])
        combobox.append_text(str(value))

    completion = Gtk.EntryCompletion()
    completion.set_model(model)
    completion.set_text_column(text_column_index)

    combobox.get_child().set_completion(completion)
    combobox.set_entry_text_column(text_column_index)
    return combobox


def compare_dates(date1: date, date2: date) -> int:
    """Perform c-style comparison of two dates. Useful for Gtk.ListBox sort_func when sorting by date"""
    if date1 < date2:
        return 1
    elif date1 > date2:
        return -1
    else:
        return 0
