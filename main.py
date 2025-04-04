import dearpygui.dearpygui as dpg
from scipy.io import wavfile
from math import sin

dpg.create_context()

files = []

global_offset_id = 0
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
        self.width_slider_id = dpg.add_input_int(label='width', parent=g, min_value=1, max_value=len(self.data), default_value=min(len(self.data), 1000), width=200, step_fast=100, min_clamped=True, max_clamped=True, callback=lambda : update_callback())

        self.y_offset_slider_id = dpg.add_input_int(label='y_offset', parent=g, default_value=0, width=100, step_fast=100, callback=lambda : update_callback())
        self.y_scale_slider_id = dpg.add_input_float(label='y_scale', parent=g, default_value=1, width=100, min_value=-10, max_value=10, step=0.001, step_fast=0.05, min_clamped=True, max_clamped=True, callback=lambda : update_callback())

    def actual_size(self):
        self.update_controls()
        return self.width
    def get_channels(self, offset, target_length):
        left = []
        right = []
        self.update_controls()
        begin = self.begin + offset
        clamped_width = min(len(self.data) - begin, self.width)
        for v in self.data[begin: begin + clamped_width]:
            left.append(int(v[0]) * self.y_scale + self.y_offset)
            right.append(int(v[1]) * self.y_scale + self.y_offset)
        l_result = left + [0] * (target_length - clamped_width)
        r_result = right + [0] * (target_length - clamped_width)
        return (l_result, r_result)


    def update_controls(self):
        self.begin = dpg.get_value(self.begin_slider_id)
        self.width = dpg.get_value(self.width_slider_id)

        self.y_offset = dpg.get_value(self.y_offset_slider_id)
        self.y_scale = dpg.get_value(self.y_scale_slider_id)



def get_x_axis_data():
    required_length = 0
    for f in files:
        if f.actual_size() > required_length:
            required_length = f.actual_size()
    result = []
    for i in range(required_length):
        result.append(i)
    return result


def file_dialog_callback(sender, app_data):
    selections = app_data["selections"]
    file_paths = list(selections.values())  # Get all selected file paths 
    
    for file_path in file_paths:
        files.append(WavData(file_path, update_plots_data))
        
    update_plots_data()


def draw_plots(w):

    with dpg.plot(label="Left", parent=w, height=600, width=1920):
        dpg.add_plot_legend()
        dpg.add_plot_axis(dpg.mvXAxis, label="x", tag='left_x_axis')
        dpg.add_plot_axis(dpg.mvYAxis, label="y", tag='left_y_axis')



    with dpg.plot(label="Right", parent=w, height=600, width=1920):
        dpg.add_plot_legend()
        dpg.add_plot_axis(dpg.mvXAxis, label="x", tag='right_x_axis')
        dpg.add_plot_axis(dpg.mvYAxis, label="y", tag='right_y_axis')

    update_plots_data()


def update_plots_data():
    datax = get_x_axis_data()
    for i, f in enumerate(files):
        left_tag = f'left_{i}_line'
        right_tag = f'right_{i}_line'
        global_offset = dpg.get_value(global_offset_id)
        left, right = f.get_channels(global_offset, len(datax))
        if not dpg.does_item_exist(left_tag):
            dpg.add_line_series(datax, left, label=f'{i}', tag=left_tag, parent='left_y_axis')
        else:
            dpg.set_value(left_tag, [datax, left])

        if not dpg.does_item_exist(right_tag):
            dpg.add_line_series(datax, right, label=f'{i}', tag=right_tag, parent='right_y_axis')
        else:
            dpg.set_value(right_tag, [datax, right])

def fit_all_axis():
    dpg.fit_axis_data('left_x_axis')
    dpg.fit_axis_data('left_y_axis')
    dpg.fit_axis_data('right_x_axis')
    dpg.fit_axis_data('right_y_axis')

with dpg.window(label="WavDiffViewer", width=1920, height=1080) as w:
    dpg.set_primary_window(w, True)

    with dpg.file_dialog(show=False, directory_selector=False, callback=file_dialog_callback, tag="file_dialog_id", width=700, height=400, default_path='./data/', default_filename='initial.waw'):
        dpg.add_file_extension('.wav')
        dpg.add_file_extension(".*")

    dpg.add_group(tag='draw_items')
    global_offset_id = dpg.add_input_int(label='global_offset', min_value=0, default_value=0, width=200, step_fast=100, min_clamped=True, callback=update_plots_data)
    dpg.add_button(label='Add file', callback=lambda: dpg.show_item("file_dialog_id"))
    dpg.add_button(label='FitAll', callback=fit_all_axis)
    draw_plots(w)


dpg.create_viewport(title='WavDiffViewer', width=1920, height=1080)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
