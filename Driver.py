import gi
import TransactionInputForm as txnInput

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 400
TXN_PATH = './Data/Transactions_test.csv'
txn_input_form = txnInput.TransactionInputForm(WINDOW_HEIGHT, TXN_PATH)


def on_activate(application: Gtk.Application):
    top_level_layout = Gtk.FlowBox()
    top_level_layout.set_orientation(Gtk.Orientation.HORIZONTAL)
    top_level_layout.append(txn_input_form)
    top_level_layout.append(txn_input_form.txn_list.list_widget)

    app_window = Gtk.ApplicationWindow(application=application)
    app_window.set_title('Finance App')
    app_window.set_size_request(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    app_window.set_child(top_level_layout)
    app_window.present()


def on_exit(window, user_data):
    txn_input_form.close()


main_application = Gtk.Application(application_id='com.example.GtkApplication')
main_application.connect('activate', on_activate)
main_application.connect('window-removed', on_exit)

main_application.run(None)
