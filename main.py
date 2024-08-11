import dearpygui.dearpygui as dpg
from scipy.io import wavfile
from math import sin

dpg.create_context()



files = []

class WavData:
    def __init__(self, path):
        self._path = path
        self.samplerate, self.data = wavfile.read(path)
        print(f'samplerate: {self.samplerate} data length: {len(self.data)}')
        self.l = []
        self.r = []
        for i, v in enumerate(self.data):
            self.l.append(v[0])
            self.r.append(v[1])

    def get_l(self, target_length):
        result = []
        for v in self.data:
            result.append(v[0])
        return result + [0] * (target_length - len(result))

def get_x_axis_data():
    required_length = 0
    for f in files:
        if len(f.data) > required_length:
            required_length = len(f.data)
    result = []
    for i in range(required_length):
        result.append(i)
    return result

def callback(sender, app_data):
    files.append(WavData(app_data['file_path_name']))

def draw_plots(w):
    datax = get_x_axis_data()
    with dpg.plot(label="Left", parent=w, height=400, width=800):
        # optionally create legend
        dpg.add_plot_legend()

        # REQUIRED: create x and y axes
        dpg.add_plot_axis(dpg.mvXAxis, label="x")
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="y")
        # series belong to a y axis
        for i, f in enumerate(files):
            dpg.add_line_series(datax, f.get_l(len(datax)), label= f'{i}', parent=y_axis)


    with dpg.plot(label="Right", parent=w, height=400, width=800):
        # optionally create legend
        dpg.add_plot_legend()

        # REQUIRED: create x and y axes
        dpg.add_plot_axis(dpg.mvXAxis, label="x")
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="y")

        # for i, f in enumerate(files):
        #     dpg.add_line_series(datax, f.r, label= f'{i}', parent=y_axis)


with dpg.window(label="WavDiffViewer", width=1920, height=1080) as w:


    with dpg.file_dialog(show=False, directory_selector=False, callback=callback, tag="file_dialog_id", width=700, height=400):
        dpg.add_file_extension('.wav')
        dpg.add_file_extension(".*")

    dpg.add_button(label='Add file', callback = lambda: dpg.show_item("file_dialog_id"))
    dpg.add_button(label="Draw",callback = lambda: draw_plots(w))




dpg.create_viewport(title='WavDiffViewer', width=1920, height=1080)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()