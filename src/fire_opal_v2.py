# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 14:56:56 2019

@author: Maureen

This script runs the Fire Opal program.

Structure: 
    - Defines functions
    - Runs FOR loop that batch processes image files from a directory and
    extracts data
    
Requirements:
    Astrometry.net API client
    fire_opal_settings.py
    Rawpy, cv2, astropy, datetime, os, scipy, numpy


"""
from fire_opal_settings import *
import os, rawpy, cv2, datetime, nova_client
import numpy as np
from scipy.ndimage import gaussian_filter
from astropy.wcs import WCS
from astropy.io import fits



def convert_to_grey(rgbimage):
    
    """ This function converts an RGB image to a 
    greyscale image by averaging the RGB values.
    
    Input: RGB image
    Output: Greyscale image """

    greyimage = np.sum(rgbimage, axis=2)/(3*255.0)
    return greyimage



def cloudy_or_clear(greyimage):
    
    """ 
    This function sorts greyscale images of the night sky into two
    categories: clear or cloudy. Returns Boolean True or False.
    
    Inputs: Greyscale image, upper intensity bound of background, lower
    intensity bound for stars, Gaussian filter sigma.
    Output: True if clear, False if cloudy 
    
    """

    c = np.abs(greyimage.astype('float64') - gaussian_filter(greyimage, cl_sigma).astype('float64'))
    # Make a defocused copy of original image and subtract from original
    # A cloudy input image results in pure noise, while a clear input image
    # has points.
    
    subimage = c[row1:row2, col1:col2]
    ignore = len(subimage[np.where(subimage<=cl_background_thresh)]) 
    # Count the number of pixels in the subimage below an intensity threshold 
    # defined as the background. 
    
    perc = 100*(len(subimage[np.where(subimage>cl_lower_thresh)]))/(500*500 - ignore + 1)
    # Calculate the percentage of pixels above the brightness threshold, after
    # low-intensity background pixels have been disregarded.   
    
    if perc > 0.:
        return True, greyimage
    else:
        return False, greyimage
    


def line_from_two_points(x1, y1, x2, y2):

    """
    This function calculates the slope and intercept of a line from two points.
    
    Inputs: two sets of (x,y) pixel coordinates
    Outputs: slope m, intercept b
    
    """
    if x2 == x1: 
        x2 += 1
    if y2 == y1:
        y2 += 1
    # Avoids NAN or 0 slope errors
    
    m = float(y2-y1)/float(x2-x1)
    b = (y2 - m*x2)
    return m, b



for file in os.listdir(datadirectory):
# The first loop processes all images in a directory and returns a text file
# containing streak data. The data consists of the filename of
# an image containing a satellite streak, together with coordinate and
# timestamp information used in the next step to calculate orbits.
    
    streaks = open(streaks_data,'a+')
    # Creates a .txt document to store data extracted from image processing loop
    processed_images = open(processingrecord, 'a+')
    # Creates a .txt document to store filenames of images as they are processed
    processed_images_read = open(processingrecord, 'r')   
    # Read-only version of processing record
    already_processed = processed_images_read.read().split()
    
    if file in already_processed:   
        processed_images.close()
        processed_images_read.close()
        streaks.close()
        continue
        # Skips already processed files and continues to next iteration
        
    else: 
        
        try:
            
            raw = rawpy.imread(datadirectory + file)
            rgb = raw.postprocess()
            grey = convert_to_grey(rgb)
            # Reads in RAW image, converts to RGB, converts to grey, in uint8
            # format for compatibility with cv2 library
            
            is_it_clear, greyscale_image = cloudy_or_clear(grey)
            # Returns True if the image is clear and False if cloudy
            # Also returns the greyscale image for further processing

            if is_it_clear == True:
                
                greyscale_image *= 255.0
                edges = cv2.Canny(greyscale_image.astype('uint8'), definitely_not_an_edge, definitely_an_edge, apertureSize=3)
                lines = cv2.HoughLinesP(edges, 1, np.pi/180, line_votes, minLineLength=50, maxLineGap=5)
                # First a Canny edge detector creates a binary black and white image
                # in which edges are shown in white. Next the Hough Line Parameters
                # transform calculates which edges are lines and returns the endpoints
                # of the lines.

                if lines is not None: 
                    
                    if lines.shape[0] > 1:
                        
                        # If the satellite streak has a width greater than one pixel,
                        # HoughLineP will interpret it as multiple lines placed very
                        # close together. We solve this by averaging the endpoints of
                        # the lines to get an estimate of the 'real' endpoint.
                        
                        x1 = np.mean(lines[: lines.shape[0],0,0].tolist(), dtype=np.float64)
                        y1 = np.mean(lines[: lines.shape[0],0,1].tolist(), dtype=np.float64)
                        x2 = np.mean(lines[: lines.shape[0],0,2].tolist(), dtype=np.float64)
                        y2 = np.mean(lines[: lines.shape[0],0,3].tolist(), dtype=np.float64)
        
                    elif lines.shape[0] == 1:
                        
                        # If HoughLinesP returns only one line, no further processing
                        # of the endpoints is needed.
                        
                        x1 = float(lines[:,0,0])
                        y1 = float(lines[:,0,1])
                        x2 = float(lines[:,0,2])
                        y2 = float(lines[:,0,3])
                    
                    centre_xcoordinate = int(x1 + (np.abs(x1-x2)/2.0))
                    centre_ycoordinate = int(y1 + (np.abs(y1-y2)/2.0))    
                    x_lo = max(0, centre_xcoordinate - box_length)
                    x_hi = min(centre_xcoordinate + box_length, len(greyscale_image[1]) - 1)
                    y_lo = max(0, centre_ycoordinate - box_length)
                    y_hi = min(centre_ycoordinate + box_length, len(greyscale_image[0]) - 1)
                    box_around_streak = greyscale_image[y_lo : y_hi, x_lo : x_hi]
                    # Calculates the central pixel of the streak and draws a box around it
                    # with sides of length box_length. This section of the image around
                    # the streak is extracted for astrometric calibration using
                    # nova.astrometry.net.
                    
                    filename = file.replace('.NEF', '_streak.png')
                    cv2.imwrite(str(detectionpath) + str(filename), box_around_streak)
                    # Saves section of image as separate .png image in a folder 
                    # designated for uploads to nova.astrometry.net
                    
                    uploadpath = str(uploads_from) + str(filename)
                    wcsfile = str(wcs_goes_to) + str(filename).replace('.png', '_wcs.fits')
                    # Specifies commands used in the nova.astrometry.net parser:
                    # uploadpath is the location+filename of the .png image
                    # wcsfile is the location+filename of the resulting wcs file 
                    # to be downloaded from nova.astrometry.net
                    
                    cmd = '%s %s --apikey %s --upload %s --wcs %s' % (pythonpath, clientpath, apikey, uploadpath, wcsfile)
                    os.system(cmd)
                    # Runs API to nova.astrometry.net. WCS files are returned to the
                    # directory specified in the variable wcs_goes_to
                    
                    hdu = fits.open(wcsfile)
                    w = WCS(hdu[0].header)
                    # Opens wcs file and extracts calibration information from header
                    # Note: Throws a warning that the axes of the WCS file are 0 
                    # when the expected number of axes is 2. This can be ignored,
                    # the program will continue running.
                    
                    ra1, dec1 = w.wcs_pix2world(x1, y1, 0, ra_dec_order=True)
                    ra2, dec2 = w.wcs_pix2world(x2, y2, 0, ra_dec_order=True)
                    # Uses wcs header information to calculate RA and DEC coordinates
                    # for the x,y endpoints of the streak. RA is always first, DEC second.
                         
                    slope, intercept = line_from_two_points(x1, y1, x2, y2)
                    # Fits a line to the streak and records line parameters
                    # for use in post-processing
                    
                    filename_list = list(filename)
                    timestamp = "".join(filename_list[15:21])
                    time = datetime.datetime.strptime(timestamp, '%H%M%S')
                    # Extracts timestamp from filename and converts into a
                    # datetime object
                    
                    endpointa_time = time.time()
                    endpointb_time = (time + datetime.timedelta(seconds=5)).time()
                    # Sets the times for the streak endpoints to be the image
                    # timestamp and the timestamp + shutter speed
                    
                    streaks.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (file, timestamp, ra1, dec1, x1, y1, ra2, dec2, x2, y2, endpointa_time, endpointb_time, slope, intercept))                    
                    processed_images.write(str(file) + ' clear_streak' + '\n')
                    processed_images.close()
                    processed_images_read.close()
                    streaks.close()
                    # Writes all extracted data to a .txt file and records
                    # as 'clear_streak'
                    
                elif lines == None:
                    
                    processed_images.write(str(file) + ' clear_streakless' + '\n')
                    processed_images.close()
                    processed_images_read.close()
                    streaks.close()
                    # If image is clear but has no streaks, records as
                    # 'clear_streakless'
                                
            else:
                    
                processed_images.write(str(file) + ' cloudy' + '\n')
                processed_images.close()
                processed_images_read.close()
                streaks.close()
                # If image is cloudy, records as 'cloudy'
                        
        except Exception as e:
        # If the processing throws an error for any reason, the program will
        # write ERROR to the processing record and continue to the
        # next iteration
            print(str(e))
            processed_images.write(str(file) + ' ERROR' + '\n')
            processed_images.close()
            processed_images_read.close()
            streaks.close()
            
                