# HistoImageSticher
## Manual Stitcher for histology images
![HistoImageStitcher](https://github.com/AbacusInLife/HistoImageStitcher/blob/master/Images/save.png)

### Requirements
Python 3.5+ is the only supported Python version and there are several modules required for this to run. The GUI is built with `tkinter` but the main functionality comes from `openCV`. You will will need to build openCV from source yourself, including the `contrib` modules found at https://github.com/opencv/opencv_contrib. Find a tutoiral online on how to install. The remaining packages can be seen in the `stitcher.py` and `mosaic.py` files.  

### Known Errors:
The overlap is not perfect everytime. To minimise errors, try to take images with at least 1/3 overlap in both directions. Even if you do your best, sometimes the placement is incorrect. There is currently no `Undo` function, so if you get a misplaced tile, unfortunately you will need to start again. However, this happens < 1% of the time and only where overlapping regions are *very* similar. If you want perfection, feel free to play around under the hood.

### Blank Canvas
In a terminal run `python3 mosaic.py`. Images from a microscope should be saved in the `Input` folder of this parent directory. 
![Blank Canvas](https://github.com/AbacusInLife/HistoImageStitcher/blob/master/Images/blank_canvas.png)

### Reading Images
Pressing **⌘ + G** will begin checking the `Input` folder of images and stich them based on their sequential order. 
![Reading](https://github.com/AbacusInLife/HistoImageStitcher/blob/master/Images/reading.png)

**Note:** *Images should be saved using a numerical convention, and the number of files in the `Input` folder should not exceed 9 at anyone time. This is to avoid files Image_1.png and Image_10 being grouped sequentially. Ideally you want to have no more than 1 to 2 images in the `Input` folder at anytime if you are imaging and stitching simultaneously.*

![Load](https://github.com/AbacusInLife/HistoImageStitcher/blob/master/Images/load.png)

Images will be read in and stitched to the canvas. A green box shows where the latest image is in the context of the full mosaic.
![Stich](https://github.com/AbacusInLife/HistoImageStitcher/blob/master/Images/stitching.png)

### Saving Images
Pressing **⌘ + G** will stop looking for images to add to the mosaic. Mosaics can be saved using the `Save` button. An error will occur if a correct filename is not entered. i.e anything other than \*.png,  \*.tiff or  \*.jpg. Mosaics are saved in the `Output` folder.

![Save](https://github.com/AbacusInLife/HistoImageStitcher/blob/master/Images/save.png)

Pressing **⌘ + R** will reset the canvas to blank. 

A high resolution stitch (65MB) can be seen [here](https://github.com/AbacusInLife/HistoImageStitcher/blob/master/Images/Stitch_1.png) 



