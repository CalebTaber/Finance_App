import gi
import TransactionInputForm as txnInput

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 400


# class MainWindow:
#     layout = Gtk.FlowBox()
#
#     def __init__(self):
#         super().__init__(title="Finance App")
#         self.set_default_size(500, 400)
#         self.layout.set_valign(Gtk.Align.START)
#
#         self.layout.append(txn_input)
#
#         self.append(self.layout)


def on_activate(app):
    win = Gtk.ApplicationWindow(application=app)
    layout = Gtk.FlowBox()
    txn_input = txnInput.TransactionInputForm(WINDOW_HEIGHT, '/home/caleb/Documents/Finances/Dashboard/Transactions.csv')
    layout.append(txn_input)
    win.set_child(layout)
    win.present()


app = Gtk.Application(application_id='com.example.GtkApplication')
app.connect('activate', on_activate)

# Run the application
app.run(None)
