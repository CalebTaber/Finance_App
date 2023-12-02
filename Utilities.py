import gi
from datetime import date, datetime

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


def compare(value1, value2, reverse: bool) -> int:
    if value1 < value2:
        return 1 if reverse else -1
    elif value1 > value2:
        return -1 if reverse else 1
    else:
        return 0


def compare_transactions(txn1, txn2) -> int:
    date_comparison = compare(datetime.strptime(txn1.date_buffer.get_text(), "%m-%d-%y").date(),
                              datetime.strptime(txn2.date_buffer.get_text(), "%m-%d-%y").date(),
                              True)

    if date_comparison == 0:
        return compare(float(txn1.amount_buffer.get_text()), float(txn2.amount_buffer.get_text()), False)
    else:
        return date_comparison
