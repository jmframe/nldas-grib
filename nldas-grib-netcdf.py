#!/home/jmframe/programs/anaconda3/python2
# This scrip is meant to convert all the NLDAS forcing data
# From GRIB format to NetCDF format.
# Specifically for input for NeuroHydrology

import datetime as dt
import numpy as np
import netCDF4 as nc # http://unidata.github.io/netcdf4-python/
import pygrib as pg
import sys
import os
from tqdm import tqdm
import pickle as pkl
import nldas_pygrib_tools as npt
import time

np.set_printoptions(threshold=sys.maxsize)

nc_year=1980

# Write the NetCDF forcing data file.
grib_dir = '/home/NearingLab/data/nldas/grib/NLDAS2.FORCING/'
write_dir = '/home/NearingLab/data/nldas/netcdf-single-cells/'+str(nc_year)+'/'

# Open an example file
fname = grib_dir + '1979/001/' + 'NLDAS_FORA0125_H.A19790101.1300.002.grb'
#fname = grib_dir + '2019/001/' + 'NLDAS_FORA0125_H.A20190101.0000.002.grb'
gbf_temp = pg.open(fname)
lats = gbf_temp[1].latitudes
lons = gbf_temp[1].longitudes
nrows = gbf_temp[11].values.shape[0]
ncols = gbf_temp[11].values.shape[1]
N = nrows*ncols

gvars = {0:'airtemp', 1:'spechum', 2:'airpres', 3:'forcingUGRD', 4:'windspd',
         5:'LWRadAtm',6:'forcingCONVfrac', 7:'forcingCAPE', 8:'forcingPEVAP', 9:'pptrate', 10:'SWRadAtm'}
fvars = {0:'airpres', 1:'airtemp', 2:'pptrate', 3:'spechum', 4:'windspd', 5:'LWRadAtm',6:'SWRadAtm'}

# Set start and end data information for the GRIB/NetCDF forcing data.
yearStart  = 1979
monthStart = 1 
dayStart   = 1 
hourStart  = 13
startDateTime = dt.datetime(yearStart, monthStart, dayStart, hour = hourStart)
print("Will be calculating hours starting from: ")
print(startDateTime)
dayOfYearStart = dt.datetime.date(startDateTime).timetuple().tm_yday
yearEnd  = 1979
monthEnd = 12
dayEnd   = 31 
hourEnd  = 23
endDateTime = dt.datetime(yearEnd, monthEnd, dayEnd, hour = hourEnd)
dayOfYearEnd = dt.datetime.date(endDateTime).timetuple().tm_yday

# Initializing the directory, but will change each day and year.
mainDirectory = '/home/NearingLab/data/nldas/grib/NLDAS2.FORCING/'
startDirectory = mainDirectory + str(yearStart)  + "/" \
    + str("{:03d}".format(dayOfYearStart))  + "/"
endDirectory = mainDirectory + str(yearEnd)  + "/" \
    + str("{:03d}".format(dayOfYearEnd))  + "/"
filePrefix = 'NLDAS_FORA0125_H.A'
fileSufix = '.002.grb'

# specify the data and time to fine the correct file in this name format
startFileDateTime = npt.dateForFile(yearStart, monthStart, dayStart, hourStart)
endFileDateTime = npt.dateForFile(yearEnd, monthEnd, dayEnd, hourEnd)
#Add prefix and sufix to the date to create the whole file name.
startFile = npt.getFileName(startFileDateTime, startDirectory, "A")
endFile = npt.getFileName(endFileDateTime, endDirectory, "A")

# Need to get the GRIB time for the first and last files
#Start the loop at the first date in the files.
year1, month1, day1, hour1 = npt.dateFromGRIB(startFile)
t = dt.datetime(year1, month1, day1, hour=hour1)
#Then have the loop run until the last file date.
year2, month2, day2, hour2 = npt.dateFromGRIB(endFile)
endTime = dt.datetime(year2, month2, day2, hour=hour2)
# Set timestep to move forward, to run through the files
deltime = dt.timedelta(hours=1)
# Estimate the number of hours in the record
H = endTime - t # (t = startDateTime)
# Convert the time difference to hours) 
H = int(H.total_seconds()/60/60) + 1
time_series = [0 for x in range(H)]

# Make a list of all the times to loop through
dates = [startDateTime + deltime*h for h in range(H)]
len(dates)

# find all the masked cells before the main loop, and avoid them
ixy = -1 # Start at -1, so when we add the first value before the mask check, it goes to 0
xy_list = []
for x in tqdm(range(464)):
    for y in range(224):            
        ixy+=1 # lat/lon from the 1D arrays that correspond to these indices
        if np.ma.is_masked(gbf_temp[11].values[y, x]): # Skip masked cells, takes .0044 seconds
            continue
        xy_list.append(ixy)

# Set up a dictionary for each cell, keys named from lat-lon
# Will be filled in with data from the grib files
G = {}
for ixy in tqdm(xy_list):
    xy = npt.name_xy(ixy, lats, lons)
    G[xy] = npt.setForcingLists(H)

# Main loop through the GRIB files by one hour intervals. open, extract, write, save
# Main loop through the NetCDF files by one hour intervals. 
# iH: Index to use for filling forcing data list.
for iH, t in enumerate(tqdm(dates)):

    hoursSinceStartDate = t - startDateTime
    hoursSinceStartDate = int(hoursSinceStartDate.total_seconds()/60/60)
    time_series[iH] = float(hoursSinceStartDate)

    # The files have both A and B versions.
    AB = "A"
    # Set the strings for the file name
    iYear, iMonth, iDay, iHour = npt.getValuesFromDateTime(t)
    # Get the datetime stuff in strings to be used in the NetCDF file call.
    dateTime4File = npt.dateForFile(iYear, iMonth, iDay, iHour)
    # Need to change the directory to reflect the loop data
    directory = npt.changeDirectory(t, grib_dir)
    # Put the file name together, this includes the full path
    fileName = npt.getFileName(dateTime4File, directory, AB)
    # Open the file for this particular data & time.
    try:
        gbf = pg.open(fileName)
    except:
        # skip the file
        print('File not found: \n',fileName)
        continue
    
#####################################################################
#####################################################################
#####   THIS IS A MAJOR CHANGE, AND IS NOT WORKING YET  #############
    g = extractGrib(gbf, xy_list, nrows, ncols)
#####   NEED TO COLLECT DATA IN VECTOR, THEN ASSIGN TO THE CELL SOMEHOW


    # Looping takes too long. Need to get all values in vector
    # through x,y 1D indices.
    for ixy in xyloop:

        xy = npt.name_xy(ixy, lats, lons)
        
        # Need to get the two dimensional x,y values from the 1D xy
        x, y = np.unravel_index(ixy, (ncols,nrows))
                
        # Fill in the main Grib dictionary.
        for iv, v in enumerate(fvars):
            G[xy][fvars[v]][iH] = g[fvars[v]][ixy]

# Save the whole data periodically.
save_G_name = write_dir+'grib_export.pkl'
with open(save_G_name,'wb') as f:
    pkl.dump(G, f)
os.chmod(save_G_name, 0o777)

# Save the forcing data for each cell, individually
for ixy in tqdm(xy_list):
    xy = npt.name_xy(ixy, lats, lons)
    x, y = np.unravel_index(ixy, (ncols,nrows))
    lat=lats[ixy]
    lon=lons[ixy]
    timestp=3600 #seconds
    # Write the NetCDF forcing data file.
    fname = "{}-{}".format(lat, -lon)
    forcingDataName = write_dir + fname +'.nc'
    forcing = nc.Dataset(forcingDataName, 'w', format='NETCDF4_CLASSIC')
    forcing.title = "NLDAS forcing "+fname
    forcing.description = 'NLDAS forcing data for '+fname
    forcing = npt.fillForcing(forcing, H, lat, lon, timestp, time_series, 
        G[xy]['SWRadAtm'], 
        G[xy]['LWRadAtm'], 
        G[xy]['airpres'], 
        G[xy]['airtemp'], 
        G[xy]['pptrate'], 
        G[xy]['spechum'], 
        G[xy]['windspd'])
    os.chmod(forcingDataName, 0o777)


