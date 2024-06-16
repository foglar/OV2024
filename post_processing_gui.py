import logging
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from post_processing import post_processing


class MeteorApp(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Meteor Plotter")

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

        index_box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.END, valign=Gtk.Align.START)
        m_box.pack_start(index_box, True, True, 0)

        info_box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.START, valign=Gtk.Align.START)
        m_box.pack_start(info_box, True, True, 0)

        btn_box = Gtk.Box(spacing=60, orientation=Gtk.Orientation.HORIZONTAL, halign=Gtk.Align.CENTER, valign=Gtk.Align.END)
        m_box.pack_start(btn_box, True, True, 0)

        self.index_label = Gtk.Label()
        self.update_index_label()
        self.index_label.set_justify(Gtk.Justification.RIGHT)
        index_box.pack_start(self.index_label, True, True, 0)

        self.label = Gtk.Label()
        self.update_label()
        self.label.set_justify(Gtk.Justification.LEFT)
        info_box.pack_start(self.label, True, True, 0)

        btn_view_meteor = Gtk.Button(label="Preview Meteor", halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        btn_view_meteor.connect("clicked", self.on_button_clicked)
        btn_box.pack_start(btn_view_meteor, True, True, 0)

        btn_prev_meteor = Gtk.Button(label="Previous Meteor", halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        btn_prev_meteor.connect("clicked", self.previous_meteor)
        btn_box.pack_start(btn_prev_meteor, True, True, 0)

        btn_next_meteor = Gtk.Button(label="Next Meteor", halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        btn_next_meteor.connect("clicked", self.next_meteor)
        btn_box.pack_start(btn_next_meteor, True, True, 0)

        btn_save_meteors = Gtk.Button(label="Save Meteors", halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        btn_save_meteors.connect("clicked", self.save_to_file)
        btn_box.pack_start(btn_save_meteors, True, True, 0)

    def on_button_clicked(self, widget):
        logging.info("Button clicked, processing meteors.")
        try:
            data = self.pp.meteor_data_table
            self.pp.plot_meteors(
                [data[self.index][-4], data[self.index][-3]],
                data[self.index][-2],
                data[self.index][-1],
            )

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
        return self.meteor_data[self.index-1]

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
        return self.meteor_data[self.index-1]
    
    def save_to_file(self, widget):
        logging.info("Saving meteor data to file.")
        try:
            self.pp.write_to_csv()
            logging.info("Meteor data saved successfully.")
            self.info_dialog("Meteor data saved successfully.", "Output file is saved at home directory of the observation filetree named overview.csv.")
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

    def update_label(self):
        meteor_info = self.meteor_data[self.index - 1]
        label_text = "\n".join(map(str, meteor_info))  # Assuming meteor_info is a list of strings or numbers
        self.label.set_markup(label_text)

    def update_index_label(self):
        label_text = f"<span size=\"20000\" >Meteor {self.index}/{len(self.meteor_data)}</span>\n"
        self.index_label.set_markup(label_text)

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
