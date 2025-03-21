from astropy.io import fits
import numpy as np
from astropy import units as u


from astropy.wcs import WCS

from astropy.time import Time
from astropy.coordinates import SkyCoord

# question: is this right? should I just give one the other wcs
print("running")

def pm_correct(hdu1,hdu2):
    '''
    1 happened first, 2 happened second
    
    '''

    header_1 = hdu1[0].header
    header_2 = hdu2[0].header

    wcs_1 = WCS(header_1)
    wcs_2 = WCS(header_2)

    #getting observation dates
    time_1 = Time(header_1['DATE-OBS'])
    time_2 = Time(header_2['DATE-OBS'])
    # setting times epochs were taken as variables

    # setting proper motion of betelgeuse as variables
    pm_ra = 26.42 * u.mas/u.yr
    pm_dec = 9.60 * u.mas/u.yr

    # getting center from header of each image
    crval_1 = [header_1['CRVAL1'],header_1['CRVAL2']]*u.deg
    crval_2 = [header_2['CRVAL1'],header_2['CRVAL2']]*u.deg

    distance = 168*u.parsec

    # print("time1: ", time_1)
    # print("time2: ", time_2)

    print(time_1>time_2)

    if(time_1<time_2):
        c = SkyCoord(ra=crval_1[0],
                dec=crval_1[1],
                distance=distance,
                pm_ra_cosdec=pm_ra,
                pm_dec=pm_dec,
                obstime=Time(header_1['DATE-OBS']))
        # applying proper motion correction
        c.apply_space_motion(time_2) 
        # print(c)
        #updating center in header
        hdu1[0].header['CRVAL1'] = c.ra.value
        hdu1[0].header['CRVAL2'] = c.dec.value

        print("First epoch shifted to second.")
    elif(time_2<time_1):
        c = SkyCoord(ra=crval_2[0],
                dec=crval_2[1],
                distance=distance,
                pm_ra_cosdec=pm_ra,
                pm_dec=pm_dec,
                obstime=Time(header_2['DATE-OBS']))
        c.apply_space_motion(time_1)
        hdu2[0].header['CRVAL1'] = c.ra.value
        hdu2[0].header['CRVAL2'] = c.dec.value
        # print(c)

        print("Second epoch shifted to first.")

    else:
        print("Epochs were captured at the same time.")
        print("No proper motion correction is necessary.")


    return hdu1, hdu2

    

