import cv2
import numpy as np
import os
import tkinter as tk
from PIL import ImageTk, Image
import sys, os
import time
from stitcher import *
import threading

class Model(object):
    """ 
    The model component of a GUI application to stitch consecutive
    images together from the microscope.
    """
    def __init__(self):
        self.run = False
        self.Stitching = False
        self.canvas = np.zeros([60000, 60000,3], dtype="uint8")
        # Display setup
        self.stitch = None
        self.capture = None
        # Memory setup
        self.previous = None
        self.current = None
        # Image Size variations/reductions
        self.mul = 4
        self.rows = int(1920 / self.mul)
        self.cols = int(2448 / self.mul)
        # Distance measure
        self.dist = "Distances from Edge: N: 0, E: 0, S: 0, W: 0"

    def reset(self):
        """
        Resets the input and canvas ready for a new stitch.
        """
        self.__init__() # Reset all variables
        self.stitch = self.convertNumpy2Image(np.zeros([750,850,3], dtype="uint8"))
        self.capture = self.convertNumpy2Image(np.zeros([320,408, 3],dtype="uint8"))

    def checkForImage(self, PATH="./Input/"):
        """
        Checks for the latest image in the directory"

        Arguments:
            PATH - path of the directory to look in
        Returns:
            filename - filename inclusive of path
        """
        files = [ _ for _ in sorted(os.listdir(PATH)) if ".png" in _ and "Image" in _ ]
        if len(files) > 0:
            f = files[0]
            im = cv2.imread(PATH + f)
            os.remove(PATH + f)
            return im
        else:
           return None

    def convertNumpy2Image(self, array):
        """ Converts a cv2/numpy image to an tkinter Image object. """
        cv2image = cv2.cvtColor(array, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        return imgtk

    def save(self, filename):
        """ Saves the canvas to file. """
        print("Saving...", end="\r")
        canvas = self.canvas[self.N:self.S,self.W:self.E]
        cv2.imwrite("./Output/"+filename, canvas)
        print("Saved:",filename)

    def getNextImage(self):
        """
        The main method for loading and stitching images together.
        """
        # Get the next image
        frame = self.checkForImage()
        if frame is None:
            return False

        # ----------------------- #
        # Background correction
        background = cv2.imread("./Utilities/correct.png")
        frame = cv2.add(frame, background)
        # ----------------------- #


        # --- FIRST TIME --- #
        if self.Stitching == False:
            self.Stitching = True
            # Display current frame
            self.current = frame
            self.capture = self.convertNumpy2Image(cv2.resize(self.current, (408,320)))

            # --- ADD TO CANVAS --- #

            # Center of canvas
            center = findCenterStart(self.canvas, self.rows, self.cols)

            # Find positions to insert image
            rowStart, rowEnd, colStart, colEnd = computeStartPos(center, 0, 0,
                                                self.rows*self.mul, self.cols*self.mul)

            # Add first image to canvas
            self.canvas[rowStart:rowEnd, colStart:colEnd, :] = frame

            # Set previous starting position to center
            self.prevStart = center


            # MAX POSITIONS
            self.N = rowStart
            self.S = self.N + (self.rows*self.mul)
            self.W = colStart
            self.E = self.W + (self.cols*self.mul)

            temp = self.canvas[self.N:self.S,self.W:self.E]
            # BOX
            pt1 = (colStart, rowStart)
            pt2 = (colStart+self.cols, rowStart+self.rows)
            cv2.rectangle(temp, pt1, pt2, (255,0,0))
            # Update stich for display
            self.stitch = self.convertNumpy2Image(cv2.resize(temp, (850,750)))

            #Update distance
            self.dist = "Distances from Edge: N: {N}, E {E}, S: {S}, W:{W}".format(N=self.N,S=self.S, E=self.E, W=self.W)

            return True

        # --- EVERY OTHER TIME --- #
        else:
            self.previous = self.current
            self.current = frame

            cols = self.cols
            rows = self.rows
            mul = self.mul

            # Grab next image pair
            imageA = self.previous
            imageB = self.current
            imageA_small = cv2.resize(self.previous, (cols, rows))
            imageB_small = cv2.resize(self.current, (cols, rows))

            # Find difference between two images
            rowOff, colOff = findOffset(imageA_small, imageB_small,alg="SIFT")

            # Increase offset
            rowOff *= mul; colOff *= mul

            # Find splice coordinates
            rowStart, rowEnd, colStart, colEnd = computeStartPos(self.prevStart, rowOff,
                                                colOff, rows*mul, cols*mul)

            # Add image to canvas
            self.canvas[rowStart:rowEnd, colStart:colEnd, :] = maskOverlap(self.canvas[rowStart:rowEnd, colStart:colEnd, :], imageB)

            # Update previous StartPosition
            self.prevStart = (rowStart, colStart)

            # Update Max Positions
            if rowStart < self.N:
                self.N = rowStart
            if rowEnd > self.S:
                self.S = rowEnd
            if colStart < self.W:
                self.W = colStart
            if colEnd > self.E:
                self.E = colEnd

            # Crop for display
            temp = self.canvas[self.N:self.S,self.W:self.E].copy()
            # --- BOX --- #
            # Calculate placement of box
            distFromNorth = abs(self.N - rowStart)
            distFromWest = abs(self.W - colStart)
            # add bounding box
            pt1 = (distFromWest, distFromNorth)
            pt2 = (distFromWest+self.cols*self.mul, distFromNorth+self.rows*self.mul)
            cv2.rectangle(temp, pt1, pt2, (0,255,0), 20)
            # Update stich for display
            self.stitch = self.convertNumpy2Image(cv2.resize(temp, (850,750)))

        # --- ALL THE TIME --- #
        # Update capture everytime!
        self.capture = self.convertNumpy2Image(cv2.resize(self.current, (408,320)))

        # Add distance to help figure out where edge of canvas is!
        self.dist = "Distances from Edge: N: {N}, E {E}, S: {S}, W:{W}".format(N=self.N,S=self.S, E=self.E, W=self.W)
        return True

class View(object):
    """
    A digital microscope app.
    """

    # ----- VIEW ----------- #
    def __init__(self, model):
        self.master = tk.Tk()
        self.model = model

        # Master config
        self.master.title("Digital Microscope")
        self.master.resizable(width=False, height=False)
        self.master.config(background="#FFFFFF")

        # Main Window
        self.imageFrame = tk.Frame(self.master)
        self.imageFrame.grid(row=0, column=0, padx=10, pady=2)

        # Capture Frame
        self.lmain = tk.Label(self.imageFrame)
        self.lmain.grid(row=0, column=0)

        # Stitch Frame
        self.rmain = tk.Label(self.imageFrame)
        self.rmain.grid(row=0, column=1)

        # Auxilary Frame
        self.saveFrame = tk.Frame(self.imageFrame)
        self.distFrame = tk.Frame(self.rmain)
        self.runFrame = tk.Frame(self.rmain)
        # Input
        self.file = tk.StringVar()
        self.entry = tk.Entry(self.saveFrame, textvariable=self.file)
        self.file.set("")
        # Save button
        self.saveButton = tk.Button(self.saveFrame, text="Save Image");
        # Distance
        self.dist = tk.StringVar()
        self.distLabel = tk.Label(self.distFrame, textvariable=self.dist,
                fg="red",font=("Helvetica", 16), bg="black")
        self.dist.set("Distances from Edge: N: 0, E: 0, S: 0, W: 0")
        # Running 
        self.running = tk.StringVar()
        self.runLabel = tk.Label(self.distFrame, textvariable=self.running,
                fg="red", font=("Helvetica", 16), bg="black")
        self.running.set("Press ⌘ + G to start capture | ")

        # Capture Display
        frame = np.zeros((320,408, 3), dtype="uint8")
        imgtk = self.model.convertNumpy2Image(frame)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)

        # Stitch Display
        canvas = np.zeros([750,850,3], dtype="uint8")
        imgtk = self.model.convertNumpy2Image(canvas)
        self.rmain.imgtk = imgtk
        self.rmain.configure(image=imgtk)

        # Packaging
        self.lmain.pack(side=tk.LEFT)
        self.entry.pack(side=tk.LEFT)
        self.saveButton.pack(side=tk.RIGHT)
        self.runLabel.pack(side=tk.LEFT)
        self.distLabel.pack(side=tk.LEFT)
        self.rmain.pack(side=tk.RIGHT)
        self.saveFrame.place(relx=1.0, rely=1.0, x=-2, y=-2, anchor="se")
        self.distFrame.place(x=0, y=0, anchor="nw")
        self.imageFrame.pack()

    def mainloop(self):
        """
        Starts the main loop of the master frame.
        """
        self.master.mainloop()

class Controller(object):
    """
    The controller component of a GUI application to stitch consecutive
    images together from the microscope.

    The class contains methods that "Control" the GUI, that is, implements
    functionality for the buttons, what images to display, etc.

    """

    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Key bindings
        self.view.master.bind('<Command-n>', self.next)
        self.view.master.bind('<Command-s>', self.save)
        self.view.master.bind('<Command-r>', self.reset)
        self.view.master.bind('<Command-g>', self.run)
        self.view.saveButton.config(command=self.save)

    def save(self, event=None):
        """ Saves the canvas in its current form. """
        filename = self.view.file.get()
        self.model.save(filename)
        self.view.file.set("Saved.")

    def reset(self, event=None):
        self.model.reset()
        self.viewUpdate()

    def next(self, event=None):
        """
        Updates the canvas with a new image
        """
        im = self.model.getNextImage() # boolean
        if im is False:
            return
        self.viewUpdate()

    def viewUpdate(self):
        """
        Updates the GUI canvas and stitch."""
        # Update Capture
        imgtk = self.model.capture
        self.updateImage(self.view.lmain, imgtk)
        # Update Stitch 
        imgtk = self.model.stitch
        self.updateImage(self.view.rmain, imgtk)
        self.view.dist.set(self.model.dist)

    def updateImage(self, frame, image):
        """ Fast helper to update images."""
        frame.imgtk = image
        frame.configure(image=image)

    def toggleRun(self, event=None):
        if self.model.run == False:
            self.model.run = True
        else:
            self.model.run = False

    def run(self, event=None):
        self.toggleRun() # Switch on
        if self.model.run == True:
            self.view.running.set("Running... (⌘ + G to stop) | ")
            thread = threading.Thread(target=self.loop, args=())
            thread.daemon = True
            thread.start()
        else:
            self.view.running.set("Press ⌘ + G to start capture | ")

    def loop(self):
        # Keep looking in folder and loading image while pressed...
        while self.model.run == True:
            self.next()
            # Don't over do it...
            time.sleep(0.1)


class App(object):
    """
    An application class that holds the complete working
    environment of the application.
    """
    def __init__(self):
        self.model = Model()
        self.view = View(self.model)
        self.controller = Controller(self.model, self.view)

    def run(self):
        """
        Starts the application.
        """
        self.view.mainloop()

# Create and run the appplication
app = App()
app.run()



