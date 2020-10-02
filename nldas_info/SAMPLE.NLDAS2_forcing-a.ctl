DSET        ^%y4/%j3/NLDAS_FORA0125_H.A%y4%m2%d2.%h200.002.grb
INDEX       ^NLDAS2_forcing-a.idx
TITLE        NLDAS-2 forcing a files
OPTIONS      template
UNDEF        9.999E+20
DTYPE   grib 110
XDEF         464 LINEAR    -124.9375    0.125
YDEF         224 LINEAR      25.0625    0.125
ZDEF           1 LINEAR          1.0      1.0
TDEF        NNNN LINEAR HHZDDMMMYYYY      1hr
VARS          11
APCPsfc        0  61,  1,    0 ** Precipitation hourly total [kg/m^2]
CAPE180_0mb    0 157,116,46080 ** 180-0 mb above ground Convective Available Potential Energy [J/kg]
CONVfracsfc    0 153,  1,    0 ** Fraction of total precipitation that is convective [unitless]
DLWRFsfc       0 205,  1,    0 ** Longwave radiation flux downwards (surface) [W/m^2]
DSWRFsfc       0 204,  1,    0 ** Shortwave radiation flux downwards (surface) [W/m^2]
PEVAPsfc       0 228,  1,    0 ** Potential evaporation [kg/m^2]
PRESsfc        0   1,  1,    0 ** Surface pressure [Pa]
SPFH2m         0  51,105,    2 ** 2-m above ground Specific humidity [kg/kg]
TMP2m          0  11,105,    2 ** 2-m above ground Temperature [K]
UGRD10m        0  33,105,   10 ** 10-m above ground Zonal wind speed [m/s]
VGRD10m        0  34,105,   10 ** 10-m above ground Meridional wind speed [m/s]
ENDVARS
