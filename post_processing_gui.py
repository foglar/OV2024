import logging
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, GdkPixbuf

from post_processing import post_processing

# TODO: Image preview of meteor(s) in the GUI
# TODO: Format the meteor data table in the GUI
# TODO: Extract all information from data.txt and convert it to json
# TODO: Configuration window, before


class MeteorApp(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Meteor Plotter")

        self.welcome_dialog()

        self.pp = post_processing()
        self.meteor_data = self.pp.meteor_data_table
        self.index = 1

        self.set_border_width(10)
        self.set_default_size(800, 600)
        header_bar = Gtk.HeaderBar(title="Meteor Plotter")
        header_bar.set_show_close_button(True)
        self.set_titlebar(header_bar)
        m_box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        self.add(m_box)

        index_box = Gtk.Box(
            spacing=10,
            orientation=Gtk.Orientation.VERTICAL,
            halign=Gtk.Align.END,
            valign=Gtk.Align.START,
        )
        m_box.pack_start(index_box, True, True, 0)

        info_box = Gtk.Box(
            spacing=10,
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.START,
            valign=Gtk.Align.START,
        )
        m_box.pack_start(info_box, True, True, 0)

        first_meteor_box = Gtk.Box(
            spacing=10,
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.END,
            valign=Gtk.Align.CENTER,
        )
        info_box.pack_start(first_meteor_box, True, True, 0)

        second_meteor_box = Gtk.Box(
            spacing=10,
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.END,
            valign=Gtk.Align.CENTER,
        )
        info_box.pack_start(second_meteor_box, True, True, 0)

        btn_box = Gtk.Box(
            spacing=60,
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.END,
        )
        m_box.pack_start(btn_box, True, True, 0)

        self.label = Gtk.Label()
        self.update_label()
        self.label.set_justify(Gtk.Justification.LEFT)
        info_box.pack_start(self.label, True, True, 0)

        self.first_meteor_label = Gtk.Label()
        self.first_meteor_label.set_justify(Gtk.Justification.LEFT)
        first_meteor_box.pack_start(self.first_meteor_label, True, True, 0)

        self.second_meteor_label = Gtk.Label()
        self.second_meteor_label.set_justify(Gtk.Justification.LEFT)
        second_meteor_box.pack_start(self.second_meteor_label, True, True, 0)
        self.update_meteors_labels()

        self.index_label = Gtk.Label()
        self.update_index_label()
        self.index_label.set_justify(Gtk.Justification.RIGHT)
        index_box.pack_start(self.index_label, True, True, 0)

        self.btn_view_meteor = Gtk.Button(
            label="Preview Meteor", halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER
        )
        self.btn_view_meteor.connect("clicked", self.on_button_clicked)
        btn_box.pack_start(self.btn_view_meteor, True, True, 0)

        btn_prev_meteor = Gtk.Button(
            label="Previous Meteor", halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER
        )
        btn_prev_meteor.connect("clicked", self.previous_meteor)
        btn_box.pack_start(btn_prev_meteor, True, True, 0)

        btn_next_meteor = Gtk.Button(
            label="Next Meteor", halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER
        )
        btn_next_meteor.connect("clicked", self.next_meteor)
        btn_box.pack_start(btn_next_meteor, True, True, 0)

        btn_save_meteors = Gtk.Button(
            label="Save Meteors", halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER
        )
        btn_save_meteors.connect("clicked", self.save_to_file)
        btn_box.pack_start(btn_save_meteors, True, True, 0)

    def welcome_dialog(self):
        information_dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Welcome to Meteor Plotter!",
        )

        information_dialog.format_secondary_text(
            "Please select the folder containing the meteor data."
        )

        information_dialog.run()
        information_dialog.destroy()

        dialog = Gtk.FileChooserDialog(
            title="Welcome to Meteor Plotter",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            buttons=(
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN,
                Gtk.ResponseType.OK,
            ),
        )

        dialog.set_default_size(800, 400)
        dialog.set_select_multiple(False)
        dialog.set_current_folder(GLib.get_home_dir())

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            folder = dialog.get_filename()
            self.pp = post_processing(folder)
            self.meteor_data = self.pp.meteor_data_table
            self.index = 1
            logging.info(f"Folder selected: {folder}")
        else:
            logging.info("No folder selected. Exiting Meteor Plotter.")
            dialog.destroy()
            Gtk.main_quit()
            return

        dialog.destroy()

        if folder is not None:
            logging.info("Folder selected successfully.", f"Folder: {folder}")
            return folder
        else:
            return None

    def on_button_clicked(self, widget):
        logging.info("Button clicked, processing meteors.")
        self.btn_view_meteor.set_sensitive(False)

        def on_close(event):
            self.btn_view_meteor.set_sensitive(True)
            logging.info("Meteor plot closed.")

        i = self.index - 1
        try:
            data = self.pp.meteor_data_table
            plt, fig = self.pp.plot_meteors(
                [data[i][-5], data[i][-4]],
                data[i][-3],
                data[i][-2],
            )
            fig.canvas.mpl_connect("close_event", on_close)

            plt.show()

            logging.info("Meteors processed successfully.")
        except Exception as e:
            logging.error(f"Error processing meteors: {e}")

    def next_meteor(self, widget):

        self.index += 1
        if self.index > len(self.meteor_data):
            self.index = 1
            logging.info("End of meteor data table reached. Returning to first meteor.")
        else:
            logging.info(f"Next meteor selected. {self.index}")

        self.update_labels()
        return self.meteor_data[self.index - 1]

    def previous_meteor(self, widget):
        self.index -= 1
        if self.index <= 0:
            self.index = len(self.meteor_data)
            logging.info(
                "Start of meteor data table reached. Returning to last meteor."
            )
        else:
            logging.info(f"Previous meteor selected. {self.index}")

        self.update_labels()
        return self.meteor_data[self.index - 1]

    def save_to_file(self, widget):
        logging.info("Saving meteor data to file.")
        try:
            self.pp.write_to_csv()
            logging.info("Meteor data saved successfully.")
            self.info_dialog(
                "Meteor data saved successfully.",
                "Output file is saved at home directory of the observation filetree named overview.csv.",
            )
        except Exception as e:
            logging.error(f"Error saving meteor data: {e}")
            self.error_dialog(f"Error saving meteor data: {e}")

    def info_dialog(self, message, explanation=None):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=message,
        )

        if explanation:
            dialog.format_secondary_text(explanation)

        dialog.run()
        dialog.destroy()

    def error_dialog(self, message, explanation=None):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text=message,
        )

        if explanation:
            dialog.format_secondary_text(explanation)

        dialog.run()
        dialog.destroy()

    def update_labels(self):
        self.update_label()
        self.update_index_label()
        self.update_meteors_labels()

    # def update_image(self):
    # # TODO: Image loading from the meteor data
    # self.image.set_from_file(self.meteor_data[self.index - 1][9])

    def update_label(self):
        # TODO: Relevant meteor data to be displayed in the label and split them into two meteor blocks
        meteor_info = self.meteor_data[self.index - 1]
        label_text = f'<span size="30000">Meteor Information\n</span>'
        label_text += f'<span size="20000">Meteor ID: {meteor_info[0]}\n</span>'
        # label_text += f"<span size=\"20000\">Meteor Date: {meteor_info[1]}\n</span>"
        # label_text += f"<span size=\"20000\">Meteor Time: {meteor_info[2]}\n</span>"
        # label_text += f"<span size=\"20000\">Meteor Time: {meteor_info[3]}\n</span>"
        # label_text += f"<span size=\"20000\">Meteor Detection Type: {meteor_info[4]}\n</span>"
        # label_text += f"<span size=\"20000\">Meteor Detection Type: {meteor_info[5]}\n</span>"
        # label_text += f"<span size=\"20000\">Meteor Magnitude: {meteor_info[6]}\n</span>"
        # label_text += f"<span size=\"20000\">Meteor Velocity: {meteor_info[7]}\n</span>"
        # label_text += f"<span size=\"20000\">Meteor Azimuth: {meteor_info[8]}\n</span>"
        # label_text += f"<span size=\"20000\">Meteor Position: {meteor_info[11][0][0]} X, {meteor_info[11][0][1]} Y, {meteor_info[11][1][0]} X, {meteor_info[11][1][0]} Y\n</span>"
        # label_text += f"<span size=\"20000\">Meteor Position: {meteor_info[12][0][0]} X, {meteor_info[12][0][1]} Y, {meteor_info[12][1][0]} X, {meteor_info[12][1][0]} Y\n</span>"

        self.label.set_markup(label_text)

    def update_index_label(self):
        label_text = f'<span size="20000" >Meteor <b>{self.index}/{len(self.meteor_data)}</b></span>\n'
        self.index_label.set_markup(label_text)

    def update_meteors_labels(self):
        self.update_first_meteor_label()
        self.update_second_meteor_label()

    def update_first_meteor_label(self):
        meteor_info = self.meteor_data[self.index - 1]
        label_text = f'<span size="20000">Meteor ID: {meteor_info[0]}\n</span>'
        label_text += f'<span size="20000">Meteor Date: {meteor_info[1]}\n</span>'
        label_text += f'<span size="20000">Meteor Time: {meteor_info[2]}\n</span>'
        label_text += (
            f'<span size="20000">Meteor Detection Type: {meteor_info[4]}\n</span>'
        )
        label_text += f'<span size="20000">Meteor Magnitude: {meteor_info[6]}\n</span>'
        label_text += f'<span size="20000">Meteor Velocity: {meteor_info[7]}\n</span>'
        label_text += f'<span size="20000">Meteor Azimuth: {meteor_info[8]}\n</span>'
        label_text += f'<span size="20000">Meteor Position: {meteor_info[11][0][0]} X, {meteor_info[11][0][1]} Y, {meteor_info[11][1][0]} X, {meteor_info[11][1][0]} Y\n</span>'

        self.first_meteor_label.set_markup(label_text)

    def update_second_meteor_label(self):
        meteor_info = self.meteor_data[self.index - 1]
        label_text = f'<span size="20000">Meteor ID: {meteor_info[0]}\n</span>'
        label_text += f'<span size="20000">Meteor Date: {meteor_info[1]}\n</span>'
        label_text += f'<span size="20000">Meteor Time: {meteor_info[3]}\n</span>'
        label_text += (
            f'<span size="20000">Meteor Detection Type: {meteor_info[5]}\n</span>'
        )
        label_text += f'<span size="20000">Meteor Magnitude: {meteor_info[6]}\n</span>'
        label_text += f'<span size="20000">Meteor Velocity: {meteor_info[7]}\n</span>'
        label_text += f'<span size="20000">Meteor Azimuth: {meteor_info[8]}\n</span>'
        label_text += f'<span size="20000">Meteor Position: {meteor_info[12][0][0]} X, {meteor_info[12][0][1]} Y, {meteor_info[12][1][0]} X, {meteor_info[12][1][0]} Y\n</span>'

        self.second_meteor_label.set_markup(label_text)


def main():
    logging.basicConfig(level=logging.INFO)

    logging.info("Starting MeteorApp...")
    try:
        win = MeteorApp()
        win.connect("destroy", Gtk.main_quit)
        win.show_all()
        Gtk.main()
    except Exception as e:
        logging.error(f"Error starting GTK application: {e}")


if __name__ == "__main__":
    main()
