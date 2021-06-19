import numpy as np
from pynput import keyboard
import time
from pyautogui import press, typewrite, hotkey
import tkinter as tk
import numpy as np
import cv2
from mss import mss
from PIL import Image
import threading
from mss.tools import to_png

from pywinauto.findwindows    import find_window
from pywinauto.win32functions import SetForegroundWindow
#############################################
#Main Fisherman addon
#############################################
class FisherMan_App(object):
    # initialize fisherman class
    def __init__(self):      
        self.run_once = False
        # game window resolution
        self.SCREENWIDTH = 1920
        self.SCREENHEIGHT = 1080
        self.cx = int(self.SCREENWIDTH/2)
        self.cy = int(self.SCREENHEIGHT/2)
        self.capture_width = 800
        self.capture_height = 500

        # computer vision parameters
        self.sct = mss()
        self.bounding_box = {'top': self.cy - int(self.capture_height/2), 'left': -self.SCREENWIDTH+self.cx-int(self.capture_width/2),
         'width': self.capture_width, 'height': self.capture_height}
        self.bobber_img = cv2.imread('bobber.png')
        self.fishing = True
        self.threshold = 300000000
        self.stream_thread = []

        # gui window parameters
        self.win = tk.Tk()
        self.win.geometry("550x250")
        # Create title
        self.titleLabel = tk.Label(self.win, text = "WoW Fishing Addon")
        self.titleLabel.config(font =("Courier", 16))
        self.titleLabel.pack(pady=7)
        # setup main gui buttons
        self.button_dict = {}
        self.button_dict[0] =  tk.Button(self.win, text='Start fishing', command=self.start_fishing, bg='green',fg='white',font= 10)
        self.button_dict[0].pack()
        self.button_dict[1] = tk.Button(self.win, text='Stop fishing', command=self.end_fishing, bg='red',fg='white',font= 10)
        self.button_dict[1].pack()
        # status text
        self.status_text = "Ready to Start"
        self.statusTextField = tk.StringVar()
        self.statusTextField.set(self.status_text)
        self.statusLabel = tk.Label(self.win, textvariable=self.statusTextField)
        self.statusLabel.config(font =("Courier", 14))
        self.statusLabel.pack(pady=10)
        # start gui window
        self.win.mainloop()

    # start fishing addon
    def start_fishing(self):

        # bring wow window to the foreground
        SetForegroundWindow(find_window(title='World of Warcraft'))


        # stream thread
        self.stream_thread = threading.Thread(target=self.fishing_main)
        self.stream_thread.start()


    # main fishing state machine / loop
    def fishing_main(self):

        # cast fishing line
        self.cast_line() 

        # main fishing loop
        while self.fishing:
            print('### Fishing loop started ###')    

            # first find the bobber
            self.find_bobber()

            if (cv2.waitKey(1) & 0xFF) == ord('q'):
                cv2.destroyAllWindows()
                print('closing!')
                break

    def cast_line(self):

        # press key command to cast fishing line
        press('e')


    # find bobber using CV templet matching
    def find_bobber(self):

        # grab a screen shot specificed by bounding box using mss
        self.captured_img = self.sct.grab(self.bounding_box)

        # save image to file
        to_png(self.captured_img.rgb, self.captured_img.size, output = 'screenshot.png')
        
        # read it back in
        self.captured_img = cv2.imread('screenshot.png')
        
        # perform perception via template matching to find the bobber
        result = cv2.matchTemplate(self.bobber_img, self.captured_img, cv2.TM_SQDIFF)
        
        # We want the minimum squared difference
        mn,maxn,mnLoc,_ = cv2.minMaxLoc(result)
        #print(mn) 280000000
        
        # Draw the rectangle:
        # Extract the coordinates of our best match
        MPx,MPy = mnLoc

        # Step 2: Get the size of the template. This is the same size as the match.
        trows,tcols = self.bobber_img.shape[:2]

        # Step 3: Draw the rectangle on large_image
        # filter out if more than the threshold
        if mn<self.threshold:
            cv2.rectangle(self.captured_img, (MPx,MPy),(MPx+tcols,MPy+trows),(0,0,255),2)
        # display
        cv2.imshow('screen', self.captured_img)

        # retern the bobber location
        if self.run_once:
            self.fishing = False    
    # stop fishing
    def end_fishing(self):
        self.fishing = False
        self.stream_thread.join()

# instantiate fisherman class
app = FisherMan_App()

