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

import pandas as pd


csm_dense_bkg = 8.705564515074679e-05 # g / cm2

# open density file and gather radius data
n_l = 51
n_p = 200
n_z = 50

x_grid_csm,y_grid_csm,interp_csm,radius_2d_arc_csm,radius_2d_pc_csm,csm_abel = read_in_density_file("saved_data/csm_2d_density.csv",center_x=499,center_y=499,vmax_gcm2=0.0002, vmax_gcm3=2e-19,
                                                                   nlines=n_l,npoints=n_p,pix_size_arcsec = 0.005 * u.arcsec,return_grids=True,csm=True,bkg = csm_dense_bkg,plots=False)

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

#import pandas as pd
r_list = np.zeros(n_l*n_p*n_z+1)#[]
phi_list = np.zeros(n_l*n_p*n_z+1)#[]
theta_list = np.zeros(n_l*n_p*n_z+1)#[]
rho_list = np.zeros(n_l*n_p*n_z+1)#[]

count = 0
a=0
b=0

for i in range(radius_2d_pc_csm.shape[0]):
    #print('i: ',i)
    for j in range(radius_2d_pc_csm.shape[1]):
        #print('j: ',j)
        #if csm_abel_zero[i,j]!=0:
        if phi[i,j]>=(42.3*np.pi/180) and phi[i,j]<(222.3*np.pi/180): # range of phis on one side of equator
            theta_side = np.linspace(0,np.pi,n_z) # one half of theta range
            a+=1
        elif phi[i,j]>=(222.3*np.pi/180) or phi[i,j]<(42.3*np.pi/180): # range of phis on other side of equator
            #theta_side = np.linspace(np.pi,2*np.pi,n_z) # other half of theta range
            theta_side = np.linspace(0,np.pi,n_z)
            b+=1
        for th in theta_side: # make a duplicate point for each r along this side of line of sight
            print('count: ', count)
            count+=1
            r_list[count] = radius_2d_pc_csm[i,j].value# r_list.append(radius_2d_pc_csm[i,j])
            phi_list[count] = phi[i,j]# phi_list.append(phi[i,j])
            rho_list[count] = csm_abel_zero[i,j]# rho_list.append(csm_abel_zero[i,j])
            theta_list[count] = th# theta_list.append(th)

print('TOTAL LENGTH: ',count)
print('a count: ', a)
print('b count: ', b)

print('did it!')

print('TOTAL LENGTH: ',count)

print('did it!')

coords_spherical = pd.DataFrame({'r': r_list, 'phi': phi_list, 'theta': theta_list})

#convert to cartesian
x = coords_spherical['r'] * np.sin(coords_spherical['theta']) * np.cos(coords_spherical['phi'])
y = coords_spherical['r'] * np.sin(coords_spherical['theta']) * np.sin(coords_spherical['phi'])
z = coords_spherical['r'] * np.cos(coords_spherical['theta'])

coords_cartesian = pd.DataFrame({'x': x,'y': y, 'z': z, 'rho': rho_list*10**24})

coords_cartesian.to_csv("saved_data/betelgeuse_csm_rho_and_coords_small.csv", index=False)