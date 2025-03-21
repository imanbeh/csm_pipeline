# betelfunctions
# One nice big python file with all of our functions!
#

import numpy as np
from astropy.io import fits
from matplotlib import pyplot as plt
import cmasher as cmr
from astropy.io import fits
from astropy.visualization import quantity_support
quantity_support()  

from astropy.stats import sigma_clipped_stats
from photutils.detection import DAOStarFinder
from photutils.aperture import aperture_photometry, CircularAperture, CircularAnnulus
from astropy import units as u

r_betelgeuse = 29.50*1e-3*u.arcsec


lowcolor = 'steelblue'
highcolor='crimson'

#defining constants for density model

def sm(dist, ang_size):
    '''
    takes ang size arsec
    distance pc
    returns diam in pc
    '''
    diam = (ang_size*dist)/206265

    return diam

def annulus_stdev(data, radius):
    #cycle through data and radii using title[c]
    stdev = []

    for i in range(198):

        ann = []
        

        r_in = i
        r_out = i+1

        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                if radius[i,j]>r_in and radius[i,j]<r_out:
                    ann.append(data[i,j])

        stdev.append(np.std(ann))

    return stdev

def rp_annulus(data,info):
    '''
    data, pix size in arcsec, position of center star
    '''

    pix_size_arcsec = info['pix_size_arcsec']
    position = info['position']

    cent = (position[1],position[0])

    #### aperture_size = r_betelgeuse.value / pix_size_arcsec.value #put in pixel units
    ### aperture = CircularAperture(cent,aperture_size)
    ### photometry = aperture_photometry(data,aperture)
    # print()
    # print("Photometry: ", photometry)

    aperture_sizes = np.arange(1,200,1)
    # print("aperture_sizes =", aperture_sizes)
    # print("info_std",info["std"])
    error = np.full((data.shape[0],data.shape[1]),info['median'])*u.Jy/u.Jy #JUST CHANGED FROM STDEV
    # print("error =", error)
    annuli=[CircularAnnulus(cent, r_in=aperture_sizes[i], r_out=aperture_sizes[i+1]) for i in range(len(aperture_sizes)-1)]
    # print("annuli =", annuli)
    areas = np.array([circle.area for circle in annuli])#*pix_size_arcsec**2
    # print("areas =", areas)
    # print(apertures)
    
    
    photometry = aperture_photometry(data, annuli,error=error)
    #print(photometry.items())
    phot_list = []
    phot_list_err = []
    
    for k,v in photometry.items():
        # print("k",k)
        # print("v",v)
        if 'aperture_sum' in k and 'err' not in k:
            # print("A ",v)
            phot_list.append(v)
        elif 'aperture_sum_err' in k:
            # print("B",v.value)
            phot_list_err.append(v.value)

    phot_array = np.array(phot_list)
    # print("phot_array",phot_array)
    # print("err",phot_list_err)
    phot_array_err = np.array(phot_list_err)
    #print(phot_list)
    surf_brightness_jy_arc2 = (phot_array.flatten()*u.Jy/u.arcsec**2)/(areas)
    err = phot_array_err.flatten()*u.Jy/u.arcsec**2#/areas
    # surf_brightness_jy_arc2 =( phot_array.flatten()/ (areas)) *u.Jy/u.arcsec**2 #
    # info['error'] = (phot_array_err.flatten()/areas)*u.Jy/u.arcsec**2 #
    #print(err)


    centers_arc = ((aperture_sizes[1:]+aperture_sizes[:-1])/2)*pix_size_arcsec
    centers_pc = sm(168,centers_arc).value*u.pc

    centers = {'pc': centers_pc, 'arc': centers_arc}

    info['areas_arc2'] = areas*pix_size_arcsec**2
    info['areas_pix'] = areas
    info['radial_err'] = np.std(surf_brightness_jy_arc2)
    info['annuli'] = annuli
    info['r_edges'] = aperture_sizes

    return centers,surf_brightness_jy_arc2,err




def radial_read(data,info):
    '''
    reads in file and returns radial profile and returns important data
    enter data in jy/pixel.
    '''

    centers, rp_1d,err = rp_annulus(data,info)

    ### RADIUS DATA IN 2D
    r2d = radius2d(data,info)

    err = annulus_stdev(data,r2d)*u.Jy/u.Jy

    radius_2d_arc = r2d*info['pix_size_arcsec'].value
    radius_2d_pc = sm(168,radius_2d_arc)*u.pc

    # ### GATHERING DATA IN DICTONARY LISTS
    # rp = {'jy/arc2':rp}
    # rp_radius = {'arc':centers['arc'],'pc':centers['pc']}
    # radius_2d= {'arc':radius_2d_arc,'pc':radius_2d_pc}

    radius = {'arc_1d': centers['arc'], 'pc_1d': centers['pc'], 'arc_2d': radius_2d_arc, 'pc_2d': radius_2d_pc, 'pix_2d': r2d}

    return radius, rp_1d,err


def radius2d(data,info):
    ### RADIUS DATA IN 2D
    dimensions = data.shape
    rows,columns = dimensions
    radius_2d = np.array([[0.0]*columns]*rows)
    x = info['position'][0]
    y = info['position'][1]
    for i in range(rows):
        for j in range(columns):
            c = (x-i)**2+(y-j)**2
            radius_2d[i,j] = np.sqrt(c)

    return radius_2d

