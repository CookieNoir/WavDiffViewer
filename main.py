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
        self.begin_slider_id = dpg.add_input_int(label='begin', parent=g, min_value=0, max_value=len(self.data), default_value=0, width=200, step_fast=100, min_clamped=True, max_clamped=True, callback=lambda : update_callback())
        self.width_slider_id = dpg.add_input_int(label='width', parent=g, min_value=1, max_value=len(self.data), default_value=min(len(self.data), 1000), width=200, step_fast=100,min_clamped=True, max_clamped=True, callback=lambda : update_callback())

        self.y_offset_slider_id = dpg.add_input_int(label='y_offset', parent=g, default_value=0, width=200, step_fast=100, callback=lambda : update_callback())

    def actual_size(self):
        self.update_controls()
        return self.width
    def get_channels(self, target_length):
        left = []
        right = []
        self.update_controls()
        for v in self.data[self.begin : self.begin + self.width]:
            left.append(int(v[0]) + self.y_offset)
            right.append(int(v[1]) + self.y_offset)
        l_result = left + [0] * (target_length - self.width)
        r_result = right + [0] * (target_length - self.width)
        return (l_result, r_result)


    def update_controls(self):
        self.begin = dpg.get_value(self.begin_slider_id)
        self.width = dpg.get_value(self.width_slider_id)

        self.y_offset = dpg.get_value(self.y_offset_slider_id)



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
        dpg.add_plot_legend()
        dpg.add_plot_axis(dpg.mvXAxis, label="x", tag='left_x_axis')
        dpg.add_plot_axis(dpg.mvYAxis, label="y", tag='left_y_axis')



    with dpg.plot(label="Right", parent=w, height=400, width=800):
        dpg.add_plot_legend()
        dpg.add_plot_axis(dpg.mvXAxis, label="x", tag='right_x_axis')
        dpg.add_plot_axis(dpg.mvYAxis, label="y", tag='right_y_axis')

    update_plots_data()


def update_plots_data():
    datax = get_x_axis_data()
    for i, f in enumerate(files):
        left_tag = f'left_{i}_line'
        right_tag = f'right_{i}_line'
        left, right = f.get_channels(len(datax))
        if not dpg.does_item_exist(left_tag):
            dpg.add_line_series(datax, left, label=f'{i}', tag=left_tag, parent='left_y_axis')
        else:
            dpg.set_value(left_tag, [datax, left])

        if not dpg.does_item_exist(right_tag):
            dpg.add_line_series(datax, right, label=f'{i}', tag=right_tag, parent='right_y_axis')
        else:
            dpg.set_value(right_tag, [datax, right])
    # dpg.fit_axis_data('left_x_axis')
    # dpg.fit_axis_data('left_y_axis')


with dpg.window(label="WavDiffViewer", width=1920, height=1080) as w:
    dpg.set_primary_window(w, True)

    with dpg.file_dialog(show=False, directory_selector=False, callback=callback, tag="file_dialog_id", width=700, height=400, default_path='./data/', default_filename='initial.waw'):
        dpg.add_file_extension('.wav')
        dpg.add_file_extension(".*")

    dpg.add_group(tag='draw_items')

    dpg.add_button(label='Add file', callback=lambda: dpg.show_item("file_dialog_id"))
    draw_plots(w)


dpg.create_viewport(title='WavDiffViewer', width=1920, height=1080)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
