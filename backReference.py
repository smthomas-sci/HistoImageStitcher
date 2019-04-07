# 
# Creates a background correction image
# 
# Simon Thomas
# 11th January, 2018

import argparse
import numpy as np
import cv2

# Parse command line arguments
parser = argparse.ArgumentParser(description='Convert video into mosaic.')
parser.add_argument('--image', type=str, help='Background reference image')
args = parser.parse_args()

# Read in reference image as grey-scale ie. '0'
im = cv2.imread(args.image, 0)

# Get brightest pixel in image
val = np.ndarray.max(im)

# Create matrix of max values
vals = np.ones(shape=im.shape, dtype="uint8")*val

# Find difference between max and image values
correct = cv2.subtract(vals, im)

# Save image
cv2.imwrite("correct.png", correct)



