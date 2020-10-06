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
import pickle as pkl
import nldas_pygrib_tools as npt
import time
from tqdm import tqdm

np.set_printoptions(threshold=sys.maxsize)

nc_year = 1980
year_splits = 10
recover = False
search_xy = False

# Write the NetCDF forcing data file.
proj_dir = '/home/NearingLab/projects/jmframe/nldas-grib/'
grib_dir = '/home/NearingLab/data/nldas/grib/NLDAS2.FORCING/'
write_dir = '/home/NearingLab/data/nldas/netcdf-single-cells/'+str(nc_year)+'/'

# Open an example file
fname = grib_dir + '1979/001/' + 'NLDAS_FORA0125_H.A'+ str(nc_year) +'0101.0000.002.grb'
if yearStart == 1979:
    fname = grib_dir + str(nc_year) +'/001/' + 'NLDAS_FORA0125_H.A19790101.0000.002.grb'
gbf_temp = pg.open(fname)
lats = gbf_temp[1].latitudes
lons = gbf_temp[1].longitudes
nrows = gbf_temp[11].values.shape[0]
ncols = gbf_temp[11].values.shape[1]

gvars = {0:'airtemp', 1:'spechum', 2:'airpres', 3:'forcingUGRD', 4:'windspd',
         5:'LWRadAtm',6:'forcingCONVfrac', 7:'forcingCAPE', 8:'forcingPEVAP', 9:'pptrate', 10:'SWRadAtm'}
fvars = {0:'airpres', 1:'airtemp', 2:'pptrate', 3:'spechum', 4:'windspd', 5:'LWRadAtm',6:'SWRadAtm'}

# Set start and end data information for the GRIB/NetCDF forcing data.
yearStart  = nc_year
monthStart = 1 
dayStart = 1 
if yearStart == 1979:
    hourStart = 13
else:
    hourStart = 0
startDateTime = dt.datetime(yearStart, monthStart, dayStart, hour = hourStart)
print("Will be calculating hours starting from: ")
print(startDateTime)
dayOfYearStart = dt.datetime.date(startDateTime).timetuple().tm_yday
yearEnd  = nc_year
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
list_fname = 'unmasked_xy_indices.txt'
if search_xy:
    ixy = -1 # Start at -1, so when we add the first value before the mask check, it goes to 0
    xy_list = []
    for x in tqdm(range(464)):
        for y in range(224):            
            ixy+=1 # lat/lon from the 1D arrays that correspond to these indices
            if np.ma.is_masked(gbf_temp[11].values[y, x]): # Skip masked cells, takes .0044 seconds
                continue
            xy_list.append(ixy)
    np.savetxt(list_fname, xy_list)
elif os.path.exists(list_fname):
    xy_list = list(np.genfromtxt(list_fname))
    for i, ixy in enumerate(xy_list):
        xy_list[i] = int(xy_list[i])
else:
    print("xy_list not working")
N = len(xy_list)
num_in_split = int(N/year_splits)

# Set up a dictionary for each cell, keys named from lat-lon
# Will be filled in with data from the grib files
start_time_index = 0
# if recover:
#     with open(G_pkl_file,'rb') as f:
#         G = pkl.read(f)
#     # Find where the saved file left off:
#     for iH, t in enumerate(tqdm(dates)):
#         i=0
#         ixy=xy_list[i]
#         xy = npt.name_xy(ixy, lats, lons)
#         v = fvars[0]
#         if np.isnan(G[xy][fvars[v]][iH]):
#             continue
#         else:
#             start_time_index = iH
#             break
# else:
G = {i:{} for i in range(year_splits)}
for isplit in range(year_splits):
    if isplit+1==year_splits: # Last split ends at i=N
        for i, ixy in enumerate(tqdm(xy_list[isplit*int(N/year_splits):N])):
            xy = npt.name_xy(ixy, lats, lons)
            G[isplit][xy] = npt.setForcingLists(H)
    else:
        for i, ixy in enumerate(tqdm(xy_list[isplit*int(N/year_splits):(isplit+1)*int(N/year_splits)])):
            xy = npt.name_xy(ixy, lats, lons)
            G[isplit][xy] = npt.setForcingLists(H)

# Main loop through the GRIB files by one hour intervals. open, extract, write, save
# Main loop through the NetCDF files by one hour intervals. 
# iH: Index to use for filling forcing data list.
for iH, t in enumerate(tqdm(dates)):
    
    # start from where the last save was made
#     if recover:
#         if iH < start_time_index:
#             continue
    
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
    #####   THIS IS the function to actually get the forcing data  ######
    g = npt.extractGrib(gbf, xy_list, nrows, ncols)

    # Looping takes too long. Need to get all values in vector
    # through x,y 1D indices.
    for i, ixy in enumerate(xy_list):
        
        # Calculate the split in the list from i.        
        isplit = int(np.floor(i/num_in_split))
        if isplit >= year_splits:
            isplit = year_splits - 1

        xy = npt.name_xy(ixy, lats, lons)
        
        # Need to get the two dimensional x,y values from the 1D xy
        x, y = np.unravel_index(ixy, (ncols,nrows))
                
        # Fill in the main Grib dictionary.
        for iv, v in enumerate(fvars):
            G[isplit][xy][fvars[v]][iH] = g[fvars[v]][i]
               
    # Save the whole data periodically.
    if (iH>0) and not iH % 2000 or t == dates[-1]:
        for isplit in range(year_splits):
            G_pkl_file = write_dir+'grib_export_'+str(isplit)+'.pkl'
            print('writing G[{}] at time: {}'.format(isplit, t))
            with open(G_pkl_file,'wb') as f:
                pkl.dump(G[isplit], f)
            os.chmod(G_pkl_file, 0o777)


# Save the forcing data for each cell, individually
print("Saving data in netCDF files")
for i, ixy in enumerate(tdqm(xy_list)):
    # Calculate the split in the list from i.        
    isplit = int(np.floor(i/num_in_split))
    if isplit >= year_splits:
        isplit = year_splits - 1
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
        G[isplit][xy]['SWRadAtm'], 
        G[isplit][xy]['LWRadAtm'], 
        G[isplit][xy]['airpres'], 
        G[isplit][xy]['airtemp'], 
        G[isplit][xy]['pptrate'], 
        G[isplit][xy]['spechum'], 
        G[isplit][xy]['windspd'], year)
    os.chmod(forcingDataName, 0o777)
