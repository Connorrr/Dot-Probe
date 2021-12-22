import tkinter as tk
from FixationMonitor import FixationMonitor

#  A singleton for the fixation popup bar at the bottom of screen


class FixationPopup:
    class __FixationPopup:
        def __init__(self, dflen, cmd, fix_dur, samp_time):
            self.pw = None
            self.cmd = cmd              # Updates the drawn point
            self.slider_len = dflen     # length of data file -> length of slider
            self.slider = None
            self.slider_label = None
            self.is_fixation_pane_shown = False

        # set up the window
        def set_paned_window(self, pw):
            self.pw = pw
            self.slider = tk.Scale(self.pw, from_=0, to=self.slider_len-1, orient=tk.HORIZONTAL, command=self.cmd)
            self.slider_label = tk.Label(self.pw, text="First Text")

        # Sets the text for the Label
        def set_slider_label(self, text):
            self.slider_label.configure(text=text)

        def toggle_fixation_pane(self):
            if self.is_fixation_pane_shown:
                self.hide_fixation_pane()
            else:
                self.show_fixation_pane()

        def show_fixation_pane(self):
            self.pw.add(self.slider)
            self.is_fixation_pane_shown = True
            self.pw.add(self.slider_label)

        def hide_fixation_pane(self):
            self.pw.remove(self.slider)
            self.pw.remove(self.slider_label)

    instance = None

    def __init__(self, dflen, cmd, fix_dur, samp_time):
        if not self.instance:
            self.instance = self.__FixationPopup(dflen, cmd, fix_dur, samp_time)

    def set_paned_window(self, pw):
        self.instance.set_paned_window(pw)

    def set_slider_label(self, text):
        self.instance.set_slider_label(text)

    def show_fixation_pane(self):
        self.instance.show_fixation_pane()

    def hide_fixation_pane(self):
        self.instance.hide_fixation_pane()
