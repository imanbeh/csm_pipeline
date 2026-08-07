'''
Procedure for radial interpolation of a 2d dataset

'''

import numpy as np
from matplotlib import pyplot as plt
from astropy import units as u
from scipy.interpolate import RectBivariateSpline

print("hello")

def radial_interp(image, cx,cy, n_lines, n_pts, plot=True):
    '''
    runs radial interpolation sequence
    plots resulting comparison

    returns:
    Plots comparison of original image and interpolated image
    x_vals: x value grid where each row corresponds to the x values along a given ray
    y_vals: y value grid where ... y values along a given ray
    interp_star: grad where rows correspond to interpolated values along a given ray
    '''
    x_vals,y_vals,interp_star = ray_calculation(image, cx,cy, n_lines, n_pts, plot=True)
    return x_vals,y_vals,interp_star

def make_spline(x,y,image):
    '''
    makes RectBivariateSpline for your 2d dataset 
    returns spline
    '''
    spline = RectBivariateSpline(x,y,image) # making function to interpolate starry array

    return spline

def ray_calculation(image, cx,cy, n_lines, n_pts, plot=True):
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

    # get x and y grid
    x = np.linspace(0,image[0,:].shape[0]-1,image[0,:].shape[0])
    y = np.linspace(0,image[:,0].shape[0]-1,image[:,0].shape[0])
    X,Y = np.meshgrid(x,y)

    spline = make_spline(x,y,image) #makes interpolation spline on data

    x_vals = np.zeros((n_lines, n_pts))
    y_vals = np.zeros((n_lines, n_pts))
    rys_xy = np.full((n_lines,n_pts),tuple) # make emmpty tuple array for cartesian coords corresponding to interpolated star

    #pick coordinates for interpolation
    for i, psi in enumerate(psis):

        # polar to cartesian
        x_r = cx + rs * np.cos(psi) #add cx and cy to x and y values to shift origin to image center instead of (0,0)
        y_r = cy + rs * np.sin(psi)

        x_vals[i] = x_r
        y_vals[i] = y_r

        # xy coordinates for each ray index 
        for j in range(n_pts):
            rys_xy[i,j]=(x_r[j],y_r[j])

    # now interpolate!
    interp_star = spline(x_vals,y_vals, grid=False)
        
    if plot==True:
        plot_interp_grid(X,Y,image,x_vals,y_vals,interp_star)

    return x_vals,y_vals,interp_star

def plot_interp_grid(X,Y,image,x_vals,y_vals,interp_star):

    fig, ax = plt.subplots(nrows=1, ncols=2,figsize=(8,4))
    ax[0].pcolormesh(X, Y, image.value)
    ax[0].set_title("Original Image")
    ax[1].pcolormesh(x_vals, y_vals, interp_star)
    ax[1].set_title("Interpolated Image")

    plt.show()


def plot_rays(x_grid,y_grid,interp_star):
    '''
    data validation step to show polar alignment
    '''
    # making temp dataset to add rays of a different value
    # this will plot as radial lines
    interp_box_temp = np.zeros((len(interp_star),len(interp_star[0])))

    # making rays for reference
    for i in range(len(interp_star)):
        for j in range(len(interp_star[0])):
            #print(i)
            if i%10==0:
                interp_box_temp[i,j] = 100
                #print(i,j)
            else:
                interp_box_temp[i,j] = interp_star[i,j]

    plt.figure(figsize=(6,5))
    plt.pcolormesh(x_grid,y_grid,interp_box_temp)

    plt.vlines(49,0,100,colors='red')
    plt.hlines(49,0,100,colors='red')

    plt.title("Plotting Interpolated Rays")
    plt.colorbar()
