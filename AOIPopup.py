from tkinter import *
from tkinter import ttk
import tkinter as tk
from DrawOnCanvas import DrawOnCanvas
from functools import partial

#  A singleton for the Area of Interest popup
class AOIPopup:
    class __AOIPopup:
        def __init__(self, pixels_per_deg):
            #  Tkinter
            self.root = None
            # GUI
            self.pw = None
            self.aoi_panel_is_shown = False
            self.aoi_panel = None
            self.aois = DrawOnCanvas()
            self.aoi_name = None
            self.panel_width = 205
            self.fixation_size_str = None
            self.is_fixation_shown = False
            # Main fonts
            self.LARGE_FONT = ("Verdana", 12)
            self.NORM_FONT = ("Helvetica", 10)
            self.SMALL_FONT = ("Helvetica", 8)
            # External functions
            self.draw_func = None
            # Grid Widgets
            self.aoi_name_input = None
            self.fixation_var_input = None
            self.fixation_scale: tk.Scale
            # Screen Vars
            self.pixels_per_deg = pixels_per_deg

        def set_aois(self, aois):
            self.aois = aois

        def set_paned_window(self, pw, root):
            self.pw = pw
            self.root = root

        def toggle_window(self):
            self.__toggle_window()

        def set_draw_callback(self, func):
            self.draw_func = func

        def show_panel(self):
            if not self.aoi_panel_is_shown:
                self.__toggle_window()

        def hide_panel(self):
            if self.aoi_panel_is_shown:
                self.__toggle_window()

        def __toggle_window(self):
            if (self.aoi_panel_is_shown):
                self.pw.remove(self.aoi_panel)
                # self.aois.redraw_dict(self.panel_width)
            else:
                self.aoi_panel = tk.Frame(self.pw, bd=2)
                self.pw.add(self.aoi_panel, minsize=200, stretch='never')
                self.pw.paneconfigure(self.aoi_panel, minsize=self.panel_width)
                self.__build_grid()

            self.aoi_panel_is_shown = not self.aoi_panel_is_shown

        def __begin_draw(self, event):
            self.__draw_func_raw()

        def __draw_func_raw(self):
            self.draw_func()
            self.aoi_name = self.aoi_name_input.get()
            self.aoi_name_input.config(state='disabled')
            self.aois.set_name(self.aoi_name)
            self.root.unbind('<Return>')

        def __delete_aoi(self, name):
            self.aois.remove_dict_entry(name)
            self.reset_frame()

        def __build_grid(self):
            self.__set_AOI_row(1, self.aoi_panel, "Name", "Close", self.__toggle_window, 0)
            row_n = 1
            aois = self.aois.get_aoi_dict()
            for name in aois:
                new_func = partial(self.__delete_aoi, name)
                self.__set_AOI_row(2, self.aoi_panel, name, "Delete", new_func, row_n)
                row_n = row_n + 1

            self.__set_AOI_row(3, self.aoi_panel, "Name", "Draw AOI", self.__draw_func_raw, row_n)

            self.__set_return_bind(1)
            self.aoi_name_input.focus_set()

            row_n = row_n + 1
            ttk.Separator(self.aoi_panel, orient=tk.HORIZONTAL).grid(row=row_n, columnspan=2, pady=10, sticky="EW")
            row_n = row_n + 1
            fixation_frame = ToggledFrame(self.aoi_panel, text='Fixation', relief="raised", borderwidth=1)
            fixation_frame.grid(row=row_n, columnspan=2, sticky="EW")
            f1 = tk.Frame(fixation_frame.sub_frame, borderwidth=1)
            ttk.Label(f1, text='size (deg)').pack(side="left", fill="x")
            self.fixation_size_str = tk.StringVar(f1, value="1.0")
            self.fixation_var_input = ttk.Entry(f1, textvariable=self.fixation_size_str, justify=tk.RIGHT, width=16)
            self.fixation_var_input.pack(side="left")
            self.fixation_var_input.bind("<1>", self.__set_click_focus_fixation)
            f1.pack()
            f2 = tk.Frame(fixation_frame.sub_frame, borderwidth=1)
            self.fixation_scale = tk.Scale(f2, from_=1.0, to=3.0, resolution=0.1, showvalue=0, orient=tk.HORIZONTAL, command=self.__set_fixation_string_var, length=150)
            self.fixation_scale.pack(anchor=W)
            self.fixation_scale.set(1.5)
            self.is_fixation_shown = True
            f2.pack()

        #  The folllowing defs are for setting the <RETURN> button click methods
        # when one of the Entry boxes is clicked.
        def __set_click_focus_aoi(self, event):
            self.__set_return_bind(1)

        def __set_click_focus_fixation(self, event):
            self.__set_return_bind(2)

        # This function sets the keybind for return
        #  i = 1:  Bind to __begin_draw
        #  i = 2:  Bind to __set_fixation_scale
        def __set_return_bind(self, i):
            if (i == 1):
                self.root.bind('<Return>', self.__begin_draw)
            else:
                self.root.bind('<Return>', self.__set_fixation_scale)

        # Returns the AOI Row for the AOIPopup window
        # type - 1 = Header, 2 = Existing AOI, 3 = New AOI
        # parent - master
        # label - the text next to the button or entry
        # but_label - the label on the Button
        # func - function to be called when btton is pressed
        # row - the grid row
        def __set_AOI_row(self, type, parent, label, but_label, func, row):
            if type == 1:
                tk.Label(parent, text=label).grid(row=row, column=0)
                tk.Button(parent, text=but_label, command=func).grid(row = row, column = 1, sticky="NE")
            elif type == 2:
                tk.Label(parent, text=label).grid(row=row, column=0)
                tk.Button(parent, text=but_label, command=func).grid(row = row, column = 1, sticky="NW")
            elif type == 3:
                self.aoi_name_input = tk.Entry(parent)
                self.aoi_name_input.grid(row=row, column=0, padx=4)
                self.aoi_name_input.bind("<1>", self.__set_click_focus_aoi)
                tk.Button(parent, text=but_label, command=func).grid(row = row, column = 1, sticky="E")
            else:
                print("Error: AOIPopup: __set_AOI_row: ")

        def __set_fixation_string_var(self, v):
            self.fixation_size_str.set(str(v))
            if self.is_fixation_shown:
                self.aois.draw_fixation_circle(int(self.pixels_per_deg*float(v)))

        def __set_fixation_scale(self, v):
            fix = float(self.fixation_size_str.get())
            self.fixation_scale.set(fix)
            if self.is_fixation_shown:
                self.aois.draw_fixation_circle(int(self.pixels_per_deg*fix))

        def reset_frame(self):
            self.__toggle_window()
            self.__toggle_window()

    instance = None

    def __init__(self, pixels_per_deg):
        if not self.instance:
            self.instance = self.__AOIPopup(pixels_per_deg)

    def set_aois(self, aois):
        self.instance.set_aois(aois)

    def set_paned_window(self, pw, root):
        self.instance.set_paned_window(pw, root)

    #  Display or hide the side AOE side panel
    def toggle_window(self):
        self.instance.toggle_window()

    #  Set the callback to begin drawing the AOI on the main Windows
    def set_draw_callback(self, func):
        self.instance.set_draw_callback(func)

    # Refreshes the aoi grid
    def reset_frame(self):
        self.instance.reset_frame()

    #  Shows the panel if it is not open and does nothing if it is already open
    def show_panel(self):
        self.instance.show_panel()

    #  Hides panel if it is open and does nothing if it is already hidden
    def hide_panel(self):
        self.instance.hide_panel()

class ToggledFrame(tk.Frame):

    def __init__(self, parent, text="", *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)

        self.show = tk.IntVar()
        self.show.set(0)

        self.title_frame = ttk.Frame(self)
        self.title_frame.pack(fill="x")

        ttk.Label(self.title_frame, text=text).pack(side="left", fill="x")

        self.toggle_button = ttk.Checkbutton(self.title_frame, width=2, text='+', command=self.toggle,
                                            variable=self.show, style='Toolbutton')
        self.toggle_button.pack(side="right")

        self.sub_frame = tk.Frame(self, relief="sunken", borderwidth=1)

    def toggle(self):
        if bool(self.show.get()):
            self.sub_frame.pack(fill="x", expand=0)
            self.toggle_button.configure(text='-')
        else:
            self.sub_frame.forget()
            self.toggle_button.configure(text='+')
