from PIL import Image
import os

#  This class builds the background images to be printed on the main canvas


class BackgroundImageBuilder:
    def __init__(self, df_img, root_folder, s_width, s_height):
        # System vars
        self.root_folder = root_folder
        # Stim images
        self.df_img = df_img
        self.face_arr = None
        # Screen vars
        self.s_width = s_width
        self.s_height = s_height
        # trial vars
        self.trial_no = None

        self.__build_face_arr()

    # returns the trial number associated with the current bg image
    def get_bg_trial_no(self):
        return self.trial_no

    def save_background_image(self, trial_no):
        self.trial_no = trial_no
        file_path = self.__set_background(self.face_arr[trial_no][0], self.face_arr[trial_no][1], self.s_width, self.s_height)
        return file_path

    #  Build Face Array
    def __build_face_arr(self):
        (rows, cols) = (self.df_img.shape[0], 2)
        self.face_arr = [['tst' for i in range(cols)] for j in range(rows)]
        for index, row in self.df_img.iterrows():
            #  Get the Face string
            left_img_str = str(row['face_no']) + row['left_image'] + row['mouth'] + '.jpg'
            right_img_str = str(row['face_no']) + row['right_image'] + row['mouth'] + '.jpg'
            #  Add those strings to the faces array
            self.face_arr[index][0] = left_img_str
            self.face_arr[index][1] = right_img_str

    #  Make and set the background image
    def __set_background(self, left_img, right_img, screen_w, screen_h):

        # Get the left face image
        lImg = Image.open(self.root_folder + 'Stimulus\\' + left_img, 'r')
        lImgW, lImgH = lImg.size
        # Get right face image
        rImg = Image.open(self.root_folder + 'Stimulus\\' + right_img, 'r')
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
        tmpBGImgFile = self.root_folder + 'BG\\tmpbg_' + str(self.trial_no) + '.gif'
        #if os.path.exists(tmpBGImgFile):
            #os.remove(tmpBGImgFile)
        bg.save(tmpBGImgFile)
        return tmpBGImgFile
