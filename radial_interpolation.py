'''
Procedure for radial interpolation of a 2d dataset

'''

import numpy as np
from matplotlib import pyplot as plt
from astropy import units as u
from scipy.interpolate import RectBivariateSpline



def make_spline(image):
    '''
    makes RectBivariateSpline for your 2d dataset 
    returns spline
    '''
    # get x and y grid
    x = np.linspace(0,image[0,:].shape[0]-1,image[0,:].shape[0])
    y = np.linspace(0,image[:,0].shape[0]-1,image[:,0].shape[0])

    spline = RectBivariateSpline(y,x,image) # making function to interpolate starry array

    return spline



#X,Y = np.meshgrid(x,y)

def lines(image, cx,cy, n_lines, n_pts, plot=True):
    '''
    returns n_lines rays of n_pts long radial profiles, and corresponding array of cartesian coordinates

    image = 2d array image to be interpolated
    cx = x center
    cy = y center
    n_lines = number of rays
    n_pts = number of points along rays
    plot = booleon T/F to plot resulting interpolated grid

    '''
    psis = np.linspace(0,2*np.pi, n_lines, endpoint=False)
    rs = np.linspace(0,cx+1,n_pts)
    spline = make_spline(image) #makes interpolation spline on data

    rys = np.zeros((n_lines, n_pts)) # make ray array. rows will interate through psis,
                                    # cols iterate through radii

    rys_xy = np.full((n_lines,n_pts),tuple) # make emmpty tuple array for cartesian coords corresponding to interpolated star

    #pick coordinates for interpolation
    for i, psi in enumerate(psis):

        # polar to cartesian
        
        x_r = cx + rs * np.cos(psi) #add cx and cy to x and y values to shift origin to image center instead of (0,0)
        y_r = cy + rs * np.sin(psi)


        #interpolate a line of values
        new_ray = spline(x_r,y_r,grid=False)

        # give ray at psi = i interpolated values
        rys[i,:] = new_ray
        # xy coordinates for each ray index 
        for j in range(n_pts):
            rys_xy[i,j]=(x_r[j],y_r[j])
        
    if plot==True:
        plot_interp_grid(rys,rys_xy)

    return rys,rys_xy

def plot_interp_grid(rys,rys_xy):

    # get x and y vals from coordinate grid
    x_vals = [x[0] for row in rys_xy for x in row] # gets x values
    y_vals = [x[1] for row in rys_xy for x in row] # gets y values

    plt.figure(figsize=(6,5))
    plt.scatter(x_vals,y_vals,c=rys)
    # plt.xlim(0,100)
    # plt.ylim(0,100)
    #plt.gca().invert_yaxis()

    plt.title("Radially Interpolated Star")
    plt.colorbar()