from astropy.io import fits
from astropy import units as u
import numpy as np

from matplotlib import pyplot as plt
import cmasher as cmr

r_betelgeuse = 29.50*1e-3*u.arcsec

def read(hdu):
    '''
    enter hdu
    disects header and converts dataset to different units
    '''

    #hdu = fits.open(filename)
    data_jy_beam = hdu[0].data
    header = hdu[0].header

    beam = (header['BMAJ'] * u.deg, header['BMIN']*u.deg)
    pix_size = np.abs(header['CDELT1'])*u.deg,np.abs(header['CDELT2'])*u.deg
    pix_size_arcsec = pix_size[0].to(u.arcsec)
    beam_solid_angle = np.pi * beam[0] * beam[1] / (4*np.log(2))
    beam_solid_angle_arc2 = beam_solid_angle.to(u.arcsec**2).value
    pix_per_beam = beam_solid_angle / (pix_size[0]*pix_size[1])

    data_jy_pix = data_jy_beam / pix_per_beam
    data_jy_arc2 = (data_jy_pix / beam_solid_angle_arc2)
    #data_jy_arc2 = data_jy_pix * (pix_size_arcsec**2).value
    #data_jy_arc2 = (data_jy_beam / beam_solid_angle_arc2).value




    kspatres = np.sqrt(header['BMAJ']*u.deg.to(u.arcsec)*header['BMIN']*u.deg.to(u.arcsec))



    datas = [data_jy_beam,data_jy_pix,data_jy_arc2]
    
    titles= ['jy beam', 'jy pixel','jy arc2']

    # finding max val for each dataset
    max_pos = np.unravel_index(np.argmax(np.ma.masked_invalid(data_jy_arc2)), data_jy_arc2.shape)

    #print(max_pos)
    position=(max_pos[-2],max_pos[-1])

    data_dict = {"jy_pix": data_jy_pix, "jy_arc2": data_jy_arc2, "jy_beam": data_jy_beam}

    info = {'beam': beam,'beam_solid_angle': beam_solid_angle, 'pix_size': pix_size, 'pix/beam': pix_per_beam,
            'pix_size_arcsec': pix_size_arcsec, 'theta': header['BPA'], 'bmaj': header['BMAJ'], 'bmin':header['BMIN'], 
            'header':header,'position': position, 'kspatres': kspatres, 'cmap': cmr.flamingo}


    print("Header information imported.")

    return data_dict, info

