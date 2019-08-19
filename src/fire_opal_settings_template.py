# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 13:09:30 2019

@author: Maureen

This file contains settings and parameters used in the Fire Opal process
flow. 

"""


""" Directory Paths
"""
txtpath = 'C:/Users/inner_000/Desktop/Research/Fire_Opal/txt/'
streaks_data = 'C:/Users/inner_000/Desktop/Research/Fire_Opal/streaks_data.txt'
# .txt file that stores data relating to satellite streaks extracted from
# image batch processing
processingrecord = 'C:/Users/inner_000/Desktop/Research/Fire_Opal/processed_images.txt'
# .txt file that records filenames of images as they are processed, this 
# avoids re-processing of images if there is an error or the program crashes
datadirectory = 'C:/Users/inner_000/Desktop/Research/Fire_Opal/test_set/'
# Directory containing images to be processed
pythonpath = 'C:/WPy64-3720/python-3.7.2.amd64/python.exe'
# Location of Python distribution (needed for command line in Windows)
clientpath = 'C:/WPy64-3720/python-3.7.2.amd64/Lib/nova_client.py'
# Location of Astrometry.net API client script
detectionpath = 'C:/Users/inner_000/Desktop/Research/Fire_Opal/detected_streaks/'
uploads_from = 'C:/Users/inner_000/Desktop/Research/Fire_Opal/detected_streaks/'
# Folder containing small images with detected streaks to be sent to
# Astrometry.net
wcs_goes_to = 'C:/Users/inner_000/Desktop/Research/Fire_Opal/detected_streaks/wcs/'
# Folder into which WCS files are saved when sent back from Astrometry.net


""" Astrometry.net API """

# An API key is needed to access astrometry.net. The API key is linked
# to a specific user account.
apikey = ''




""" Cloudy or Clear?:
    Variables in process step distinguishing cloudy nights from clear nights """

# Variation 1: Algorithm using pixel intensities (cloudy_or_clear) #

cl_background_thresh = 0.1 
# Pixel intensity threshold for background noise (disregard pixels below
# this value)
cl_lower_thresh=0.15 
# Pixel intensity threshold for stars (counts pixels above this intensity)
cl_sigma=10 
# Sigma used in Gaussian filter
row1 = int(2000) 
row2 = int(2500)
col1 = int(2000)
col2 = int(2500)
# Row and column values for subimage

# Variation 2: Algorithm using histogram bins (cloudy_or_clear_alt) #
# Not being used at the moment

cl_curve_thresh = 0.3
# Fraction of maximum histogram value where curve width is measured
axis_comp = 20.0
# How many times longer should the right-hand tail of the curve be?

""" Satellite Streak Detection:
    Variables in process step for extracting satellite streaks """
    
# Canny edge dector
definitely_not_an_edge = 90 # Below this gradient value, pixel is not an edge
definitely_an_edge = 180 # Above this gradient value, pixel is definitely an edge

# Hough line transform 
line_votes = 100 # How many votes for something to count as line (e.g. length of line)

# Section of image that contains streak
box_length = 600
# Distance in pixels from centre of box to edge, e.g. 250 would give a 500x500 box

""" Post-Processing """

floor_scale = 100
# The slope is multiplied by this factor. The floor function used in grouping
# rounds to the nearest integer. Since slopes in test data can have values
# such as 0.4578, 1.872, etc., rounding to whole integers isn't useful. 
# Multiply by floor_scale to get 45.78 and 187.2 - now integer rounding works!
# Effectively you are rounding to the 2nd decimal place. To round to the 3rd
# decimal place, change floor_scale to 1000.
