import gi
import logging

logging.basicConfig(level=logging.DEBUG)

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf
from post_processing import post_processing


class MeteorsListGui(Gtk.Window):

    def __init__(self, meteors_list):
        Gtk.Window.__init__(self, title="Meteor List")
        self.meteor_data = meteors_list

        self.set_border_width(10)
        self.set_default_size(800, 600)
        self.set_resizable(True)
        self.header_bar = Gtk.HeaderBar(title="Meteor List")
        self.header_bar.set_show_close_button(True)
        self.set_titlebar(self.header_bar)

        length = len(self.meteor_data)
        m_box = Gtk.Table(n_rows=length, n_columns=7, homogeneous=False)
        m_box.set_row_spacings(5)
        m_box.set_col_spacings(10)
        self.add(m_box)

        for i in range(length):
            meteor = self.meteor_data[i]
            time_str = meteor[1] + " " + meteor[2]
            time_str1 = meteor[1] + " " + meteor[3]

            obs = meteor[9].split("/")[-3]
            obs1 = meteor[10].split("/")[-3]

            img_path = meteor[9]
            img1_path = meteor[10]

            img = GdkPixbuf.Pixbuf.new_from_file_at_scale(img_path, 100, 100, True)
            img1 = GdkPixbuf.Pixbuf.new_from_file_at_scale(img1_path, 100, 100, True)

            imgf = Gtk.Image()
            imgf.set_from_pixbuf(img)
            img1f = Gtk.Image()
            img1f.set_from_pixbuf(img1)

            m_box.attach(Gtk.Label(label=meteor[0]), 0, 1, i, i + 1)
            m_box.attach(Gtk.Label(label=obs), 1, 2, i, i + 1)
            m_box.attach(Gtk.Label(label=time_str), 2, 3, i, i + 1)
            m_box.attach(imgf, 3, 4, i, i + 1)
            m_box.attach(Gtk.Label(label=obs1), 4, 5, i, i + 1)
            m_box.attach(Gtk.Label(label=time_str1), 5, 6, i, i + 1)
            m_box.attach(img1f, 6, 7, i, i + 1)


if __name__ == "__main__":
    meteors_list = post_processing().meteor_data_table
    meteors_list_gui = MetorListGui(meteors_list)
    meteors_list_gui.connect("destroy", Gtk.main_quit)
    meteors_list_gui.show_all()
    Gtk.main()
