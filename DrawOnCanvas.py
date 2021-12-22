import tkinter

#  A singleton that takes a tk canvas and draws on lines and rectangles with the given coordinates (potentially mouse coordinates)
class DrawOnCanvas:
    class __DrawOnCanvas:
        def __init__(self):
            #  Canvas Vars
            self.canv = None
            self.x_pad = 0      # Used to account for collapsable frames
            self.y_pad = 0
            self.org_s_width = 0
            self.org_s_height = 0
            self.Sw = 1.0       # Scale factor used to normalize x values
            self.Sh = 1.0       # Scale factor used to normalize y values
            #  Rectangle line variables
            self.start_x = 0
            self.start_y = 0
            self.end_x = 0
            self.end_y = 0
            self.line_id = None
            self.rect_ids = None
            self.t_line_id = None
            self.l_line_id = None
            self.r_line_id = None
            self.b_line_id = None
            self.aoi_ids = None
            #  Circle variables
            self.circle_id = None
            # fixation demo
            self.fixation_demo_circle = None
            #  Aoi variables
            self.name = "AOI"
            self.aoi_dict = {}      # A dictionary that holds the name and line IDs (array) for the aois
            #  App level variables
            self.root = None
            self.left_click_id = None
            self.left_release_id = None
            self.left_hold_id = None

        def set_name(self, name):
            self.name = name

        #  Must call this function before running
        def set_canvas(self, can):
            self.canv = can

        def set_pad(self):
            self.canv.create_oval(-2, -2, 2, 2, fill='red')
            self.x_pad = self.canv.winfo_width()/2
            self.y_pad = self.canv.winfo_height()/2
            print("W " + str(self.x_pad) + " H " + str(self.y_pad))

        def set_screen_dim(self, w, h):
            self.org_s_width = w
            self.org_s_height = h

        def __check_canvas(self):
            if not self.canv:
                print('Error:  set_canvas must be called before any other functions are called')

        def draw_line(self, x, y):
            self.__check_canvas()
            if self.line_id:
                self.canv.delete(self.line_id)
            self.line_id = self.canv.create_line(0, 0, x-self.x_pad, y-self.y_pad, fill="red")

        #  Set starting point for drawing a rectangle on canvas
        def set_start_coord(self, x, y):
            self.__check_canvas()
            self.redraw_dict()
            self.start_x = x
            self.start_y = y

        #  Set ending point for drawing a rectangle on canvas
        def set_end_coord(self, x, y):
            self.__check_canvas()
            self.__set_scale_factors()
            self.end_x = x
            self.end_y = y
            self.rect_ids = [self.t_line_id,
                             self.l_line_id,
                             self.r_line_id,
                             self.b_line_id,
                             self.start_x,
                             self.start_y,
                             self.end_x,
                             self.end_y,
                             self.Sw,
                             self.Sh]
            self.aoi_dict[self.name] = self.rect_ids

        # Takse the fixation data and returns the AOI name in an array if it is inside the rectangle
        def is_fixation_in_aoi(self, x, y):
            topY = 0
            botY = 0
            leftX = 0
            rightX = 0
            retArr = []
            x = int(x)      # these values are already in a normalized format since they come straight from the eyetracking data
            y = int(y)

            for name in self.aoi_dict:
                rectID = self.aoi_dict[name]
                Sw = rectID[8]      # Scale factors used to normalize the stored values
                Sh = rectID[9]

                if (rectID[4] <= rectID[6]):      # if start x is less than end x
                    leftX = rectID[4] * Sw
                    rightX = rectID[6] * Sw
                else:
                    leftX = rectID[6] * Sw
                    rightX = rectID[4] * Sw
                if (rectID[5] <= rectID[7]):        # if start y is less than end y
                    botY = rectID[5] * Sh
                    topY = rectID[7] * Sh
                else:
                    botY = rectID[7] * Sh
                    topY = rectID[5] * Sh

                if (x <= rightX):  # Is the fixation in the aoi
                    if (x >= leftX):
                        if (y <= topY):
                            if (y >= botY):
                                retArr.append(name)
            return retArr

        #  drag and drop the rectangle
        def draw_rectangle(self, x, y):
            self.__check_canvas()
            x = x
            y = y

            if self.t_line_id:
                self.canv.delete(self.t_line_id)
            if self.l_line_id:
                self.canv.delete(self.l_line_id)
            if self.r_line_id:
                self.canv.delete(self.r_line_id)
            if self.b_line_id:
                self.canv.delete(self.b_line_id)

            self.t_line_id = self.canv.create_line(self.start_x-(self.x_pad), self.start_y-(self.y_pad), x-(self.x_pad), self.start_y-(self.y_pad), fill="red")
            self.l_line_id = self.canv.create_line(self.start_x-(self.x_pad), self.start_y-(self.y_pad), self.start_x-(self.x_pad), y-(self.y_pad), fill="red")
            self.r_line_id = self.canv.create_line(x-(self.x_pad), self.start_y-(self.y_pad), x-(self.x_pad), y-(self.y_pad), fill="red")
            self.b_line_id = self.canv.create_line(x-(self.x_pad),  y-(self.y_pad), self.start_x-(self.x_pad), y-(self.y_pad), fill="red")

        #  Daw a circle at point with radius
        def draw_circle(self, x, y, r, colour='white'):
            if self.circle_id:
                self.canv.delete(self.circle_id)

            x = int(x/self.Sw)
            y = int(y/self.Sh)
            x0 = x - r
            y0 = y - r
            x1 = x + r
            y1 = y + r

            self.circle_id = self.canv.create_oval(x0, y0, x1, y1, fill=colour)

        # Draws a circle in the middle of the screen to represents the fixation size
        def draw_fixation_circle(self, r, x=-1, y=-1, color='red'):
            new_fix = False             # is this fixation new
            if self.fixation_demo_circle:
                self.canv.delete(self.fixation_demo_circle)
            else:
                new_fix = True

            if (x == -1 and y == -1):
                x = int((self.org_s_width/2)/self.Sw)
                y = int((self.org_s_height/2)/self.Sh)
            else:
                x = int(x/self.Sw)
                y = int(y/self.Sh)

            Srw = r/self.Sw
            Srh = r/self.Sh
            x0 = x - Srw
            y0 = y - Srh
            x1 = x + Srw
            y1 = y + Srh

            self.fixation_demo_circle = self.canv.create_oval(x0, y0, x1, y1, outline=color, width=2)
            return new_fix

        # removes the fixation circle if it exists
        def remove_fixation_circle(self):
            if self.fixation_demo_circle:
                self.canv.delete(self.fixation_demo_circle)

        def __set_scale_factors(self):
            if self.canv:
                self.Sw = self.org_s_width/self.canv.winfo_width()
                self.Sh = self.org_s_height/self.canv.winfo_height()

        #  Takes the dictionary
        def redraw_dict(self, xadj=0):
            self.__set_scale_factors()

            if self.fixation_demo_circle:
                self.canv.delete(self.fixation_demo_circle)

            for name in self.aoi_dict:
                # get original ids and coords
                rect_ids = self.aoi_dict[name]
                Sw = rect_ids[8]
                Sh = rect_ids[9]
                norm_start_x = rect_ids[4] * Sw
                norm_start_y = rect_ids[5] * Sh
                norm_end_x = rect_ids[6] * Sw
                norm_end_y = rect_ids[7] * Sh
                #  delete the old lines
                self.canv.delete(rect_ids[0])
                self.canv.delete(rect_ids[1])
                self.canv.delete(rect_ids[2])
                self.canv.delete(rect_ids[3])
                # get new coordinates
                start_x = norm_start_x/self.Sw
                start_y = norm_start_y/self.Sh
                end_x = norm_end_x/self.Sw
                end_y = norm_end_y/self.Sh
                #  push them to canvas
                rect_ids[0] = self.canv.create_line(start_x, start_y, end_x, start_y, fill="red")
                rect_ids[1] = self.canv.create_line(start_x, start_y, start_x, end_y, fill="red")
                rect_ids[2] = self.canv.create_line(end_x, start_y, end_x, end_y, fill="red")
                rect_ids[3] = self.canv.create_line(end_x,  end_y, start_x, end_y, fill="red")

                # push to dictionary
                self.aoi_dict[name] = rect_ids

        def get_aoi_dict(self):
            return self.aoi_dict

        def remove_dict_entry(self, name):
            ids = self.aoi_dict[name]
            print(ids)
            if ids[0]:
                self.canv.delete(ids[0])
            if ids[1]:
                self.canv.delete(ids[1])
            if ids[2]:
                self.canv.delete(ids[2])
            if ids[3]:
                self.canv.delete(ids[3])
            else:
                print("couldn't find these lines")

            del self.aoi_dict[name]
            self.redraw_dict()

    instance = None
    def __init__(self):
        if not DrawOnCanvas.instance:
            DrawOnCanvas.instance = DrawOnCanvas.__DrawOnCanvas()

    def set_name(self, name):
        self.instance.set_name(name)

    def set_canvas(self, can):
        DrawOnCanvas.instance.set_canvas(can)

    #  To be called after the screen has been initialized.  This gives padding information if the screen size changes
    def set_pad(self):
        DrawOnCanvas.instance.set_pad()

    # Sets the original screen dimensions during eyetracking.  These values are used for scaling
    def set_screen_dim(self, w, h):
        DrawOnCanvas.instance.set_screen_dim(w, h)

    #  Takse the fixation data and returns the AOI name in an array if it is inside the rectangle
    def is_fixation_in_aoi(self, x, y):
        return DrawOnCanvas.instance.is_fixation_in_aoi(x, y)

    def draw_line(self, x, y):
        DrawOnCanvas.instance.draw_line(x, y)

    def set_start_coord(self, x, y):
        DrawOnCanvas.instance.set_start_coord(x, y)

    def set_end_coord(self, x, y):
        DrawOnCanvas.instance.set_end_coord(x, y)

    def draw_rectangle(self, x, y):
        DrawOnCanvas.instance.draw_rectangle(x, y)

    def draw_circle(self, x, y, r, colour="white"):
        DrawOnCanvas.instance.draw_circle(x, y, r, colour)

    # Draws a circle in the middle of the screen to represents the fixation size
    def draw_fixation_circle(self, r, x=-1, y=-1, color='red'):
        self.instance.draw_fixation_circle(r, x, y, color=color)

    # removes the fixation circle if it exists
    def remove_fixation_circle(self):
        self.instance.remove_fixation_circle()

    def get_aoi_dict(self):
        return DrawOnCanvas.instance.get_aoi_dict()

    def remove_dict_entry(self, name):
        DrawOnCanvas.instance.remove_dict_entry(name)

    #  Redraw the rectangles if they are erased for any reason
    def redraw_dict(self, xadj = 0):
        DrawOnCanvas.instance.redraw_dict(xadj)
