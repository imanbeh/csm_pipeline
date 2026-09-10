import numpy as np
from astropy import units as u
import csv
from matplotlib import pyplot as plt
from radial_interpolation import *
from radial import sm

lines = 201
points = 100



def read_in_density_file(filename,pix_size_arcsec,center_x,center_y,vmax_gcm2, vmax_gcm3,csm =False,rnge=0.3,return_grids=False):
    '''
    filename: as csv
    pix_size_arcsec as unit object in arcsec
    csm: boolean. if csm, will need to be cropped for nan vals

    '''
    #read in data
    density_2d_as_list = []
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC) # change contents to floats
        for row in reader: # each row is a list
            density_2d_as_list.append(row)

    density_2d = np.array(density_2d_as_list) #convert to array

    density_2d[np.isnan(density_2d)] = 0 # set nans equal to zero

    if csm == True:
        # get ready to crop out all of the nan vals
        a=440
        b=560
        print(density_2d[a:b,a:b].shape[0])
        #moving center for cropped image
        center_x,center_y = (int(density_2d[a:b,a:b].shape[0]/2-1),int(density_2d[a:b,a:b].shape[0]/2-1))
        density_2d = density_2d[a:b,a:b]

    figure,ax = plt.subplots(nrows = 1, ncols=1, figsize = (5,4))#, subplot_kw={'projection': wcs})
    figure.suptitle("Image Square", fontsize = 18, y=1.01)
    im = ax.pcolormesh(density_2d, cmap='gist_heat',shading="gouraud", vmin = 0, vmax = vmax_gcm2)
    figure.colorbar(im,ax=ax, label=r'Jy arc$^{-2}$')
    ax.plot(center_x,center_y,'x')
    ax.set_xlabel(r'$\Delta$ RA (arc)' , size = 10)
    ax.set_ylabel(r'$\Delta$ Dec (arc)' , size = 10)

    x_grid,y_grid,interp_data = radial_interp(density_2d, center_x,center_y,
                    n_lines = lines, n_pts = points, pix_arc = pix_size_arcsec,plot_bool=True,vmax=vmax_gcm2)

    plot_rays(x_grid,y_grid,interp_data,vmax=vmax_gcm2)


    xaxis = x_grid*pix_size_arcsec.value-(center_x*pix_size_arcsec.value)
    yaxis = y_grid*pix_size_arcsec.value-(center_y*pix_size_arcsec.value)

    radius_2d_arc,radius_2d_pc,data_abel = start_abel(xaxis,yaxis,interp_data,vmax_gcm2,vmax_gcm3,rnge)

    if return_grids==True:
        return xaxis,yaxis,interp_data,radius_2d_arc,radius_2d_pc,data_abel

    return radius_2d_arc,radius_2d_pc,data_abel


def start_abel(xaxis,yaxis,interp_data,vmax_gcm2,vmax_gcm3,rnge):
        '''
        sends interpolated data to IAT function.
        returns IAT data
        '''
        # abel transformation
        radius_2d_arc,radius_2d_pc = radius_2d_arrays(xaxis,yaxis)

        data_abel = []
        row = np.zeros(len(interp_data[0,:]))
        med_dens = 8.7055651*10**-8 #csm median density

        df_ds = [] #df/ds filled list
        for i in range(len(interp_data[:,0])):
            #print('i',i)
            row = np.zeros(len(interp_data[i,:]))

            row,df_ds_temp = do_abel_2(interp_data[i,:],(radius_2d_pc[i,:].to(u.cm)).value,med_dens/10)
            #print(df_ds_temp.shape)

            df_ds.append(df_ds_temp)
            data_abel.append(row)

        data_abel = np.array(data_abel)

        #plot results
        fig, ax = plt.subplots(nrows=1, ncols=2,figsize=(12,5))

        im0 = ax[0].pcolormesh(xaxis, yaxis, interp_data,cmap='gist_heat',shading="gouraud", vmin = 0, vmax = vmax_gcm2)

        ax[0].set_xlim(-rnge,rnge)
        ax[0].set_ylim(-rnge,rnge)
        ax[0].set_xlabel("Radius (arc)")
        ax[0].set_ylabel("Radius (arc)")

        ax[0].set_title("Surface Density Image")
        fig.colorbar(im0,label = "Density in g/cm2")

        ### abel image
        #im1 = ax[1].pcolormesh(xaxis[:,0:-c], yaxis[:,0:-c], csm_abel,cmap='gist_heat',shading="gouraud", vmin = 0, vmax = 2e-19)
        im1 = ax[1].pcolormesh(xaxis, yaxis, data_abel,cmap='gist_heat',shading="gouraud", vmin = 0, vmax = vmax_gcm3)

        ax[1].set_xlim(-rnge,rnge)
        ax[1].set_ylim(-rnge,rnge)
        ax[1].set_xlabel("Radius (arc)")
        ax[1].set_ylabel("Radius (arc)")


        ax[1].set_title("IA Transformed Image")
        fig.colorbar(im1,label = "Density in g/cm3")

        return radius_2d_arc,radius_2d_pc,data_abel
    



    
def radius_2d_arrays(xaxis,yaxis):
    print(xaxis.shape)
    radius_2d_arc = np.array([[0.0]*xaxis.shape[1]]*xaxis.shape[0])
    #fill pc array of radii
    for i in range(xaxis.shape[0]):
            for j in range(xaxis.shape[1]):
                c = (xaxis[i,j])**2+(yaxis[i,j])**2
                radius_2d_arc[i,j] = np.sqrt(c)
    radius_2d_pc = sm(168,radius_2d_arc)*u.pc

    return radius_2d_arc,radius_2d_pc

    
def do_abel_2(F_arr,s,med):
    '''
    F = radial profile of surface density
    s = radii corresponding with radial profile
    med = background median- sets all neg values in F array to bkg median
    '''

    F = F_arr.copy() # copy density array to prevent overwriting
    F[F<0] = 0#med/1000 # turn negative values into background 0 or median
    dF_ds = np.gradient(F,s) 

    f_r = np.zeros(len(s))
    r_arr = np.zeros(len(s))
    
    for i in range(len(s)-1):
        
        r = (s[i]+s[i+1])/2 # set r values (3D radial coords) to s (on sky radius) bin centers
        r_arr[i] = r                    # curtails potential div by zero issues

        
        # integrate from r to highest radial value
        integ = np.trapezoid(dF_ds[i+1:]/ np.sqrt(s[s>r]**2-r**2),s[s>r])
        
        # multiply integral result by -1/pi coefficient
        f_r[i]= (-1/np.pi)* integ # integrate from r to highest radial value


    return f_r, dF_ds

def get_grids():
     return x_grid_glo,y_grid_glo