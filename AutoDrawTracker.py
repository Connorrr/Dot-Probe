import pandas as pd
import tkinter as tk
import os
from PIL import Image
import numpy
from MainWindowController import MainWindowController
from BackgroundImageBuilder import BackgroundImageBuilder
from CSVLogfileMaker import CSVLogfileMaker

# Main fonts
LARGE_FONT= ("Verdana", 12)
NORM_FONT = ("Helvetica", 10)
SMALL_FONT = ("Helvetica", 8)

csv_maker = CSVLogfileMaker("test.csv")
col_name = numpy.array([["OK", "How", "You", "Be?"]])
row = numpy.array([['2', '3', '5', '7']])
csv_maker.set_column_names(col_name)
csv_maker.add_row(row)

#  Get the root root_folder
root_folder = os.path.dirname(os.path.abspath(__file__)) + '\\'

#imagesLog = easygui.fileopenbox(msg = 'Please select the image logfile.', default = root_folder)
imagesLog = 'C:\Projects\Open Sesame\Dot Probe\subject-99.csv'
#eyetrackerLog = easygui.fileopenbox(msg = 'Please select the eye tracker logfile.', default = root_folder)
eyetrackerLog = 'C:\Projects\Open Sesame\Dot Probe\subject-99_TOBII_output.tsv'

df = pd.read_csv(eyetrackerLog, header=None, sep='\n')
df = df[0].str.split('\t', expand=True)
display_string = df[0][1]
fix_degrees_string = df[0][3]
sample_time_str = df[0][9]
fix_pixel_str = df[0][13]
fix_dur = 150       #  fixation duration set in milliseconds and then converted to samples later on

df = pd.read_csv(eyetrackerLog, header=17, sep='\t')
df_img = pd.read_csv(imagesLog)

# get the screen resolution for eyetracker
strs = display_string.split(': ')
res_string = strs[1]
resolution = res_string.split('x')
s_width = int(resolution[0])
s_height = int(resolution[1])

# get the fixation vars()
strs = fix_degrees_string.split(': ')
fix_str = strs[1]
strs = fix_str.split(' d')      # remove 'dregrees' at the end of str
fix_deg = float(strs[0])

# get the fixation pixels
strs = fix_pixel_str.split(': ')
fix_str = strs[1]
strs = fix_str.split(' p')      # remove 'pixels' at the end of str
fix_pix = int(float(strs[0]))

# get tobii sample time in ms
strs = sample_time_str.split(': ')
sample_time_str = strs[1]
strs = sample_time_str.split(' m')      # cut off ms
sampl_time = float(strs[0])

pixels_per_deg = fix_pix / fix_deg

#  Make and set the background image
def set_background(left_img, right_img, screen_w, screen_h, scr, num):

    # Get the left face image
    lImg = Image.open(root_folder + 'Stimulus\\' + left_img, 'r')
    lImgW, lImgH = lImg.size
    # Get right face image
    rImg = Image.open(root_folder + 'Stimulus\\' + right_img, 'r')
    rImgW, rImgH = rImg.size
    # Make background
    bg = Image.new('RGBA', (screen_w, screen_h), (0,0,0,255))
    bgW, bgH = bg.size
    # image offsets
    lOffset = ((bgW//2)-(lImgW//2)-480, (bgH//2)-(lImgH//2))
    rOffset = ((bgW//2)-(rImgW//2)+480, (bgH//2)-(rImgH//2))
    # Make final image
    bg.paste(lImg, lOffset)
    bg.paste(rImg, rOffset)
    tmpBGImgFile = root_folder + 'BG\\tmp' + str(num) + '.gif'
    if os.path.exists(tmpBGImgFile):
        #print('attempting to remove:  ' + tmpBGImgFile)
        os.remove(tmpBGImgFile)
    #else:
        #print('couldn\'t find:  ' + tmpBGImgFile)

    bg.save(tmpBGImgFile)
    #  Set the image to the screen background
    scr.bgpic(tmpBGImgFile)

#  Use the xy points to move the turtle
def trace_gaze_points(turt, scrn, xPoint, yPoint, delay):
    turt.setpos(xPoint, yPoint)
    scrn.delay(delay)

trial_list = numpy.empty(len(df), dtype=int)


def add_trial_numbers():
    # adds the trial numbers to the event column of the df
    trial_count = 1
    in_trial = False
    for index, row in df.iterrows():
        #  Are we in a trial
        if row['Event'] == 'start_trial':
            in_trial = True
        elif row['Event'] == 'stop_trial':
            trial_count = trial_count + 1
            in_trial = False

        if in_trial:
            trial_list[index] = trial_count
        else:
            trial_list[index] = 0

add_trial_numbers()

#  Build Face Array
(rows, cols) = (df_img.shape[0], 2)
faces = [['tst' for i in range (cols)] for j in range(rows)]
for index, row in df_img.iterrows():
    #  Get the Face string
    left_img_str = str(row['face_no']) + row['left_image'] + row['mouth'] + '.jpg'
    right_img_str = str(row['face_no']) + row['right_image'] + row['mouth'] + '.jpg'
    #  Add those strings to the faces array
    faces[index][0] = left_img_str
    faces[index][1] = right_img_str

root = tk.Tk()
bg_builder = BackgroundImageBuilder(df_img, root_folder, s_width, s_height)
main_window = MainWindowController(root, s_width, s_height, df, bg_builder, trial_list, sampl_time, fix_pix, fix_deg, pixels_per_deg, fix_dur)

root.mainloop()
