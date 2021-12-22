import tkinter as tk
import PIL
from PIL import ImageTk, Image
from DrawOnCanvas import DrawOnCanvas
from AOIPopup import AOIPopup
from FixationPopup import FixationPopup
from FixationMonitor import FixationMonitor
from BackgroundImageBuilder import BackgroundImageBuilder
import math
from CSVLogfileMaker import CSVLogfileMaker

# A singleton that controls the top level window


class MainWindowController:
    class __MainWindowController:
        def __init__(self, root, screen_w, screen_h, df, bg_image_builder, trial_list, sampl_time, fix_pix, fix_deg, pixels_per_deg, fix_dur):
            #  App
            self.root = root
            #  Menu bar
            self.menubar = None
            self.filemenu = None
            # fixation datafile
            self.df = df
            self.trial_list = trial_list
            # Screen and fixation vars
            self.sampl_time = sampl_time
            self.fix_pix = fix_pix
            self.fix_deg = fix_deg
            self.pixels_per_deg = pixels_per_deg
            self.fix_dur = fix_dur
            #  Top window
            self.pw = None          # includes pw2 and the aoi pane
            #  Sub pane Windows
            self.pw2 = None
            #  Canvas
            self.canvas1 = None     # img and drawing canvas
            self.canvas2 = None     # aoi panel
            self.canvas3 = None     # fixation panel
            # Other Vars
            self.is_aoi_pane_shown = False
            self.is_fixation_pane_shown = False
            self.bg_image = None
            #  AOI Pane
            self.aois = AOIPopup(pixels_per_deg)
            # Fixation Pane
            self.fixation_panel = FixationPopup(len(self.df.index), self.__update_fixation, self.fix_dur, self.sampl_time)
            #  Fixation Monitor
            self.fix_monitor: FixationMonitor = FixationMonitor(self.fix_dur, self.sampl_time, self.fix_pix)
            self.fix_buffer = []
            #  Canvas Drawer
            self.aoi_drawer = DrawOnCanvas()
            self.aoi_drawer.set_screen_dim(screen_w, screen_h)
            # Background Image
            self.bg_image_builder: BackgroundImageBuilder = bg_image_builder
            #  Log file
            self.logfile = CSVLogfileMaker()

            self.__set_up_window()

        #  Sets the fixation monitor's buffer if there are enough samples
        def __set_fixation_monitor_buffer(self, row_num):
            num_samps = self.fix_monitor.num_samples
            row_num = int(row_num)
            is_fixation = False
            if (row_num >= num_samps):
                buffer = []
                for i in range(row_num-num_samps+1, row_num+1):
                    row = self.df.iloc[[i]]
                    sample = [self.__get_x(row), self.__get_y(row)]
                    buffer.append(sample)

                is_fixation = self.fix_monitor.set_buffer(buffer, True)

            else:
                print("Error:  Not enough samples in the yet")

            return is_fixation

        def __get_x(self, row):
            return -1 if math.isnan(row['GazePointX']) else int(row['GazePointX'])

        def __get_y(self, row):
            return -1 if math.isnan(row['GazePointY']) else int(row['GazePointY'])

        def __save_log_file(self):
            # get aois
            aois = self.aoi_drawer.get_aoi_dict()
            header = ['Trial', 'First Fixation', 'Num Fixations']
            names = []
            fix_count = []
            for name in aois:
                header.append(name + '_FixCount')
                names.append(name)
                fix_count.append(0)

            self.logfile.set_column_names([header])

            exp_data = []
            trial_data = []
            trial_no = 0
            first_fixation: str = None
            num_fixations = 0
            is_fix = True   # Trials begin assuming a fixation on the cross.  Start trials as False if you want to include the cross in first fixation

            for i in range(0, len(self.df.index)-1):
                row = self.df.iloc[[i]]
                is_new_trial = False
                #  New trial init (ignores trial 0)
                if (trial_no < self.trial_list[int(i)]):
                    is_new_trial = True
                    is_fix = True   # set False if you want to include fix cross in first fixation data
                if (self.trial_list[int(i)] < trial_no):  # a trial has ended and we are at the next ITI
                    trial_data = [str(trial_no), first_fixation, str(num_fixations)]
                    j = 0
                    for count in fix_count:
                        trial_data.append(str(count))
                        fix_count[j] = 0
                        j = j + 1
                    num_fixations = 0
                    first_fixation = None
                    self.logfile.add_row([trial_data])
                trial_no = self.trial_list[int(i)]
                x = self.__get_x(row)
                y = self.__get_y(row)

                if (trial_no != 0):
                    if x >= 0 & y >= 0:
                        aoi_names = self.aoi_drawer.is_fixation_in_aoi(x, y)

                        # unique fixation (prev samp wasn't fix and this one is)
                        if ((not is_fix) & self.__set_fixation_monitor_buffer(i)):
                            num_fixations = num_fixations + 1
                            for name in aoi_names:
                                name_index = names.index(name)
                                fix_count[name_index] = fix_count[name_index] + 1

                        is_fix = self.__set_fixation_monitor_buffer(i)

                        if (first_fixation is None and is_fix):
                            first_fixation = str(aoi_names)

                        if (is_new_trial):
                            exp_data.append(trial_data)
                            trial_data = []
                            first_fixation = None
                            is_fix = True

            trial_data = [str(trial_no), first_fixation, num_fixations]
            for count in fix_count:
                trial_data.append(str(count))
            self.logfile.add_row([trial_data])
            self.logfile.save_file()

        #def __check_fixation(self, names):


        def __update_fixation(self, v):
            is_fix = self.__set_fixation_monitor_buffer(v)
            row = self.df.iloc[[v]]
            label_str = ''
            trial_no = self.trial_list[int(v)]
            x = self.__get_x(row)
            y = self.__get_y(row)

            if (trial_no-1 != self.bg_image_builder.get_bg_trial_no()):
                if trial_no != 0:
                    fname = self.bg_image_builder.save_background_image(trial_no-1)
                    self.set_bg_image(fname)

            if x >= 0 & y >= 0:
                aoi_names = self.aoi_drawer.is_fixation_in_aoi(x, y)
                label_str = 'Trial ' + str(trial_no) + '\n' + str(aoi_names)
                self.fixation_panel.set_slider_label(label_str)
                if aoi_names:
                    self.aoi_drawer.draw_circle(x, y, 5, "red")
                else:
                    if is_fix:
                        self.aoi_drawer.draw_circle(x, y, 5, "blue")
                    else:
                        self.aoi_drawer.draw_circle(x, y, 5)

        # returns the canvas for given number
        def get_canvas(self, num):
            can = None
            if num == 1:
                can = self.canvas1
            elif num == 2:
                can = self.canvas2
            else:
                can = self.canvas3
            return can

        def __set_up_window(self):
            self.root.state('zoomed')        # Start the app in full screen
            self.aois.set_draw_callback(self.bind_aoi_mouse)
            self.__set_up_panes()

        def __set_up_panes(self):
            self.pw = tk.PanedWindow(sashwidth=2, orient=tk.HORIZONTAL)
            self.pw.pack(fill=tk.BOTH, expand=1)

            self.pw2 = tk.PanedWindow(self.pw, orient=tk.VERTICAL)
            self.canvas1 = ResizingImageCanvas(self.pw2, bd=0)
            self.set_bg_image(self.bg_image_builder.save_background_image(0))

            self.pw2.add(self.canvas1, stretch='always')
            self.canvas3 = tk.Canvas(self.pw2, bg='green', bd=0, height=200)
            #
            self.pw.add(self.pw2, stretch='always')
            self.canvas2 = tk.Canvas(self.pw, bg='red', bd=0, width=300)
            self.aoi_drawer.set_canvas(self.canvas1)
            self.aoi_drawer.set_pad()
            self.aois.set_paned_window(self.pw, self.root)

            self.fixation_panel.set_paned_window(self.pw2)

            self.__set_up_menu()

        def __set_up_menu(self):
            self.menubar = tk.Menu(self.root)
            self.filemenu = tk.Menu(self.menubar, tearoff=0)
            self.filemenu.add_command(label="Run Trials")
            self.filemenu.add_command(label="Draw AOI")
            self.filemenu.add_command(label="Save Logs", command=self.__save_log_file)
            self.menubar.add_cascade(label="File", menu=self.filemenu)
            self.viewmenu = tk.Menu(self.menubar, tearoff=0)
            self.viewmenu.add_command(label="Show Fixations", command=self.toggle_fixation_pane, accelerator="Ctrl+5")
            self.viewmenu.add_command(label="Show Aois", command=self.toggle_aoi_pane, accelerator="Ctrl+4")
            self.menubar.add_cascade(label="View", menu=self.viewmenu)

            self.root.config(menu=self.menubar)

            self.root.bind('<Control-Key-4>', self.__toggle_aoi_pane)
            self.root.bind('<Control-Key-5>', self.__toggle_fixation_pane)

        # Uses the filename string to set the canvas background image
        def set_bg_image(self, filename):
            self.canvas1.set_bg_img(filename)

        def __toggle_aoi_pane(self, event):
            self.toggle_aoi_pane()

        def toggle_aoi_pane(self):
            if self.is_aoi_pane_shown:
                self.hide_aoi_pane()
            else:
                self.show_aoi_pane()

        def __toggle_fixation_pane(self, event):
            self.toggle_fixation_pane()

        def toggle_fixation_pane(self):
            if self.is_fixation_pane_shown:
                self.hide_fixation_pane()
            else:
                self.show_fixation_pane()

        def show_aoi_pane(self):
            self.aois.show_panel()
            self.is_aoi_pane_shown = True

        def hide_aoi_pane(self):
            self.aois.hide_panel()
            self.is_aoi_pane_shown = False

        def show_fixation_pane(self):
            self.fixation_panel.show_fixation_pane()
            self.is_fixation_pane_shown = True

        def hide_fixation_pane(self):
            self.fixation_panel.hide_fixation_pane()
            self.is_fixation_pane_shown = False

        # Mouse Bind Functions
        def unbind_aoi_mouse(self):
            self.root.unbind('<B1-Motion>')
            self.root.unbind('<ButtonRelease-1>')
            self.root.unbind('<ButtonPress-1>')

        def draw_rect(self, event):
            self.aoi_drawer.draw_rectangle(event.x-2, event.y-2)

        def set_start_pos(self, event):
            self.aoi_drawer.set_start_coord(event.x-2, event.y-2)

        def set_end_pos(self, event):
            self.aoi_drawer.set_end_coord(event.x-2, event.y-2)
            self.aois.reset_frame()
            self.unbind_aoi_mouse()

        def bind_aoi_mouse(self):
            self.root.bind('<B1-Motion>', self.draw_rect)
            self.root.bind('<ButtonRelease-1>', self.set_end_pos)
            self.root.bind('<ButtonPress-1>', self.set_start_pos)

    instance = None

    def __init__(self, root, screen_w, screen_h, df, bg_image_builder, trial_list, sampl_time, fix_pix, fix_deg, pixels_per_deg, fix_dur):
        if not MainWindowController.instance:
            MainWindowController.instance = MainWindowController.__MainWindowController(root, screen_w, screen_h, df, bg_image_builder, trial_list, sampl_time, fix_pix, fix_deg, pixels_per_deg, fix_dur)

    def set_bg_image(self, filename):
        MainWindowController.instance.set_bg_image(filename)

    def get_canvas(self, num):
        self.instance.get_canvas(num)

    def show_aoi_pane(self):
        self.instance.show_aoi_pane()

    def get_paned_window(self):
        return self.instance.pw


#  Canvas that resizes the widgets with the tag "all"
class ResizingCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self, event):
        # determine the ratio of old width/height to new width/height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)


#  Resizing canvas that also has a resizing background image
class ResizingImageCanvas(ResizingCanvas):
    def __init__(self, parent, **kwargs):
        ResizingCanvas.__init__(self, parent, **kwargs)
        self.bg_img_tag = "bg_img"
        self.image = None
        self.tmp_img = None
        self.photo = None
        self.aois = DrawOnCanvas()
        self.bind("<Configure>", self.on_resize_image)

    def set_bg_img(self, fname):
        self.image = Image.open(fname)
        self.__refresh_canvas()

    def on_resize_image(self, event):
        self.on_resize(event)
        self.__refresh_canvas()

    # must be called to add new image
    def __refresh_canvas(self):
        self.tmp_img = self.image.resize((self.width, self.height), PIL.Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(self.tmp_img)
        self.create_image(0, 0, image=self.photo, anchor=tk.NW, tags=self.bg_img_tag)
        self.aois.redraw_dict()
