# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 10:55:17 2019

@author: Maureen

Structure:
    - Defines classes, functions
    - Initializes lists
    - Reads in data from txt file
    - Processing
     - Saves output in txt file

Requirements:
    fire_opal_settings, groupby.itertools, numpy
    
"""

from fire_opal_settings import *
import numpy as np
from itertools import groupby



class StreakyImage:
    
    """
    A StreakyImage object is an image in which Fire Opal has detected at least one
    streak. Attributes are the filename, timestamp and a Streak object or list of
    Streak objects.
    
    """
    def __init__(self, filename, timestamp, streak):
        self.filename = filename
        self.timestamp = timestamp
        self.streak = streak
    
    def __repr__(self):
        return "StreakyImage()"



class Streak:
    
    """ 
    A Streak object represents a distinct streak found in an Image object. 
    Attributes are the two endpoints of the streak
    (in both right ascension/declination and x/y coordinates), the two 
    times associated with the endpoints, the slope and intercept of a
    line fit to the streak, the original file name, and the
    timestamp extracted from the original file name. 
    
    """
    
    def __init__(self, filename, timestamp, ra1, dec1, x1, y1, ra2, dec2, x2, y2, endpointa_time, endpointb_time, slope, intercept):
        self.filename = filename
        self.timestamp = endpointa_time 
        # Use datetime formatted time instead of timestamp string - this helps
        # with assigning RA/DEC coordinates to a time later on. Timestamp is
        # still accessible from StreakyImage object.
        self.ra1 = ra1
        self.dec1 = dec1
        self.x1 = x1
        self.y1 = y1
        self.ra2 = ra2
        self.dec2 = dec2
        self.x2 = x2
        self.y2 = y2
        self.endpointa_time = endpointa_time
        self.endpointb_time = endpointb_time
        self.slope = slope
        self.intercept = intercept
    
    def __repr__(self):
        return "Streak()"
    
    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

        

class OrbitalPoint:
    """
    
    Contains the right ascension, declination, and time of a streak endpoint.
    
    """
    def __init__(self, filename, ra, dec, time):
        self.filename = filename
        self.ra = ra
        self.dec = dec
        self.time = time
    
    def __repr__(self):
        return "OrbitalPoint()"
    
    def __str__(self):
        return "File is %s, coordinates are %s, %s, time is %s" % (self.filename, self.ra, self.dec, self.time)


def deg2HMS(ra, dec):
    
    """ Converts right ascension and declination in decimal degrees into 
    hours, minutes, and seconds in IOD format.
    
    Input: Right ascension and declination
    Output: A string combining the RA and DEC in hours, minutes seconds in 
    IOD format."""
    
    dsign = '+' # Sign of declination assumed to be positive
    if str(dec)[0] == '-': # If input has a negative sign, switch to negative
      dsign, dec = '-', abs(dec)
    deg = int(dec) # Degrees
    if deg < 10: 
        dhours = '0'+ str(deg)
        # If less than 10, append a 0 in front of the string to make sure it
        # complies with IOD format (HHMMSS)
    else:
        dhours = str(deg)
    decM = abs(int((dec-deg)*60)) # Minutes
    if decM < 10:
        dminutes = '0'+ str(decM)
    else:
        dminutes = str(decM)
    decS = round((abs((dec-deg)*60)-decM)*60) # Seconds
    if decS < 10:
        dseconds = '0' + str(decS)
    else:
        dseconds = str(decS)
    DEC = '{0}{1}{2}{3}'.format(dsign, dhours, dminutes, dseconds)
    # Seven-digit string consisting of sign plus HHMMSS
  
    raH = int(ra/15) # Hours
    if raH < 10:
        rhours = '0' + str(raH)
    else:
        rhours = str(raH)
    raM = int(((ra/15)-raH)*60) # Minutes
    if raM < 10:
        rminutes = '0' + str(raM)
    else:
        rminutes = str(raM)
    raS = round(((((ra/15)-raH)*60)-raM)*60) # Seconds
    if raS < 10:
        rseconds = '0' + str(raS)
    else:
        rseconds = str(raS)
    RA = '{0}{1}{2}'.format(rhours, rminutes, rseconds)
    # Six-digit string consisting of HHMMSS
  
    return str(RA+DEC)

list_of_streaky_images = []
# Initialize a list to contain the StreakyImage objects created from recorded
# data
list_of_satellites = []
# Initialize a list to contain distinct but unidentified satellites

""" Processing starts here """
""" Data extraction """
data = open(streaks_data, 'r')
# Opens txt file where data from Fire Opal image processing is stored
extracted_data = data.readlines()
# Creates list of lines in the txt file as list of strings
for line_of_data in extracted_data:
    get_data = line_of_data.split(',') # List of data points in a line
    one_streak = Streak(get_data[0], get_data[1], float(get_data[2]), float(get_data[3]), float(get_data[4]), float(get_data[5]), float(get_data[6]), float(get_data[7]), float(get_data[8]), float(get_data[9]), get_data[10], get_data[11], floor_scale*float(get_data[12]), float(get_data[13]))
    # Assigns extracted data to a Streak data object. See fire_opal_settings.py
    # for note about floor_scale, which is multiplying the slope of the streak.
    streak_image = StreakyImage(get_data[0], get_data[1], one_streak)
    # Assigns Streak object to a Streaky Image object
    list_of_streaky_images.append(streak_image)
    # Creates list of Streaky Image objects

""" Identification of satellite trail over multiple images """
slope_list = []
for streakyimage in list_of_streaky_images:
    slope_list.append(streakyimage.streak.slope)
# Creates a list of slopes of all streaks

groups = []  
for key, group in groupby(slope_list, np.floor):
    groups.append(list(group))
# Creates list of groups of slope values, e.g. [[2.1, 2.5, 2.3], [45.6, 45.8, 45.3]]
# Streaks with the same slope are assumed to be the same streak
    
""" Determination of direction of satellite trail """

for j in range(0,len(groups)): # Selects one group at a time
    images_with_same_streak = [] 
    for streakyimage in list_of_streaky_images:        
        if streakyimage.streak.slope in groups[j]:
            images_with_same_streak.append(streakyimage)
    # Creates a list of StreakyImage objects that contain the same streak (i.e.
    # streaks have the same slope).StreakyImage objects are appended in 
    # CONSECUTIVE order, which allows the next block of code to function.
    
    if images_with_same_streak[0].streak.x1 == images_with_same_streak[1].streak.x1: # If streak is vertical, x-endpoints are identical (fringe case)
        if images_with_same_streak[0].streak.y1 > images_with_same_streak[1].streak.y1: # Find direction of trail based on movement of y-endpoint
            for i in range(0, len(images_with_same_streak)):
                images_with_same_streak[i].streak.endpointa_time = images_with_same_streak[i].streak.endpointb_time
                images_with_same_streak[i].streak.endpointb_time = images_with_same_streak[i].streak.timestamp
        else:
            pass
    elif images_with_same_streak[0].streak.x1 > images_with_same_streak[1].streak.x1: # If trail is moving in reverse, consecutive x-endpoints will have smaller values
        for i in range(0,len(images_with_same_streak)):
            images_with_same_streak[i].streak.endpointa_time = images_with_same_streak[i].streak.endpointb_time
            images_with_same_streak[i].streak.endpointb_time = images_with_same_streak[i].streak.timestamp
    else:
        pass

    # This section of code compares the first image in the list to the second
    # image and checks which direction the streak endpoints have moved. If the
    # trail is moving "in reverse" (away from the origin), the code swaps the
    # times associated with each endpoint.
    
    points_for_one_satellite = []
    for image in images_with_same_streak:         
        point1 = OrbitalPoint(image.filename, image.streak.ra1, image.streak.dec1, image.streak.endpointa_time)
        point2 = OrbitalPoint(image.filename, image.streak.ra2, image.streak.dec2, image.streak.endpointb_time)
        points_for_one_satellite.append(point1)
        points_for_one_satellite.append(point2)
        # Creates OrbitalPoints objects and appends to a list of points 
        # belonging to the same satellite
    list_of_satellites.append(points_for_one_satellite)
    # Master list of unidentified satellites

""" Formatting of data as IOD and saving in txt file """
count = 0       
for sat in list_of_satellites:
    count += 1
    txtname = 'satellite%s.txt' % count
    # Gives unidentified satellites consecutively numbered filenames
    with open(txtpath + txtname, 'a+') as txtFile:
        for point in sat:
            prefix = '99999 99 999999 1234 E ' 
            # 9's are fillers, 1234 is the station code
            datetag = (point.filename[4:8] + point.filename[9:11] + point.filename[12:14] + str(point.time).replace(':','')).replace(' ','')
            # Creates date and time from filename and time
            timeunc = ' 00 00 '
            # Time uncertainty, filler
            ra_dec = deg2HMS(point.ra, point.dec)
            # RA and DEC converted into IOD format
            suffix = ' 00 S\n' 
            # Positional uncertainty, filler
            file_line = prefix + datetag + timeunc + ra_dec + suffix
            txtFile.write(file_line)
        txtFile.close()
# Creates a separate txt file for each satellite. Txt file contains the
# (ra, dec, time) points for the satellite in IOD format.
        
