"""
A compact implementation of the mosaic algorithm used
in combination with a manual mosaic stitch.

Author: Simon Thomas
Date: January 2018

"""
# Import libraries
import cv2
import numpy as np

def findOffset(imageA, imageB, alg="SURF"):
    """
    Finds the the change in X and Y positions
    for similar features in two images.
    Arguments::
        imageA/imageB -- images where A.shape == B.shape
        alg -- feature detection algorithm. SURF is faster but less accurate

    Output:
        - Tuples (X, Y) change
    """
    # Set feature algorithm
    if alg == "SIFT":
        descriptor = cv2.xfeatures2d.SIFT_create()
    else:
        descriptor = cv2.xfeatures2d.SURF_create()
    # Extract features of imageA
    (kpsA, featuresA) = descriptor.detectAndCompute(imageA, None)
    kpsA = np.float32([kp.pt for kp in kpsA])
    # Extract features of imageB
    (kpsB, featuresB) = descriptor.detectAndCompute(imageB, None)
    kpsB = np.float32([kp.pt for kp in kpsB])

    # Match features in sets
    matcher = cv2.DescriptorMatcher_create("BruteForce")
    rawMatches = matcher.knnMatch(featuresA, featuresB, 2)

    matches = []
    # Loop over rawMatches 
    for m in rawMatches:
        # ensure the distance is within a certain ratio of each
        # other (i.e. Lowe's ratio test)
        ratio = 0.75
        if len(m) == 2 and m[0].distance < m[1].distance*ratio:
            matches.append((m[0].trainIdx, m[0].queryIdx))

    counts = dict()
    # loop through matches
    for m in matches:
        # find pixel positions of features
        (trainIdx,queryIdx) = m
        ptA = (int(kpsA[queryIdx][0]), int(kpsA[queryIdx][1]))
        ptB = (int(kpsB[trainIdx][0]), int(kpsB[trainIdx][1]))
        # find change in X and Y
        changeXY = (ptB[1]-ptA[1], ptB[0]-ptA[0])
        # add (x,y) pair to couner
        counts[changeXY] = counts.get(changeXY, 0) + 1

    # sort the pairs based on frequency
    pairs = sorted(list(counts.items()), key=lambda entry: entry[1])
    # Grab the most frequny pair i.e. pos -1
    # and swap, as in rows, cols format
    rowOff, colOff = pairs[-1][0][0], pairs[-1][0][1]

    # Switch directions on values
    return (-1*rowOff, -1*colOff)

def maskOverlap(canvasSlice, image):
    """ Creates a hybird image that pasts `image` onto the canvas only where 0's existed.
    Arguments:
        canvasSlice -- A slice of the canvas of same shape as image
        image -- the image to paste onto the canvas
    Output:
        image -- hybrid image ready to be inserted into bigger canvas
    """
    mask = (canvasSlice > 0)
    temp = image.copy()
    temp[mask] = 0
    return np.maximum(canvasSlice, temp)

def findCenterStart(image, rows, cols):
    """ Finds the position when the image will be inserted
    so it is at the center of the image.
    Arguments:
        image -- image to find center of
        rows/cols -- size of image

    Output:
        tuple -- (row, col) positions
    """
    return (image.shape[0] // 2 - (rows//2), image.shape[1] // 2 - (cols//2))

def computeStartPos(prevStart, rowOff, colOff, rows, cols):
    """
    Computes the starting and ending positions for new slice.
    """
    rowStart, rowEnd = prevStart[0] + rowOff, prevStart[0] + rowOff + rows
    colStart, colEnd = prevStart[1] + colOff, prevStart[1] + colOff + cols
    return rowStart, rowEnd, colStart, colEnd

 
