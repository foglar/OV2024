import gi
import threading
import logging

logging.basicConfig(level=logging.DEBUG)

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from main import MeteorsList


class DataWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Spinner")
        self.set_border_width(3)
        self.set_default_size(400, 150)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.delete_event_id = self.connect("delete-event", self.on_delete_event)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox.set_halign(Gtk.Align.CENTER)
        hbox.set_valign(Gtk.Align.CENTER)

        self.spinner = Gtk.Spinner()

        self.label = Gtk.Label("Loading data, please wait... It may take a while.")
        
        hbox.pack_start(self.spinner, False, False, 0)
        hbox.pack_start(self.label, False, False, 0)

        self.add(hbox)

        self.show_all()

        # Start the spinner and background thread
        self.spinner.start()
        self.thread = threading.Thread(target=self.load_data_thread)
        self.thread.start()

    def on_delete_event(self, widget, event):
        """Block the window from closing if data is still loading"""
        logging.info("Data is still loading. Please wait.")
        return True

    def loading_some_data(self):
        """Run meteors.compare() in a separate thread"""
        try:
            self.meteors = MeteorsList()
            self.ra_dec_list = self.meteors.compare()
        except ConnectionError:
            logging.error("Connection error")
            return
        except Exception as e:
            logging.error(f"Failed to load data: {e}")
            return

    def load_data_thread(self):
        self.loading_some_data()
        # Once data loading is done, update the UI in the main thread
        Gtk.main_iteration_do(False)
        self.on_loading_finished()

    def on_loading_finished(self):
        # Stop the spinner when the task is complete
        self.spinner.stop()
        if hasattr(self, 'ra_dec_list') and self.ra_dec_list:
            print(self.ra_dec_list)
            self.label.set_text(f"Data loaded successfully: {len(self.ra_dec_list)} meteors found.")
        else:
            self.label.set_text("Failed to load data.")

        # Now that the task is complete, allow the window to close
        self.destroy()

if __name__ == "__main__":
    win = DataWindow()
    Gtk.main()
