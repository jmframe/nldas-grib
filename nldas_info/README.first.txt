
UPDATE: On 4 Jun 2018, NLDAS-2 forcing "A" files were replaced
for 13Z 19 Feb to 12Z 21 Feb 2018.  The original operational
files incorrectly hadd zero precipitation amounts over CONUS.
The original NLDAS-2 forcing "A" files for this day have been
archived.  The operational LSMs, however, were run with this
zero precipitation, and since 13Z on 19 Feb 2018, are drier
than expected.  We have requested several times with NOAA for
them to correct the NLDAS-2 LSMs as well.

----
This README describes the NLDAS Phase 2 (NLDAS-2) Forcing data
on "Discover".  These files use the "GES DISC" convention.

Land Information System (LIS) users that are using the data in
this directory should have this line in their "lis.config" file:
NLDAS2 data center source:              "GES-DISC"

Cron jobs update the data daily in near real-time, currently with
a ~3.5-day latency.  Data is typically made available on Discover
about 21:30Z every day, although the data is often available from
the GES DISC an hour or two earlier every day, if needed.

I welcome questions, but you may find some answers
already on the website, including on the FAQ:
    http://ldas.gsfc.nasa.gov/nldas/
    http://ldas.gsfc.nasa.gov/faq/

David Mocko   (David.Mocko@nasa.gov)   x4-6222

----
The "README.NLDAS2.pdf" file describes the Forcing data within this
directory.  The data is organized by sub-directory by year and then
by day of year.  All daily directories contain hourly files for both
the Forcing "a" and Forcing "b" files.  Please see the pdf README
file for more information about which variables are instantaneous
and which are backward-averaged/accumulated over the previous hour.

The data is in GRIB-1 format with the following naming convention:
    YYYY/JJJ/NLDAS_FORA0125_H.AYYYYMMDD.HH00.002.grb - for Forcing "a" files
    YYYY/JJJ/NLDAS_FORB0125_H.AYYYYMMDD.HH00.002.grb - for Forcing "b" files
where YYYY = 4-digit year;
      JJJ  = 3-digit day of year;
      MM   = 2-digit month;
      DD   = 2-digit day of month;
      HH   = 2-digit GMT hour.

----
The following GRIB table applies to both the "a" and "b" files:

# NLDAS-2 Forcing
-1:7:12:130
001:PRES:Pressure [Pa]
007:HGT:Geopotential height [gpm]
011:TMP:Temperature [K]
033:UGRD:Zonal wind speed [m/s]
034:VGRD:Meridional wind speed [m/s]
051:SPFH:Specific humidity [kg/kg]
061:APCP:Precipitation hourly total [kg/m^2]
063:ACPCP:Convective precipitation hourly total [kg/m^2]
153:CONVfrac:Fraction of total precipitation that is convective [unitless]
157:CAPE:Convective Available Potential Energy [J/kg]
179:ACOND:Aerodynamic conductance [m/s]
204:DSWRF:Shortwave radiation flux downwards (surface) [W/m^2]
205:DLWRF:Longwave radiation flux downwards (surface) [W/m^2]
228:PEVAP:Potential evaporation [kg/m^2]

----
There are two GrADS control files, with GRIB index files that are
already created, for the entire period of record of the NLDAS-2
forcing (13Z01jan1979 to present [*]):
    NLDAS2_forcing-a.ctl
    NLDAS2_forcing-b.ctl

Users are encouraged to open these control files directly in GrADS.
Just open, and then set the time for your period of interest.

[*] - The index files are updated monthly, about 5-10 days after
the beginning of the month.  If you need to plot more recent data
in GrADS, please follow the directions below. 

----
There are two SAMPLE control files to open the NLDAS-2 Forcing
data in GrADS.  Follow this procedure to create a GrADS gribmap:

1) Copy the appropriate SAMPLE control file to your directory.
      cp SAMPLE.NLDAS2_forcing-a.ctl ~/your_directory/NEWFILENAME.ctl
         or
      cp SAMPLE.NLDAS2_forcing-b.ctl ~/your_directory/NEWFILENAME.ctl

2) Edit the file with a text editor and look for the line that
      begins with "TDEF".

3) Replace NNNN with the number of hourly times you need to plot.
      NNNN can be any value from 1 to the total number of hourly
      files since Jan 1979 (currently over 325,000 hourly files -
      this will take a LONG time in gribmap, so not recommended)!

4) a) Replace HH with the 2-digit starting GMT hour
   b) Replace DD with the 2-digit starting day of month
   c) Replace MMM with the 3-letter abbreviation starting month
   d) Replace YYYY with the 4-digit starting year

   Example: To plot 12 days of hourly data starting at 12Z GMT
            on 23 September 2008, the TDEF line should be:
               TDEF         288 LINEAR 12Z23sep2008      1hr

5) Close and save the file.

6) Run "gribmap -E -i NEWFILENAME.ctl", replacing NEWFILENAME
      with the file name chosen in step #1 above.

7) Fire up GrADS, "open NEWFILENAME.ctl", and begin plotting!

If you need data in other formats (binary, ASCII, netCDF), please
follow the above steps to generate a gribmap, then use the GrADS
commands "set fwrite" or "set gxout print".  Please see the GrADS
online documentation for help with these commands and with GrADS:
    http://www.iges.org/grads/gadoc/gadocindex.html
Or you can use the Mirador and Giovanni services available from
the GES DISC at the link below.

----
NLDAS-2 data is also available via ftp:
    ftp://hydro1.sci.gsfc.nasa.gov/data/s4pa/NLDAS/
and via a GrADS data server:
    http://hydro1.sci.gsfc.nasa.gov/dods/
and via other methods/services from the GES DISC:
    http://disc.sci.gsfc.nasa.gov/hydrology/data-holdings

----
Note that monthly and monthly climatology datasets are also available
from the GES DISC, and on Discover from these paths:
    /discover/nobackup/projects/drought/shared/MONTHLY/NLDAS2.FORCING
    /discover/nobackup/projects/drought/shared/MONTHLY/CLIMATOLOGY

