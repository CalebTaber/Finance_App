import gi
import TransactionInputForm as txnInput
import Dashboard

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

main_application = Gtk.Application(application_id='Finance.App')

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 400
TXN_PATH = '/home/caleb/Documents/Finances/Dashboard/Transactions.csv'

top_level_layout = Gtk.Notebook()
txn_input_form = txnInput.TransactionInputForm(WINDOW_WIDTH, WINDOW_HEIGHT, TXN_PATH)

dashboard_box = Gtk.FlowBox(homogeneous=False)


def box_remove_all_children(box):
    while box.get_child_at_index(0) is not None:
        box.remove(box.get_child_at_index(0))


def switch_page(notebook, page, page_num):
    if page_num == 0:
        box_remove_all_children(dashboard_box)
        dashboard_box.set_size_request(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        notebook.set_size_request(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    elif page_num == 1:
        box_remove_all_children(dashboard_box)
        dashboard_box.append(Dashboard.show(txn_input_form.txn_list.transaction_df, WINDOW_WIDTH, WINDOW_HEIGHT))


def on_activate(application: Gtk.Application):
    top_level_layout.append_page(txn_input_form, Gtk.Label(label="Transactions"))
    dashboard_box.append(Gtk.Label(label="Test"))
    top_level_layout.insert_page(dashboard_box, Gtk.Label(label="Dashboard"), 1)

    app_window = Gtk.ApplicationWindow(application=application)
    top_level_layout.connect("switch-page", switch_page)

    app_window.set_title('Finance App')
    app_window.set_size_request(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    app_window.set_child(top_level_layout)
    app_window.present()


def on_exit(window, user_data):
    txn_input_form.close()


main_application.connect('activate', on_activate)
main_application.connect('window-removed', on_exit)

main_application.run(None)
