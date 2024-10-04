import gi
import threading
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from main import MeteorsList



class SpinnerAnimation(Gtk.Window):

    def __init__(self):

        Gtk.Window.__init__(self, title="Spinner")
        self.set_border_width(3)
        self.connect("destroy", Gtk.main_quit)

        self.spinner = Gtk.Spinner()

        self.button = Gtk.ToggleButton("Start Spinning")
        self.button.connect("toggled", self.on_button_toggled)

        self.label = Gtk.Label("Press the button to start the spinner")
        self.label.set_halign(Gtk.Align.CENTER)
        self.label.set_valign(Gtk.Align.CENTER)

        self.table = Gtk.Table(3, 2, True)
        self.table.attach(self.button, 0, 2, 0, 1)
        self.table.attach(self.spinner, 0, 2, 2, 3)

        self.add(self.table)
        self.show_all()

    def loading_some_data(self):
    # Simulate loading data from a file
        try:
            self.meteors = MeteorsList()
            self.ra_dec_list = self.meteors.compare()
        except ConnectionError:
            print("Connection error")
            return
        except Exception as e:
            print(e)
            return

    def on_button_toggled(self, button):
        if button.get_active():
            self.spinner.start()
            self.button.set_label("Stop Spinning")
            # Start the long-running task in a separate thread
            thread = threading.Thread(target=self.load_data_thread)
            thread.start()
        else:
            self.spinner.stop()
            self.button.set_label("Start Spinning")

    def load_data_thread(self):
        self.loading_some_data()
        # Once data loading is done, update the UI in the main thread
        Gtk.main_iteration_do(False)
        self.on_loading_finished()

    def on_loading_finished(self):
        # Stop the spinner when the task is complete
        self.spinner.stop()
        self.button.set_label("Start Spinning")
        print(self.ra_dec_list)
        self.label.set_text(str(self.ra_dec_list[0][0]))
        self.table.attach(self.label, 0, 2, 1, 2)


myspinner = SpinnerAnimation()

Gtk.main()
