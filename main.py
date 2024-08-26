import dearpygui.dearpygui as dpg
from scipy.io import wavfile
from math import sin

dpg.create_context()

files = []


class WavData:
    def __init__(self, path, update_callback):
        self._path = path
        self.samplerate, self.data = wavfile.read(path)
        print(f'samplerate: {self.samplerate} data length: {len(self.data)}')
        self.l = []
        self.r = []
        for i, v in enumerate(self.data):
            self.l.append(v[0])
            self.r.append(v[1])
        # dpg.add_same_line()
        h = dpg.add_collapsing_header(label=path, parent='draw_items', default_open=True)

        g = dpg.add_group(horizontal=True, parent=h)
        self.begin_slider_id = dpg.add_input_int(label='begin', parent=g, min_value=0, max_value=len(self.data), default_value=0, width=200, step_fast=100, callback=lambda : update_callback())
        self.end_slider_id = dpg.add_input_int(label='end', parent=g, min_value=0, max_value=len(self.data), default_value=len(self.data), width=200, step_fast=100, callback=lambda : update_callback())


    def actual_size(self):
        self.update_range()
        return self.end - self.begin + 1
    def get_l(self, target_length):
        result = []
        self.update_range()
        for v in self.data[self.begin : self.end]:
            result.append(v[0])
        return result + [0] * (target_length - len(result))

    def update_range(self):
        self.begin = dpg.get_value(self.begin_slider_id)
        self.end = dpg.get_value(self.end_slider_id)



def get_x_axis_data():
    required_length = 0
    for f in files:
        if f.actual_size() > required_length:
            required_length = f.actual_size()
    result = []
    for i in range(required_length):
        result.append(i)
    return result


def callback(sender, app_data):
    files.append(WavData(app_data['file_path_name'], update_plots_data))
    update_plots_data()


def draw_plots(w):

    with dpg.plot(label="Left", parent=w, height=400, width=800):
        # optionally create legend
        dpg.add_plot_legend()

        # REQUIRED: create x and y axes
        dpg.add_plot_axis(dpg.mvXAxis, label="x", tag='left_x_axis')
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="y", tag='left_y_axis')
        # series belong to a y axis
    update_plots_data()


    # with dpg.plot(label="Right", parent=w, height=400, width=800):
    #     # optionally create legend
    #     dpg.add_plot_legend()
    #
    #     # REQUIRED: create x and y axes
    #     dpg.add_plot_axis(dpg.mvXAxis, label="x")
    #     y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="y")

        # for i, f in enumerate(files):
        #     dpg.add_line_series(datax, f.r, label= f'{i}', parent=y_axis)

def update_plots_data():
    datax = get_x_axis_data()
    for i, f in enumerate(files):
        tag = f'left_{i}_line'
        datay = f.get_l(len(datax))
        if not dpg.does_item_exist(tag):
            dpg.add_line_series(datax, datay, label=f'{i}', tag=tag, parent='left_y_axis')
        else:
            dpg.set_value(tag, [datax, datay])
    # dpg.fit_axis_data('left_x_axis')
    # dpg.fit_axis_data('left_y_axis')


with dpg.window(label="WavDiffViewer", width=1920, height=1080) as w:
    dpg.set_primary_window(w, True)

    with dpg.file_dialog(show=False, directory_selector=False, callback=callback, tag="file_dialog_id", width=700, height=400, default_path='./data/', default_filename='initial.waw'):
        dpg.add_file_extension('.wav')
        dpg.add_file_extension(".*")

    dpg.add_group(tag='draw_items')

    dpg.add_button(label='Add file', callback=lambda: dpg.show_item("file_dialog_id"))
    # dpg.add_button(label="Draw", callback=lambda: draw_plots(w))
    draw_plots(w)


dpg.create_viewport(title='WavDiffViewer', width=1920, height=1080)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
