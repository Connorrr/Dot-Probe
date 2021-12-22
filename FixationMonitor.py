import math
from DrawOnCanvas import DrawOnCanvas
#  This class uses a window of samples and determines there is a fixation then draws it


class FixationMonitor:
    def __init__(self, fix_dur, samp_time, fix_pix):
        self.buffer = []            # [[x,y],[x,y],...]
        self.fix_dur = fix_dur
        self.samp_time = samp_time
        self.num_samples: int = int(math.ceil(self.fix_dur/self.samp_time))
        self.avg_fix = []           # The average x and y location for the fixation buffer
        self.fix_pix = int(fix_pix/2)    # The number of pixels a sample can be away from the average to register as a fixation ( /2 because it is a radius rather than diameter)
        #  Canvas Drawer
        self.canvas_drawer = DrawOnCanvas()
        #
    #  puts the sample at the end of the buffer
    def __update_buffer_forwards(self, sample):
        if (len(self.buffer) >= self.num_samples):
            self.buffer.pop(0)

        self.buffer.append(sample)

    #  Set the new samples buffer moving forwards in time
    def add_sample_forwards(self, sample):
        self.__update_buffer_forwards(sample)

    #  Sets a new fixation duration and nu,ber of smaples for fixation
    def set_fix_dur(self, fix_dur):
        self.fix_dur = fix_dur
        self.num_samples: int = int(math.ceil(self.fix_dur/self.samp_time))

    #  add entirely new buffer that is of length num_samples
    #  isdrawn = true if you want the fixation to be drawn on canvas
    def set_buffer(self, buffer, isdrawn):
        is_fixation = False
        if (len(buffer) != self.num_samples):
            print("Error:  Buffer must be of length: " + str(self.num_samples) + ", buffer length: " + str(len(buffer)))
        else:
            self.buffer = buffer
            self.__get_fixation_avg()
            is_fixation = self.__check_if_buffer_is_fixation(isdrawn)

        return is_fixation

    def __check_samp_val(self, samp):
        is_valid_sample = False
        if (samp[0] > 0 and samp[1] > 0):
            is_valid_sample = True
        #else:
            #print("Error:  Sample must be > 0: [" + str(samp[0]) + "," + str(samp[1]) + "]")

        return(is_valid_sample)

    #  Calculates the average x and y position from the samples
    #  returns the average [x,y] array or [-1,-1] if there are is a problem with the samples
    def __get_fixation_avg(self):
        x_avg = 0
        y_avg = 0
        is_pass = False

        for samp in self.buffer:
            is_pass = self.__check_samp_val(samp)
            if (is_pass):
                x_avg = x_avg + samp[0]
                y_avg = y_avg + samp[1]
            else:
                break

        if (is_pass):
            x_avg = x_avg/self.num_samples
            y_avg = y_avg/self.num_samples
        else:
            x_avg = -1
            y_avg = -1

        #print("avg: [" + str(x_avg) + "," + str(y_avg) + "] buffer: " + str(self.buffer))
        self.avg_fix = [int(x_avg), int(y_avg)]

    #  This method takes the buffer and checks that the samples are within a
    #  fixation tolerance distance from the average of that buffer.  Remember
    #  that the distance threshold will be half the fixation distance since it
    #  will be a radius around the average that determains the threshold.
    #  IMPORTANT:  Only all this method after __get_fixation_avg()
    def __check_if_buffer_is_fixation(self, isdrawn):
        is_fix = True
        for samp in self.buffer:
            x = samp[0]-self.avg_fix[0]
            y = samp[1]-self.avg_fix[1]
            d = math.sqrt(x*x + y*y)

            if (d > self.fix_pix):
                #print("x = " + str(x) + ", y = " + str(y) + ", d = " + str(d) + "fix pix = " + str(self.fix_pix))
                is_fix = False
                break
        if (is_fix):
            if (isdrawn):
                self.canvas_drawer.draw_fixation_circle(self.fix_pix, self.avg_fix[0], self.avg_fix[1], 'white')
        else:
            if (isdrawn):
                self.canvas_drawer.remove_fixation_circle()
        return is_fix
