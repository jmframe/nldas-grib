#!/home/jmframe/programs/anaconda3/python2

import datetime as dt
import numpy as np
import netCDF4 as nc # http://unidata.github.io/netcdf4-python/
import pygrib as pg
import time

def name_xy(ixy, lats, lons):
    return "{}, {}".format(lats[ixy], lons[ixy])

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
        if i == (len(lats)-1):
            print("ERROR: CAN NOT FIND THE INDEXIES FOR LATITUDE AND LONGITUDE!!!!!!!!")
            return [-99, -99]
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

def changeDirectory(t, grib_dir):
    year = dt.datetime.date(t).year
    day = dt.datetime.date(t).timetuple().tm_yday
    directory = grib_dir + str(year)  + "/" + str("{:03d}".format(day))  + "/"
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
    return t_unit, year, month, day, hour

def dateFromGRIB(fileName):
    file_in = pg.open(fileName)
    gribData = file_in.select()[0]
    year = int(gribData.year)
    month = int(gribData.month)
    day = int(gribData.day)
    hour = int(gribData.hour)
    return year, month, day, hour

def getValuesFromDateTime(t):
    y = dt.datetime.date(t).year
    m = dt.datetime.date(t).month
    d = dt.datetime.date(t).day
    h = dt.datetime.time(t).hour
    return y, m, d, h

def fillForcing(forcing, H, lat, lon, timestp, time_series, year, \
                SWRadAtm, LWRadAtm, airpres, airtemp, pptrate, spechum, windspd):
    forcing.createDimension('hru', 1)
    forcing.createDimension('time', H)
    ### createVareables in new data set
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
    forcing.variables['time'].units = 'hours since '+str(year)+'-01-01 00:00:00'
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
    forcing.variables['latitude'][:]       = lat
    forcing.variables['longitude'][:]      = lon
    forcing.variables['data_step'][:]      = timestp
    forcing.variables['time'][:]      = np.transpose(time_series)
    forcing.variables['SWRadAtm'][:]  = np.transpose(SWRadAtm)
    forcing.variables['LWRadAtm'][:]  = np.transpose(LWRadAtm)
    forcing.variables['airpres'][:]   = np.transpose(airpres)
    forcing.variables['airtemp'][:]   = np.transpose(airtemp)
    forcing.variables['pptrate'][:]   = np.transpose(pptrate)
    forcing.variables['spechum'][:]   = np.transpose(spechum)
    forcing.variables['windspd'][:]   = np.transpose(windspd)

    return forcing

def setForcingLists(H):
    # Set the vectors (Python List) with these hours for the forcing data
    # Air pressure at the measurement height
    airpres = [np.nan for x in range(H)] #[Pa]
    # Air temperature at the measurement height
    airtemp = [np.nan for x in range(H)]#[K]
    # Downward longwave radiation at the upper boundary
    LWRadAtm = [np.nan for x in range(H)] #[W m-2] 
    # Precipitation rate
    pptrate = [np.nan for x in range(H)] #[kg m-2 s-1]
    # Specific humifity at the measurement height
    spechum = [np.nan for x in range(H)] #[g g-1]
    # Downward shortwave radiation at the upper boundary
    SWRadAtm = [np.nan for x in range(H)] #[W m-2]
    # Observation time
    time_series = [np.nan for x in range(H)] #[days since 1979-01-01 00:00:00]
    #wind speed at the measurement height
    windspd = [np.nan for x in range(H)] #[m s-1]
    F = {'airpres':airpres, 'airtemp':airtemp, 'pptrate':pptrate, 
         'spechum':spechum, 'windspd':windspd,
         'SWRadAtm':SWRadAtm, 'LWRadAtm':LWRadAtm}
    return F

def extractGrib(g, xy_list, nrows, ncols, verbose=False):
    # 1:11:11 TMP, 2-m above ground Temperature [K]
    airtemp = np.array(g[1].values.reshape(nrows*ncols)[xy_list])

    # 2:51:51 SPFH, 2-m above ground Specific humidity [kg/kg]
    spechum = np.array(g[2].values.reshape(nrows*ncols)[xy_list])
    # 3:1:1 PRES, Surface pressure [Pa]
    airpres = np.array(g[3].values.reshape(nrows*ncols)[xy_list])
    # 4:33:33 UGRD, 10-m above ground Zonal wind speed [m/s]
    forcingUGRD = np.array(g[4].values.reshape(nrows*ncols)[xy_list])
    # 5:34:34 VGRD, 10-m above ground Meridonal wind speed [m/s]
    windspd = np.array(g[5].values.reshape(nrows*ncols)[xy_list])
    # 6:205:205 DLWRF,  Longwave radiation flux downwards [W/m^2]
    LWRadAtm = np.array(g[6].values.reshape(nrows*ncols)[xy_list])
    # 7:153:153 CONVfrac, Frac of total precip convective
    forcingCONVfrac = np.array(g[7].values.reshape(nrows*ncols)[xy_list])
    # 8:157:157 CAPE, 180-mb above ground Convective Available Potential Energy
    forcingCAPE = np.array(g[8].values.reshape(nrows*ncols)[xy_list])
        
    # PEVAP, Potential evaporation hourly total   MAYBE: Adiabatic tendency of temperature?
    forcingPEVAP = np.array(g[9].values.reshape(nrows*ncols)[xy_list])
        
    # 10:61:61 APCP, Precipitation hourly total [kg/m^2/hr]
    pptrate = np.array(g[10].values.reshape(nrows*ncols)[xy_list]) / 60 / 60
        
    # 11:204:204 DSWRF, Shortwave radiation flux downwards (surface) [W/m^2]
    SWRadAtm = np.array(g[11].values.reshape(nrows*ncols)[xy_list])
                 
    G={'airtemp':airtemp, 'spechum':spechum, 'airpres':airpres, 'forcingUGRD':forcingUGRD, 
       'windspd':windspd, 'LWRadAtm':LWRadAtm, 'forcingCONVfrac':forcingCONVfrac, 
       'forcingCAPE':forcingCAPE,'forcingPEVAP':forcingPEVAP, 'pptrate':pptrate, 'SWRadAtm':SWRadAtm}
           
    if verbose:
        print("TMP, 2-m above ground Temperature [K]: {}".format(airtemp))
        print("SPFH, 2-m above ground Specific humidity [kg/kg]: {}".format(spechum))
        print("PRES, Surface pressure [Pa]: {}".format(airpres))
        print("UGRD, 10-m above ground Zonal wind speed [m/s]: {}".format(forcingUGRD))
        print("VGRD, 10-m above ground Meridonal wind speed [m/s]: {}".format(windspd))
        print("DLWRF,  Longwave radiation flux downwards (surface) [W/m^2]: {}".format(LWRadAtm))
        print("CONVfrac, Fraction of total precipitation that is convective: {}".format(forcingCONVfrac))
        print("CAPE, 180-mb above ground Convective Available Potential Energy: {}".format(forcingCAPE))
        print("PEVAP, Potential evaporation hourly total: {}".format(forcingPEVAP))
        print("APCP, Precipitation hourly total [kg/m^2/hr]: {}".format(pptrate))
        print("DSWRF, Shortwave radiation flux downwards (surface) [W/m^2]: {}".format(SWRadAtm))
            
    return G

