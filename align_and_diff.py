'''
aligns and differences after reprojection and convolution
adds rows instead of subtracting them
'''

import numpy as np
from matplotlib import pyplot as plt
from astropy import units as u


def a_d(drhr, dlr,info_reproj,info_lr):
    '''

    '''
    col_diff = (info_reproj['position'][1]-info_lr['position'][1])
    row_diff = (info_reproj['position'][0]-info_lr['position'][0])

    # print("running new version")
    # print("row_diff: ",row_diff)
    # print("col_diff: ", col_diff)

    # print("SHAPES")
    # print("dlr shape: ", dlr.shape)
    # print("drhr shape: ", drhr.shape)


    a = [dlr.shape[0]]*np.abs(row_diff)
    b = [0]*np.abs(row_diff)

    if (row_diff>0): # center is later in conv. lr needs to be pushed down
        dlr_add = np.insert(dlr, b, np.nan, axis = 0)
        # print("Added ", b, " to dlr to axis 0")
        drhr_add = np.insert(drhr, a, np.nan, axis = 0)
        # print("Added ", a, " to dhr to axis 0")

        # print(1)
    if (row_diff<0): # center is later in lr. conv needs to be pushed down
        dlr_add = np.insert(dlr, a, np.nan,axis=0)
        drhr_add = np.insert(drhr, b, np.nan,axis=0)
        # print(2)

    if (row_diff==0):
        dlr_add = dlr
        drhr_add = drhr

    # print("MAXIMA:")
    # print("dlr center: ", np.where(dlr==np.nanmax(dlr)))
    # print("drhr center: ", np.where(drhr==np.nanmax(drhr)))
    # print("dlr_add center: ", np.where(dlr_add==np.nanmax(dlr_add)))
    # print("drhr_add center: ", np.where(drhr_add==np.nanmax(drhr_add)))

    c = [dlr.shape[1]]*np.abs(col_diff)
    d = [0]*np.abs(col_diff)

    if (col_diff>0): # center is later in conv. lr needs to be shifted right
        dlr_add = np.insert(dlr_add, d, np.nan, axis = 1)
        drhr_add = np.insert(drhr_add, c, np.nan, axis=1)
        # print("added ", d, " to dlr to axis 1")
        # print("added ", c, " to dhr to axis 1")
        # print(3)

    if (col_diff<0):
        dlr_add = np.insert(dlr_add, c, np.nan, axis = 1)
        drhr_add = np.insert(drhr_add, d, np.nan, axis = 1)
        # print(4)

    # PRINT THESE IF YOU WANT TO CHECK THAT THEY ARE ALIGNED
    # print("MAXIMA:")
    # print("dlr center: ", np.where(dlr==np.nanmax(dlr)))
    # print("drhr center: ", np.where(drhr==np.nanmax(drhr)))
    # print("dlr_add center: ", np.where(dlr_add==np.nanmax(dlr_add)))
    # print("drhr_add center: ", np.where(drhr_add==np.nanmax(drhr_add)))

    # print()
    # print("SHAPES")
    # print("dlr shape: ", dlr.shape)
    # print("drhr shape: ", drhr.shape)
    # print("dlr_add shape: ", dlr_add.shape)
    # print("drhr_add shape: ", drhr_add.shape)

    pos1 = np.where(drhr_add==np.nanmax(drhr_add))
    pos=(int(pos1[0]),int(pos1[1]))

    # convert new datasets to diff units
    csm_jy_pixel = dlr_add-drhr_add
    csm_jy_arc = csm_jy_pixel/info_lr['beam_solid_angle'].to(u.arcsec**2).value

    data_lr_centered_add_jy_arc2 = dlr_add/info_lr['beam_solid_angle'].to(u.arcsec**2).value
    reproj_hr_pixel_centered_add_jy_arc2 = drhr_add/info_lr['beam_solid_angle'].to(u.arcsec**2).value


    data_csm = {'jy_pix': csm_jy_pixel, 'jy_arc2': csm_jy_arc, 'position': pos,
                'pix_size_arcsec': info_lr['pix_size_arcsec']}

    data_lr_add = {'jy_pix': dlr_add, 'jy_arc2': data_lr_centered_add_jy_arc2}
    
    info_lr_add = {'position': pos, 'pix_size_arcsec': info_lr['pix_size_arcsec']}
    
    data_reproj_add = {'jy_pix': drhr_add, 'jy_arc2': reproj_hr_pixel_centered_add_jy_arc2}

    info_reproj_add = {'position': pos, 'pix_size_arcsec': info_lr['pix_size_arcsec']}

    info_csm = {'position': pos,'pix_size_arcsec': info_lr['pix_size_arcsec']}

    print("Alignment and subtraction complete. Info dictionaries imported.")

    return data_csm, data_lr_add, data_reproj_add, info_csm, info_lr_add, info_reproj_add

