import gi
import TransactionInputForm as txnInput

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class MainWindow(Gtk.Window):
    layout = Gtk.FlowBox()

    def __init__(self):
        super().__init__(title="Finance App")
        self.set_default_size(500, 400)
        self.layout.set_valign(Gtk.Align.START)
        txnInputForm = txnInput.TransactionInputForm()
        self.layout.add(txnInputForm)
        self.add(self.layout)


window = MainWindow()
window.connect("destroy", Gtk.main_quit)
window.show_all()
Gtk.main()