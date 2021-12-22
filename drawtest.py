import turtle
import pandas as pd
from tkinter import *
import easygui
import os
from PIL import Image
import win32gui, win32con

rootFolder = os.path.dirname(os.path.abspath(__file__)) + '\\'

#imagesLog = easygui.fileopenbox(msg = 'Please select the image logfile.', default = rootFolder)
imagesLog = 'C:\Projects\Open Sesame\Dot Probe\subject-99.csv'
#eyetrackerLog = easygui.fileopenbox(msg = 'Please select the eye tracker logfile.', default = rootFolder)
eyetrackerLog = 'C:\Projects\Open Sesame\Dot Probe\subject-99_TOBII_output.tsv'

df = pd.read_csv(eyetrackerLog, header=None, sep='\n')
df = df[0].str.split('\t', expand=True)
display_string = df[0][1]

df = pd.read_csv(eyetrackerLog, header=17, sep='\t')
df_img = pd.read_csv(imagesLog)

# get the screen resolution for eyetracker
strs = display_string.split(': ')
res_string = strs[1]
resolution = res_string.split('x')
sWidth = int(resolution[0])
sHeight = int(resolution[1])

def donothing():
    print("did nothing")

app = Toplevel()
app.geometry(res_string)        #  Make full screen

canvas = turtle.ScrolledCanvas(app, width = sWidth, height = sHeight)
canvas.pack(expand=True)

turt_scr = turtle.TurtleScreen(canvas)

#  Setup Turtle
t = turtle.RawTurtle(turt_scr)
t.color('white')
t.speed(0)

hwnd = win32gui.GetForegroundWindow()
win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

menubar = Menu(app)
menubar.add_command(label="Hello!", command=donothing)
menubar.add_command(label="Quit", command=app.quit)

app.config(menu=menubar)

#  Make and set the background image
def set_background(left_img, right_img, screen_w, screen_h, scr, num):

    # Get the left face image
    lImg = Image.open(rootFolder + 'Stimulus\\' + left_img, 'r')
    lImgW, lImgH = lImg.size
    # Get right face image
    rImg = Image.open(rootFolder + 'Stimulus\\' + right_img, 'r')
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
    tmpBGImgFile = rootFolder + 'BG\\tmp' + str(num) + '.gif'
    bg.save(tmpBGImgFile)
    #  Set the image to the screen background
    scr.bgpic(tmpBGImgFile)

#  Use the xy points to move the turtle
def trace_gaze_points(turt, scrn, xPoint, yPoint, delay):
    turt.setpos(xPoint, yPoint)
    scrn.delay(delay)

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

# Present tracking
turt_scr.clear()
set_background(faces[0][0], faces[0][1], sWidth, sHeight, turt_scr, 0)       #  Set the inital background

def run_through_trials():
    prevTime = 0.0  # Stores the previous time sample to calc the delay
    dly = 0.0       # Sample time for this fixation
    trial_count = 1
    track_data = False
    in_trial = False
    for index, row in df.iterrows():
        #  Are we in a trial
        if row['Event'] == 'start_trial':
            in_trial = True
            set_background(faces[trial_count-1][0], faces[trial_count-1][1], sWidth, sHeight, turt_scr, trial_count-1)
        elif row['Event'] == 'stop_trial':
            turt_scr.clear()
            trial_count = trial_count + 1
            in_trial = False
        #  Are both eyes tracking
        if row['ValidityLeft'] == 1.0 and row['ValidityRight'] == 1.0:
            track_data = True
        else:
            track_data = False
        #  If in trail and tracking data then trace the gaze points
        if in_trial and track_data:
            dly = row['TimeStamp'] - prevTime
            trace_gaze_points(t, turt_scr, row['GazePointX'] - float(sWidth)/2, row['GazePointY'] - float(sHeight) / 2, dly)

        prevTime = row['TimeStamp']

run_through_trials()
#set_background(faces[0][0], faces[0][1], sWidth, sHeight, turt_scr, 0)
#  Records the coordinates of the drawn bbox

def draw_aoe(event):
    x, y = event.x, event.y
    #if (str(event.type) == 'ButtonPress'):
    print('x: ' + str(x) + ', y: ' + str(y))
    # if canvas.old_coords:
    #     x1, y1 = canvas.old_coords
    #     canvas.create_line(x, y, x1, y1)
    # canvas.old_coords = x, y

#t.getcanvas().create_line(100, 100, 200, 200)


app.bind('<ButtonPress-1>', draw_aoe)
app.bind('<ButtonRelease-1>', draw_aoe)
#app.mainloop()
set_background(faces[0][0], faces[0][1], sWidth, sHeight, turt_scr, 0)       #  Set the inital background
#turtle.done()
turtle.Screen().exitonclick()
