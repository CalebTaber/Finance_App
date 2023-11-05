import gi

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
