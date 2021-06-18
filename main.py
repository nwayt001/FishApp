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
#############################################
#Main Fisherman addon
#############################################
class FisherMan_App(object):
    # initialize fisherman class
    def __init__(self):      
        # computer vision parameters
        self.method = cv2.TM_SQDIFF
        self.sct = mss()
        self.bounding_box = {'top': 100, 'left': 0, 'width': 400, 'height': 300}
        self.bobber_img = cv2.imread('bobber.png')
        self.fishing = True
        # stream thread
        self.stream_thread = []
        # initialize gui window
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
        # stream thread
        self.stream_thread = threading.Thread(target=self.fishing_main)
        self.stream_thread.start()


    # main fishing state machine / loop
    def fishing_main(self):

        while self.fishing:
            
            # first find the bobber
            self.find_bobber()

            if (cv2.waitKey(1) & 0xFF) == ord('q'):
                cv2.destroyAllWindows()
                print('closing!')
                break

    # find bobber using CV templet matching
    def find_bobber(self):

        # grab a screen shot specificed by bounding box using mss
        self.captured_img = self.sct.grab(self.bounding_box)

        # save image to file
        to_png(self.captured_img.rgb, self.captured_img.size, output = 'screenshot.png')
        
        # read it back in
        self.captured_img = cv2.imread('screenshot.png')
        
        # perform perception via template matching to find the bobber
        result = cv2.matchTemplate(self.bobber_img, self.captured_img, self.method)
        
        # We want the minimum squared difference
        mn,_,mnLoc,_ = cv2.minMaxLoc(result)
        
        # Draw the rectangle:
        # Extract the coordinates of our best match
        MPx,MPy = mnLoc

        # Step 2: Get the size of the template. This is the same size as the match.
        trows,tcols = self.bobber_img.shape[:2]

        # Step 3: Draw the rectangle on large_image
        cv2.rectangle(self.captured_img, (MPx,MPy),(MPx+tcols,MPy+trows),(0,0,255),2)
        # display
        cv2.imshow('screen', self.captured_img)

        # retern the bobber location
        
    # stop fishing
    def end_fishing(self):
        self.fishing = False
        self.stream_thread.join()

# instantiate fisherman class
app = FisherMan_App()

