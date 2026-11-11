# getting 3d set of coordinates
# switched to py file because too large of a dataset

import numpy as np
from astropy import units as u
import csv
from matplotlib.pyplot import cm

from matplotlib import pyplot as plt
from radial_interpolation import *
from radial import sm
from interp_and_iat_2d import *


csm_dense_bkg = 8.705564515074679e-05 # g / cm2
x_grid_csm,y_grid_csm,interp_csm,radius_2d_arc_csm,radius_2d_pc_csm,csm_abel = read_in_density_file("saved_data/csm_2d_density.csv",center_x=499,center_y=499,vmax_gcm2=0.0002, vmax_gcm3=2e-19,
                                                                   nlines=1401,npoints=500,pix_size_arcsec = 0.005 * u.arcsec,return_grids=True,csm=True,bkg = csm_dense_bkg)

# zero out negatives remaining
csm_abel_zero = np.zeros_like(csm_abel)
for i in range(radius_2d_arc_csm.shape[0]):
    for j in range(radius_2d_arc_csm.shape[1]):
        if radius_2d_arc_csm[i,j]>0.1:
            csm_abel_zero[i,j]=csm_abel[i,j]
        else:
            csm_abel_zero[i,j] = 1e-99
csm_abel_zero[csm_abel_zero<=0] = 1e-99

#In spherical coordinates
phi = np.zeros_like(radius_2d_pc_csm.value)

for i in range(phi.shape[0]):
    for j in range(phi.shape[1]):
        phi[i,j] = (i/phi.shape[1]) *2
x_grid_csm_pc = sm(168,x_grid_csm)
y_grid_csm_pc = sm(168,y_grid_csm)
import pandas as pd
r_list = []
phi_list = []
theta_list = []
rho_list = []

for i in range(radius_2d_pc_csm.shape[0]):
    for j in range(radius_2d_pc_csm.shape[1]):

        if phi[i,j]>=(42.3*np.pi/180) and phi[i,j]<(222.3*np.pi/180): # range of phis on one side of equator
            theta_side = np.linspace(0,np.pi,200) # one half of theta range
        elif phi[i,j]>=(222.3*np.pi/180) or phi[i,j]<(42.3*np.pi/180): # range of phis on other side of equator
            theta_side = np.linspace(np.pi,2*np.pi,200) # other half of theta range

        for th in theta_side: # make a duplicate point for each r along this side of line of sight
            r_list.append(radius_2d_pc_csm[i,j])
            phi_list.append(phi[i,j])
            rho_list.append(csm_abel_zero[i,j])
            theta_list.append(th)

        

coords = pd.DataFrame({'r': r_list, 'phi': phi_list, 'theta': theta_list, 'rho': rho_list})
#convert to cartesian
coords['x'] = coords['r'] * np.sin(coords['theta']) * np.cos(coords['psi'])
coords['y'] = coords['r'] * np.sin(coords['theta']) * np.sin(coords['psi'])

coords['z'] = coords['r'] * np.cos(coords['theta'])
coords.to_csv("saved_data/betelgeuse_csm_rho_and_coords.csv", index=False)