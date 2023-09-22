import gi
import TransactionInputForm as txnInput

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 400


def on_activate(application: Gtk.Application):
    top_level_layout = Gtk.FlowBox()
    txn_input_form = txnInput.TransactionInputForm(WINDOW_HEIGHT, '/home/caleb/Documents/Finances/Dashboard/Transactions.csv')
    top_level_layout.append(txn_input_form)

    app_window = Gtk.ApplicationWindow(application=application)
    app_window.set_default_size(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    app_window.set_child(top_level_layout)
    app_window.present()


main_application = Gtk.Application(application_id='com.example.GtkApplication')
main_application.connect('activate', on_activate)

main_application.run(None)
