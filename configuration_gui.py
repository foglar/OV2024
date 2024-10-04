import logging
import gi
import os
from modules import ConfigLoader as config
from modules import EditConfig as editconfig

# TODO: When opening the configuration window, the values should be loaded from the config file every time

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, GdkPixbuf

class ConfigurationWindow(Gtk.Window):
    def __init__(self):

        self.first_path = config().get_value_from_data("first_observatory", "data")
        self.second_path = config().get_value_from_data("second_observatory", "data")
        self.first_long = config().get_value_from_data("first_longitude", "data")
        self.first_lat = config().get_value_from_data("first_latitude", "data")
        self.first_sealevel = config().get_value_from_data("first_sealevel", "data")
        self.first_timezone = config().get_value_from_data("first_timezone", "data")
        self.second_long = config().get_value_from_data("second_longitude", "data")
        self.second_lat = config().get_value_from_data("second_latitude", "data")
        self.second_sealevel = config().get_value_from_data("second_sealevel", "data")
        self.second_timezone = config().get_value_from_data("second_timezone", "data")
        self.timeout = config().get_value_from_data("timeout", "data")
        self.astrometry_token = config().get_astrometry_key()


        Gtk.Window.__init__(self, title="Configuration")
        self.set_border_width(10)
        self.set_default_size(500, 500)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.connect("destroy", Gtk.main_quit)

        # Header
        self.header = Gtk.HeaderBar()
        self.header.set_show_close_button(True)
        self.header.set_title("Configuration")

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.first_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.second_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.third_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.first_label = Gtk.Label(label="First observatory configuration")
        self.first_label.set_tooltip_text("First observatory configuration")
        self.second_label = Gtk.Label(label="Second observatory configuration")
        self.second_label.set_tooltip_text("Second observatory configuration")
        self.astrometry_label = Gtk.Label(label="Astrometry configuration")
        self.astrometry_label.set_tooltip_text("Astrometry configuration")

        self.grid = Gtk.Grid()
        self.grid.set_column_spacing(10)
        self.grid.set_row_spacing(10)

        self.grid2 = Gtk.Grid()
        self.grid2.set_column_spacing(10)
        self.grid2.set_row_spacing(10)

        self.grid3 = Gtk.Grid()
        self.grid3.set_column_spacing(10)
        self.grid3.set_row_spacing(10)

        # Form for folder, coordinates, sealevel, timezone, etc.

        # Folder
        self.label_folder = Gtk.Label(label="Folder")
        self.entry_folder = Gtk.Entry()
        home = config().get_home_dir()
        try:
            first_folder = config().get_value_from_data("first_observatory", "data")
            if os.path.exists(os.path.join(home, first_folder)):
                first_folder = os.path.join(home, first_folder)
            else:
                first_folder = home
        except KeyError:
            first_folder = home

        try:
            second_folder = config().get_value_from_data("second_observatory", "data")
            if os.path.exists(os.path.join(home, second_folder)):
                second_folder = os.path.join(home, second_folder)
            else:
                second_folder = home
        except KeyError:
            second_folder = home
        
        self.first_path = os.path.join(home, first_folder)
        self.second_path = os.path.join(home, second_folder)

        self.entry_folder.set_text(self.first_path)
        self.button_folder = Gtk.Button(label="...")
        self.button_folder.connect("clicked", self.on_button_select_folder_clicked2)
        self.grid.attach(self.label_folder, 0, 0, 1, 1)
        self.grid.attach(self.entry_folder, 1, 0, 1, 1)
        self.grid.attach(self.button_folder, 3, 0, 1, 1)

        # Coordinates
        self.label_coordinates = Gtk.Label(label="Coordinates")
        self.label_coordinates.set_tooltip_text("Longitude, Latitude")
        self.entry_long = Gtk.Entry()
        self.entry_long.set_text(self.first_long)
        self.entry_long.connect("changed", self.validate_long)
        self.entry_lat = Gtk.Entry()
        self.entry_lat.set_text(self.first_lat)
        self.entry_lat.connect("changed", self.validate_lat)
        self.entry_coordinates = Gtk.Grid()
        self.entry_coordinates.set_column_spacing(10)
        self.entry_coordinates.set_row_spacing(10)
        self.entry_coordinates.attach(self.entry_long, 0, 0, 1, 1)
        self.entry_coordinates.attach(Gtk.Label(label="°,"), 1, 0, 1, 1)
        self.entry_coordinates.attach(self.entry_lat, 2, 0, 1, 1)
        self.entry_coordinates.attach(Gtk.Label(label="°"), 3, 0, 1, 1)
        self.entry_coordinates.set_tooltip_text("Longitude, Latitude")

        self.grid.attach(self.label_coordinates, 0, 1, 1, 1)
        self.grid.attach(self.entry_coordinates, 1, 1, 1, 1)

        # Sealevel
        self.label_sealevel = Gtk.Label(label="Sealevel")
        self.label_sealevel.set_tooltip_text("Sealevel in meters")
        self.sealevel_adjustment = Gtk.Adjustment(int(self.first_sealevel), 0, 10000, 1, 10, 0)
        self.spinner_sealevel = Gtk.SpinButton(adjustment=self.sealevel_adjustment, numeric=True)
        self.spinner_sealevel.set_tooltip_text("Sealevel in meters")
        self.grid.attach(self.label_sealevel, 0, 2, 1, 1)
        self.grid.attach(self.spinner_sealevel, 1, 2, 1, 1)

        # Timezone
        self.label_timezone = Gtk.Label(label="Timezone")
        self.timezone_adjustment = Gtk.Adjustment(int(self.first_timezone), -12, 12, 1, 1, 0)
        self.spinner_timezone = Gtk.SpinButton(adjustment=self.timezone_adjustment, numeric=True)
        self.spinner_timezone.set_tooltip_text("Timezone")
        self.grid.attach(self.label_timezone, 0, 3, 1, 1)
        self.grid.attach(self.spinner_timezone, 1, 3, 1, 1)

        # Second observatory
        self.label_folder2 = Gtk.Label(label="Folder")
        self.entry_folder2 = Gtk.Entry()
        self.entry_folder2.set_text(self.second_path)
        self.button_folder2 = Gtk.Button(label="...")
        self.button_folder2.connect("clicked", self.on_button_select_folder_clicked2)
        self.grid2.attach(self.label_folder2, 0, 0, 1, 1)
        self.grid2.attach(self.entry_folder2, 1, 0, 1, 1)
        self.grid2.attach(self.button_folder2, 3, 0, 1, 1)

        # Coordinates
        self.label_coordinates2 = Gtk.Label(label="Coordinates")
        self.label_coordinates2.set_tooltip_text("Longitude, Latitude")
        self.entry_long2 = Gtk.Entry()
        self.entry_long2.set_text(self.second_long)
        self.entry_long2.connect("changed", self.validate_long)
        self.entry_lat2 = Gtk.Entry()
        self.entry_lat2.set_text(self.second_lat)
        self.entry_lat2.connect("changed", self.validate_lat)
        self.entry_coordinates2 = Gtk.Grid()
        self.entry_coordinates2.set_column_spacing(10)
        self.entry_coordinates2.set_row_spacing(10)
        self.entry_coordinates2.attach(self.entry_long2, 0, 0, 1, 1)
        self.entry_coordinates2.attach(Gtk.Label(label="°,"), 1, 0, 1, 1)
        self.entry_coordinates2.attach(self.entry_lat2, 2, 0, 1, 1)
        self.entry_coordinates2.attach(Gtk.Label(label="°"), 3, 0, 1, 1)
        self.entry_coordinates2.set_tooltip_text("Longitude, Latitude")

        self.grid2.attach(self.label_coordinates2, 0, 1, 1, 1)
        self.grid2.attach(self.entry_coordinates2, 1, 1, 1, 1)

        # Sealevel
        self.label_sealevel2 = Gtk.Label(label="Sealevel")
        self.label_sealevel2.set_tooltip_text("Sealevel in meters")
        self.sealevel_adjustment2 = Gtk.Adjustment(int(self.second_sealevel), 0, 10000, 1, 10, 0)
        self.spinner_sealevel2 = Gtk.SpinButton(adjustment=self.sealevel_adjustment2, numeric=True)
        self.spinner_sealevel2.set_tooltip_text("Sealevel in meters")
        self.grid2.attach(self.label_sealevel2, 0, 2, 1, 1)
        self.grid2.attach(self.spinner_sealevel2, 1, 2, 1, 1)

        # Timezone
        self.label_timezone2 = Gtk.Label(label="Timezone")
        self.timezone_adjustment2 = Gtk.Adjustment(int(self.second_timezone), -12, 12, 1, 1, 0)
        self.spinner_timezone2 = Gtk.SpinButton(adjustment=self.timezone_adjustment2, numeric=True)
        self.spinner_timezone2.set_tooltip_text("Timezone")
        self.grid2.attach(self.label_timezone2, 0, 3, 1, 1)
        self.grid2.attach(self.spinner_timezone2, 1, 3, 1, 1)

        # Astrometry configuration
        # Token
        self.astrometry_sec_label = Gtk.Label(label="Token")
        self.astrometry_sec_label.set_tooltip_text("Astrometry token")
        self.entry_token = Gtk.Entry()
        self.entry_token.set_visibility(False)
        self.entry_token.set_tooltip_text("Astrometry token")
        try:
            token = config().get_astrometry_key()
            self.entry_token.set_text(token)
        except KeyError:
            logging.error("No astrometry token found")

        self.toggle_visibility = Gtk.CheckButton(label="Show token")
        self.toggle_visibility.set_tooltip_text("Show astrometry token")
        self.toggle_visibility.connect("toggled", self.on_toggle_visibility)

        self.grid3.attach(self.astrometry_sec_label, 0, 0, 1, 1)  
        self.grid3.attach(self.entry_token, 1, 0, 1, 1)
        self.grid3.attach(self.toggle_visibility, 3, 0, 1, 1)

        # Timeout
        self.timeout_label = Gtk.Label(label="Timeout")
        self.timeout_label.set_tooltip_text("Timeout in seconds")
        self.timeout_adjustment = Gtk.Adjustment(self.timeout, 0, 1000, 1, 10, 0)
        self.spinner_timeout = Gtk.SpinButton(adjustment=self.timeout_adjustment, numeric=True, climb_rate=1)
        self.spinner_timeout.set_tooltip_text("Timeout in seconds")
        self.grid3.attach(self.timeout_label, 0, 1, 1, 1)
        self.grid3.attach(self.spinner_timeout, 1, 1, 1, 1)

        self.first_box.add(self.first_label)
        self.first_box.add(self.grid)
        self.second_box.add(self.second_label)
        self.second_box.add(self.grid2)
        self.third_box.add(self.astrometry_label)
        self.third_box.add(self.grid3)

        self.box.add(self.first_box)
        self.box.add(self.second_box)
        self.box.add(self.third_box)
        self.add(self.box)

        self.save_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.button_save = Gtk.Button(label="Save")
        self.button_save.connect("clicked", self.on_button_save_clicked)
        self.button_save.set_tooltip_text("Save configuration")
        self.save_box.add(self.button_save)
        self.box.add(self.save_box)
    
    def on_toggle_visibility(self, widget):
        if widget.get_active():
            self.entry_token.set_visibility(True)
        else:
            self.entry_token.set_visibility(False)

    def on_button_select_folder_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a folder", self, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK))
        dialog.set_default_size(800, 400)
        dialog.set_current_folder(self.entry_folder.get_text())
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.entry_folder.set_text(dialog.get_filename())
        dialog.destroy()

    def on_button_select_folder_clicked2(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a folder", self, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK))
        dialog.set_default_size(800, 400)
        dialog.set_current_folder(self.entry_folder2.get_text())
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.entry_folder2.set_text(dialog.get_filename())
        dialog.destroy()
        
    def on_button_save_clicked(self, widget):
        logging.info("Configuration saved")
        # Save configuration
        first_obs = self.entry_folder.get_text().split("/")[-1]
        second_obs = self.entry_folder2.get_text().split("/")[-1]
        editconfig().set_value("first_observatory",first_obs, "data")
        editconfig().set_value("second_observatory", second_obs, "data")
        editconfig().set_value("first_longitude", self.entry_long.get_text(), "data")
        editconfig().set_value("first_latitude", self.entry_lat.get_text(), "data")
        editconfig().set_value("first_sealevel", self.spinner_sealevel.get_value(), "data")
        editconfig().set_value("first_timezone", self.spinner_timezone.get_value(), "data")
        editconfig().set_value("second_longitude", self.entry_long2.get_text(), "data")
        editconfig().set_value("second_latitude", self.entry_lat2.get_text(), "data")
        editconfig().set_value("second_sealevel", self.spinner_sealevel2.get_value(), "data")
        editconfig().set_value("second_timezone", self.spinner_timezone2.get_value(), "data")
        editconfig().set_value("timeout", self.spinner_timeout.get_value(), "data")
        self.destroy()

    def validate_long(self, widget):
        # Validate long input
        if widget.get_text() == "":
            return
        try:
            long = float(widget.get_text())
            if long < -180 or long > 180:
                widget.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "dialog-warning")
                widget.set_icon_tooltip_text(Gtk.EntryIconPosition.SECONDARY, "Longitude must be between -180 and 180")
            else:
                widget.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)
        except ValueError:
            widget.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "dialog-warning")
            widget.set_icon_tooltip_text(Gtk.EntryIconPosition.SECONDARY, "Longitude must be a number")

    def validate_lat(self, widget):
        if widget.get_text() == "":
            return
        try:
            lat = float(widget.get_text())
            if lat < -90 or lat > 90:
                widget.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "dialog-warning")
                widget.set_icon_tooltip_text(Gtk.EntryIconPosition.SECONDARY, "Latitude must be between -90 and 90")
            else:
                widget.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)
        except ValueError:
            widget.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "dialog-warning")
            widget.set_icon_tooltip_text(Gtk.EntryIconPosition.SECONDARY, "Latitude must be a number")

def main():
    try:
        win = ConfigurationWindow()
        win.connect("destroy", Gtk.main_quit)
        win.show_all()
        Gtk.main()
    except Exception as e:
        logging.error(f"Error starting GTK application: {e}")

if __name__ == "__main__":
    main()
