#!/home/jmframe/programs/anaconda3/python2
# This scrip is meant to convert all the NLDAS forcing data
# From GRIB format to NetCDF format.
# Specifically for input for the SUMMA hydrologic model

import datetime as dt
import numpy as np
import netCDF4 as nc # http://unidata.github.io/netcdf4-python/
import scipy as sp
import pygrib as pg
import numpy.ma as ma
import array as arr

#BEGIN #######################################################################
#BEGIN #  SETTING UP THE FORCING DATA AND GRIB FILE IMPORT  ##################
#BEGIN #######################################################################
# Set the location for the forcing data
latCatchment = 34.22223 #take this from settings/summa_zLocalAttributes.nc
lonCatchment = -118.17757 #take this from settings/summa_zLocalAttributes.nc

# Write the NetCDF forcing data file.
directory = '/home/jmframe/runs/summaCAMELS/11098000/data/'
forcingDataName = directory + 'forcing.nc'
forcing = nc.Dataset(forcingDataName, 'w', format='NETCDF4_CLASSIC')
forcing.title = "11098000 SUMMA model, CAMELS catchments"
forcing.description = 'SUMMA forcing data for 11098000'

# Set start and end data information for the GRIB/NetCDF forcing data.
yearStart  = 1979
monthStart = 1
dayStart   = 1
hourStart  = 13
startDateTime = dt.datetime(yearStart, monthStart, dayStart, hour = hourStart)
print("Will be calculating hours starting from: ")
print(startDateTime)
dayOfYearStart = dt.datetime.date(startDateTime).timetuple().tm_yday
yearEnd  = 1980
monthEnd = 10
dayEnd   = 1
hourEnd  = 12
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
#END #########################################################################
#END ###  SETTING UP THE FORCING DATA AND GRIB FILE IMPORT  ##################
#END #########################################################################

# Search for nearest decimal degree in an array of decimal degrees and return the index.
# np.argmin returns the indices of minimum value along an axis.
# so subtract dd from all values in dd_array, take absolute value and find index of minimum
def geo_idx(dd, dd_array):
    geo_idx = (np.abs(dd_array - dd)).argmin()
    return geo_idx

# Search and return the single index in the GRIB file with the lat/long found from geo_idx
def geo_idx_1(lat_val, lon_val, lats, lons):
    ilat = 0
    ilon = 0
    print("Looking for lat/lon index values")
    #Loop through the one dimensional latitude list,
    #Then we'll calculate where we should be in a two dimensional array
    for i in range(0, len(lats)):
        #At some point we should hit the SINGLE location in the 1D list...
        #Where the latitude and longitude values match our grid with our point of interest
        if lats[i] == lat_val and lons[i] == lon_val:
            #When this happens return those values, because we found our treasure
            return [ilat, ilon]
        #If for some reason we never find the treasure, let the user know.
        #And then end the loop before we get an error for the (i+1) index call
        if i == len(lats):
            print("ERROR: CAN NOT FIND THE INDEXIES FOR LATITUDE AND LONGITUDE!!!!!!!!")
            break
        #If latitudes reach the end of their cycle, then restart
        #The latitudes stay constant through the longitudes, then...
        #When the longitudes reach the minimum, the latitude moves down one.
        if lats[i] != lats[i + 1]:
            #Move on, because we've cycled through the longitudes...
            # associated with this latitude
            ilat = ilat + 1
            #The longitudes reset, so the index goes back to zero for the 2D array.
            ilon = 0
        else:
            #The longitudes keep moving while the latitude stays constant.
            ilon = ilon + 1

def dateForFile(year, month, day, hour):
    # Set the strings for the file name
    yearStr = str("{:02d}".format(year))
    monthStr = str("{:02d}".format(month))
    dayStr = str("{:02d}".format(day))
    hourStr = str("{:02d}".format(hour))
    dateTime = yearStr + monthStr + dayStr + '.' +  hourStr + '00'
    return dateTime

def changeDirectory(iDateTime):
    year = dt.datetime.date(iDateTime).year
    day = dt.datetime.date(iDateTime).timetuple().tm_yday
    directory = mainDirectory + str(year)  + "/" + str("{:03d}".format(day))  + "/"
    return directory

def getFileName(dateTime4File, directory, AB):
    if AB == "A":
        filePrefix = 'NLDAS_FORA0125_H.A'
    elif AB == "B":
        filePrefix = 'NLDAS_FORB0125_H.A'
    fileSufix = '.002.grb'
    fileName = directory + filePrefix + dateTime4File + fileSufix
    return fileName

def dateFromNetCDF(fileName):
    file_in = nc.Dataset(fileName,"r",format="NETCDF4")
    t_unit = file_in.variables["time"].units # get unit  "days since 1950-01-01T00:00:00Z"
    print("NetCDF file units for time are:")
    print(t_unit)
    year = int(t_unit[12:15+1])
    month = int(t_unit[17:18+1])
    day = int(t_unit[20:21+1])
    hour = int(t_unit[23:24+1])
    return t_unit, year, month, day, hour;

def dateFromGRIB(fileName):
    file_in = pg.open(fileName)
    gribData = file_in.select()[0]
    year = int(gribData.year)
    month = int(gribData.month)
    day = int(gribData.day)
    hour = int(gribData.hour)

    return year, month, day, hour;

def getValuesFromDateTime(iDateTime):
    iYear = dt.datetime.date(iDateTime).year
    iMonth = dt.datetime.date(iDateTime).month
    iDay = dt.datetime.date(iDateTime).day
    iHour = dt.datetime.time(iDateTime).hour
    return iYear, iMonth, iDay, iHour

# specify the data and time to fine the correct file in this name format
startFileDateTime = dateForFile(yearStart, monthStart, dayStart, hourStart)
endFileDateTime = dateForFile(yearEnd, monthEnd, dayEnd, hourEnd)

#Add prefix and sufix to the date to create the whole file name.
startFile = getFileName(startFileDateTime, startDirectory, "A")
endFile = getFileName(endFileDateTime, endDirectory, "A")

# Need to get the GRIB time for the first and last files
#Start the loop at the first date in the files.
year1, month1, day1, hour1 = dateFromGRIB(startFile)
iDateTime = dt.datetime(year1, month1, day1, hour=hour1)
#Then have the loop run until the last file date.
year2, month2, day2, hour2 = dateFromGRIB(endFile)
endTime = dt.datetime(year2, month2, day2, hour=hour2)
# Set timestep to move forward, to run through the files
deltime = dt.timedelta(hours=1)

# Estimate the number of hours in the record
H = endTime - iDateTime # (iDateTime = startDateTime)
# Convert the time difference to hours) 
H = int(H.total_seconds()/60/60) + 1
# Set the vectors (Python List) with these hours for the forcing data
# Air pressure at the measurement height
airpres = [0 for x in range(H)] #[Pa]
# Air temperature at the measurement height
airtemp = [0 for x in range(H)]#[K]
# Downward longwave radiation at the upper boundary
LWRadAtm = [0 for x in range(H)] #[W m-2] 
# Precipitation rate
pptrate = [0 for x in range(H)] #[kg m-2 s-1]
# Specific humifity at the measurement height
spechum = [0 for x in range(H)] #[g g-1]
# Downward shortwave radiation at the upper boundary
SWRadAtm = [0 for x in range(H)] #[W m-2]
# Observation time
time = [0 for x in range(H)] #[days since 1979-01-01 00:00:00]
#wind speed at the measurement height
windspd = [0 for x in range(H)] #[m s-1]

# Main loop through the NetCDF files by one hour intervals. 
iH = -1 #Index to use for filling forcing data list.
while iDateTime <= endTime:
    print("----------------------------------------------------")
    print("Current data & time in the main loop is (iDateTime): ")
    print(iDateTime)

    ########### ADD THIS TYPE OF CODE TO MAIN LOOP!!!! ##########
    ########### ADD THIS TYPE OF CODE TO MAIN LOOP!!!! ##########
    ########### ADD THIS TYPE OF CODE TO MAIN LOOP!!!! ##########
    hoursSinceStartDate = iDateTime - startDateTime 
    hoursSinceStartDate = int(hoursSinceStartDate.total_seconds()/60/60)
    time[iH] = float(hoursSinceStartDate)                               
    print("Hours since the start date: %d" %hoursSinceStartDate)

    # The files have both A and B versions.
    AB = "A"
    # Set the strings for the file name
    iYear, iMonth, iDay, iHour = getValuesFromDateTime(iDateTime)
    # Get the datetime stuff in strings to be used in the NetCDF file call.
    dateTime4File = dateForFile(iYear, iMonth, iDay, iHour)
    # Need to change the directory to reflect the loop data
    directory = changeDirectory(iDateTime)
    # Put the file name together, this includes the full path
    fileName = getFileName(dateTime4File, directory, AB)
    # Open the file for this particular data & time.
    try:
        grbForce = pg.open(fileName)
        # if the file exists, then advance the list index by one.
        iH = iH + 1
        # Store configuration file values
    except:
        # skip the file
        print('File not found:')
        print(fileName)
        iDateTime = iDateTime + deltime
        continue
    # Find the index of the cell closest to the CAMELS latlon
    lats = grbForce[1].latitudes
    lons = grbForce[1].longitudes
    np.set_printoptions(threshold=np.nan)
    #Find the nearest lat/lon indeces to the point location
    #The problem with these functions is that there are multiple of each
    lat_idx = geo_idx(latCatchment, lats) #Seperate index for lat and lon
    lon_idx = geo_idx(lonCatchment, lons) #Seperate index for lat and lon
    #Then find the actual lat/lon values, from the indices
    lat_val = lats[lat_idx]
    lon_val = lons[lon_idx]
    print("Using latitude and longitude values: %f & %f" %(lat_val, lon_val))
    #But actually the original indices are not quite correct...
    #So we need to narrow down the indices to be exact
    [lat_idx, lon_idx] = geo_idx_1(lat_val, lon_val, lats, lons)
    print("The array lat/lon indices are: %d & %d" %(lat_idx, lon_idx))
    # Loop through the GRIB messages and save them
    # when their indicator ID match the variables we want
    print("List index is equall to: %d" %iH)
    for grb in grbForce:
        if grb['indicatorOfParameter'] == 11:
            airtemp[iH] = grb.values[lat_idx, lon_idx]
            print("TMP, 2-m above ground Temperature [K]: %f" %airtemp[iH])
        if grb['indicatorOfParameter'] == 51:
            spechum[iH] = grb.values[lat_idx, lon_idx]
            print("SPFH, 2-m above ground Specific humidity [kg/kg]: %f" %spechum[iH])
        if grb['indicatorOfParameter'] == 1:
            airpres[iH] = grb.values[lat_idx, lon_idx]
            print("PRES, Surface pressure [Pa]: %f" %airpres[iH])
        if grb['indicatorOfParameter'] == 33:
            forcingUGRD = grb.values[lat_idx, lon_idx]
            print("UGRD, 10-m above ground Zonal wind speed [m/s]: %f" %forcingUGRD)
        if grb['indicatorOfParameter'] == 34:
            windspd[iH] = grb.values[lat_idx, lon_idx]
            print("VGRD, 10-m above ground Meridonal wind speed [m/s]: %f" %windspd[iH])
        if grb['indicatorOfParameter'] == 205:
            LWRadAtm[iH] = grb.values[lat_idx, lon_idx]
            print("DLWRF,  Longwave radiation flux downwards (surface) [W/m^2]: %f" %LWRadAtm[iH])
        if grb['indicatorOfParameter'] == 153:
            forcingCONVfrac = grb.values[lat_idx, lon_idx]
            print("CONVfrac, Fraction of total precipitation that is convective: %f" %forcingCONVfrac)
        if grb['indicatorOfParameter'] == 157:
            forcingCAPE = grb.values[lat_idx, lon_idx]
            print("CAPE, 180-mb above ground Convective Available Potential Energy: %f" %forcingCAPE)
        if grb['indicatorOfParameter'] == 228:
            forcingPEVAP = grb.values[lat_idx, lon_idx]
            print("PEVAP, Potential evaporation hourly total: %f" %forcingPEVAP)
        # Precipitation is an hourly total. mm/s = (mm/hr) / (1hr/60min) / (1min/60sec) 
        if grb['indicatorOfParameter'] == 61:
            pptrate[iH] = grb.values[lat_idx, lon_idx] / 60 / 60
            print("APCP, Precipitation hourly total [kg/m^2/hr]: %f" %pptrate[iH])
        if grb['indicatorOfParameter'] == 204:
            SWRadAtm[iH] = grb.values[lat_idx, lon_idx]
            print("DSWRF, Shortwave radiation flux downwards (surface) [W/m^2]: %f" %SWRadAtm[iH])
    grbForce.close()
    iDateTime = iDateTime + deltime


#BEGIN #######################################################################
#BEGIN #  WRITE DATA TO THE NETCDF FORCING DATA FILE   #######################
#BEGIN #######################################################################
forcing.createDimension('hru', 1)
forcing.createDimension('time', H)
### createVareables in new data set
forcing.createVariable('hruId', np.int32, ('hru',))
forcing.variables['hruId'].units = 'id number'
forcing.variables['hruId'].long_name = 'The Hydrologic Response Unit identification number'
forcing.createVariable('latitude', np.float32, ('hru',))
forcing.variables['latitude'].units = 'decimal degree'
forcing.variables['latitude'].long_name = 'Latitude location of HRU, North-South decimal degrees'
forcing.createVariable('longitude', np.float32, ('hru',))
forcing.variables['longitude'].units = 'decimal degree'
forcing.variables['longitude'].long_name = 'Longitude location of HRU, East-West decimal degrees'
forcing.createVariable('data_step', np.int32)
forcing.variables['data_step'].units = 'seconds'
forcing.variables['data_step'].long_name = 'data step length in seconds'
forcing.createVariable('time', np.float64, ('time',))
forcing.variables['time'].units = 'hours since 1979-01-01 00:00:00'
forcing.variables['time'].long_name = 'time of forcing data'
forcing.createVariable('LWRadAtm', np.float32, ('time', 'hru'))
forcing.variables['LWRadAtm'].units = 'W m-2'
forcing.variables['LWRadAtm'].long_name = 'downward longwave radiation at the upper boundary'
forcing.variables['LWRadAtm'].v_type     = 'scalarv'
forcing.createVariable('SWRadAtm', np.float32, ('time', 'hru'))
forcing.variables['SWRadAtm'].units = 'W m-2'
forcing.variables['SWRadAtm'].long_name = 'downward shortwave radiation at the upper boundary'
forcing.variables['SWRadAtm'].v_type     = 'scalarv'
forcing.createVariable('airpres', np.float32, ('time', 'hru'))
forcing.variables['airpres'].units = 'Pa'
forcing.variables['airpres'].long_name = 'air pressure at the measurement height'
forcing.variables['airpres'].v_type     = 'scalarv'
forcing.createVariable('airtemp', np.float32, ('time', 'hru'))
forcing.variables['airtemp'].units = 'K'
forcing.variables['airtemp'].long_name = 'air temperature at the measurement height'
forcing.variables['airtemp'].v_type     = 'scalarv'
forcing.createVariable('pptrate', np.float32, ('time', 'hru'))
forcing.variables['pptrate'].units = 'kg m-2 s-1'
forcing.variables['pptrate'].long_name = 'Precipitation rate'
forcing.variables['pptrate'].v_type     = 'scalarv'
forcing.createVariable('spechum', np.float32, ('time', 'hru'))
forcing.variables['spechum'].units = 'g g-1'
forcing.variables['spechum'].long_name = 'specific humidity at the measurement height'
forcing.variables['spechum'].v_type     = 'scalarv'
forcing.createVariable('windspd', np.float32, ('time', 'hru'))
forcing.variables['windspd'].units = 'm s-1'
forcing.variables['windspd'].long_name = 'wind speed at the measurement height'
forcing.variables['windspd'].v_type     = 'scalarv'

# Fill new data set with diplicate values
forcing.variables['hruId'][:]          = 1001
forcing.variables['latitude'][:]       = latCatchment
forcing.variables['longitude'][:]      = lonCatchment
forcing.variables['data_step'][:]      = 3600
forcing.variables['time'][:]      = np.transpose(time)
forcing.variables['SWRadAtm'][:]  = np.transpose(SWRadAtm)
forcing.variables['LWRadAtm'][:]  = np.transpose(LWRadAtm)
forcing.variables['airpres'][:]   = np.transpose(airpres)
forcing.variables['airtemp'][:]   = np.transpose(airtemp)
forcing.variables['pptrate'][:]   = np.transpose(pptrate)
forcing.variables['spechum'][:]   = np.transpose(spechum)
forcing.variables['windspd'][:]   = np.transpose(windspd)

#Print data, to make sure it works.
print("-----------------------------------------------------------------------\n")
print("NetCDF file preview, the first 24 hours of the NetCDF file shown below:")
N = min(H,24)
print("hruID:     %d" %forcing.variables['hruId'][:])
print("Latitude:  %f" %forcing.variables['latitude'][:])
print("Longitude: %f" %forcing.variables['longitude'][:])
print("Data step: %d" %forcing.variables['data_step'][:])
print("Forcing data time:")
print(forcing.variables['time'][0:N])
print("DLWRF,  Longwave radiation flux downwards (surface) [W/m^2]:")
print(forcing.variables['LWRadAtm'][0:N])
print("DSWRF, Shortwave radiation flux downwards (surface) [W/m^2]:")
print(forcing.variables['SWRadAtm'][0:N])
print("PRES, Surface pressure [Pa]:")
print(forcing.variables['airpres'][0:N])
print("TMP, 2-m above ground Temperature [K]:")
print(forcing.variables['airtemp'][0:N])
print("APCP, Precipitation hourly total [kg/m^2/hr]:")
print(forcing.variables['pptrate'][0:N])
print("SPFH, 2-m above ground Specific humidity [kg/kg]:")
print(forcing.variables['spechum'][0:N])
print("VGRD, 10-m above ground Meridonal wind speed [m/s]:")
print(forcing.variables['windspd'][0:N])
#END ########################################################################
#END ##  WRITE DATA TO THE NETCDF FORCING DATA FILE   #######################
#END ##  WRITE DATA TO THE NETCDF FORCING DATA FILE   #######################




###################################################################################
###############   END PPROGRAM  ############  END PROGRAM  ########################
###############   END PPROGRAM  ############  END PROGRAM  ########################
###################################################################################
###############   END PPROGRAM  ############  END PROGRAM  ########################
###############   END PPROGRAM  ############  END PROGRAM  ########################
###################################################################################
###############   END PPROGRAM  ############  END PROGRAM  ########################
###############   END PPROGRAM  ############  END PROGRAM  ########################
###################################################################################
