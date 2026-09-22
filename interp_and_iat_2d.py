import numpy as np
from astropy import units as u
import csv
from matplotlib import pyplot as plt
from radial_interpolation import *
from radial import sm
from matplotlib.pyplot import cm
import matplotlib.colors as colors



default_lines = 201
default_points = 100



def read_in_density_file(filename,pix_size_arcsec,center_x,center_y,vmax_gcm2, vmax_gcm3,
                         nlines = default_lines, npoints = default_points, csm =False,rnge=0.3,return_grids=False):
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

    # if csm == True:
    #     # get ready to crop out all of the nan vals
    #     a=440
    #     b=560
    #     print(density_2d[a:b,a:b].shape[0])
    #     #moving center for cropped image
    #     center_x,center_y = (int(density_2d[a:b,a:b].shape[0]/2-1),int(density_2d[a:b,a:b].shape[0]/2-1))
    #     density_2d = density_2d[a:b,a:b]

    figure,ax = plt.subplots(nrows = 1, ncols=1, figsize = (5,4))#, subplot_kw={'projection': wcs})
    figure.suptitle("Image Square", fontsize = 18, y=1.01)
    im = ax.pcolormesh(density_2d, cmap='gist_heat',shading="gouraud", vmin = 0, vmax = vmax_gcm2)
    figure.colorbar(im,ax=ax, label=r'Jy arc$^{-2}$')
    ax.plot(center_x,center_y,'x')
    ax.set_xlabel(r'$\Delta$ RA (arc)' , size = 10)
    ax.set_ylabel(r'$\Delta$ Dec (arc)' , size = 10)

    x_grid,y_grid,interp_data = radial_interp(density_2d, center_x,center_y,
                    n_lines = nlines, n_pts = npoints, pix_arc = pix_size_arcsec,plot_bool=True,vmax=vmax_gcm2)

    plot_rays_image(x_grid,y_grid,interp_data,vmax=vmax_gcm2,csm=csm) 


    xaxis = x_grid*pix_size_arcsec.value-(center_x*pix_size_arcsec.value)
    yaxis = y_grid*pix_size_arcsec.value-(center_y*pix_size_arcsec.value)

    radius_2d_arc,radius_2d_pc,data_abel = start_abel(xaxis,yaxis,interp_data,vmax_gcm2,vmax_gcm3,rnge)

    if return_grids==True:
        return xaxis,yaxis,interp_data,radius_2d_arc,radius_2d_pc,data_abel

    return radius_2d_arc,radius_2d_pc,data_abel




def start_abel(xaxis,yaxis,interp_data_original,vmax_gcm2,vmax_gcm3,rnge):
        '''
        sends interpolated data to IAT function.
        returns IAT data
        '''
        # abel transformation
        radius_2d_arc,radius_2d_pc = radius_2d_arrays(xaxis,yaxis)

        interp_data = regularization(interp_data_original,radius_2d_arc)

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
    
def regularization(interp_data_original,radius_2d_arc):
    interp_csm = np.zeros_like(interp_data_original)
    i_a=0
    i_b=0
    i_c=0
    csm_dense_bkg = 8.705564515074679e-05
    radius_betel_arc = 0.295

    for i in range(radius_2d_arc.shape[0]):
        for j in range(radius_2d_arc.shape[1]): #set center to bkg value (can't divide by radius = 0)
            if radius_2d_arc[i,j]==0:
                interp_csm[i,j] = csm_dense_bkg*1e-3
                i_a+=1
            elif radius_2d_arc[i,j]<0.1 or interp_data_original[i,j]<=0: # setting up power law background distribution # radius_2d_arc[i,j]<0.1 or 
                interp_csm[i,j] = 1e-3*csm_dense_bkg/((radius_betel_arc/radius_2d_arc[i,j])**2)
                i_b+=1
            else:
                #do nothing if normsl point
                interp_csm[i,j]=interp_data_original[i,j]
                i_c+=1

    print(i_a)
    print(i_b)
    print(i_c)

    return interp_csm


    
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


## making plots for csm
color = cm.cool(np.linspace(0, 1, 23))
mdotexp = [-8,-7,-6,-5]# msun/yr
v_yr = (1e6*u.cm/u.s).to(u.cm/u.yr)

def plot_rays_image(x_grid,y_grid,interp_star,vmax=v_max,shift=True, line_a=0, line_b=19, title = None,save=False,no_rays=False,csm=False):
    '''
    data validation step to show polar alignment
    '''
    # making temp dataset to add rays of a different value
    # this will plot as radial lines
    interp_box_temp = np.zeros((len(interp_star),len(interp_star[0])))
    plt.figure(figsize=(6,5))
    # making rays for reference
    count = 0
    prev_i=0

    print("line_b: ",line_b)

    if csm==True:
        breaker =70
        n_lines = 1401
        
    else:
        breaker=10
        n_lines = 201

    if no_rays==False:
        for i in range(len(interp_star)):
            #for j in range(len(interp_star[0])):
                #print(i)
            if i%breaker==0:
                if (i!=prev_i or i==0) and count>=line_a and count<=line_b:
                    print("i: ",i)
                    print("count: ",count)
                    plt.plot(x_grid[i,],y_grid[i,],color = color[count])

                    ## get start and end psis
                    if count==line_a:
                        psi_a = 2*np.round(i/n_lines,2)
                        print("psi_a: ",psi_a)
                    elif count==line_b:
                        psi_b = 2*np.round(i/n_lines,2)
                        print("psi_b: ",psi_b)

                    elif i==line_b and csm==True:
                        psi_b = 2*np.round(i/n_lines,2)
                        print("psi_b: ",psi_b)

                count+=1
                #print(i,j)
                prev_i=i


    plt.pcolormesh(x_grid,y_grid,interp_star,cmap='gist_heat',shading="gouraud",#, vmin = 3e-21, vmax = vmax)
                norm=colors.LogNorm(vmin=3e-21, vmax=interp_star.max()))

    rnge = 0.3

    plt.xlim(-rnge,rnge)
    plt.ylim(-rnge,rnge)
    plt.xlabel('Radius (arc)')
    plt.ylabel('Radius (arc)')

    # plt.vlines(0,-10,10,colors='blue') 
    # plt.hlines(0,-10,10,colors='blue')
    if title is None:
        plt.title(f"Betelgeuse CSM density with rays from {psi_a}{"\u03C0"} to {psi_b}{"\u03C0"}",y=1.05)
    else:
        plt.title(title)
        
    plt.colorbar(extend = 'min')

    if save==True and title==False:
        filename = f"thesis/csm_abel_plots/csm_abel_image_rays_{psi_a}_{psi_b}pi.png"
        plt.savefig(filename)
    elif save==True and no_rays==True:
        filename = f"thesis/csm_abel_plots/csm_abel_image_no_rays.png"
        plt.savefig(filename)


def plot_single_rays(radius, data, line_a, line_b,save=False,csm=False):    

    num_plots = line_b-line_a+1
    fig, axes = plt.subplots(num_plots, 1, figsize=(5, num_plots*(4/3)), sharex=True)
    ax = axes.ravel()
    fig.suptitle("Inverse Abel Transform for CSM Rays", y= 0.99)
    fig.tight_layout()
    fig.subplots_adjust(hspace=0)

    x_range = np.linspace(1*10**-1,1.1)*u.arcsec
    x_range_pc = sm(168,x_range).value*u.pc

    prev_i=0
    count=0

    if csm==True:
        breaker =70
        n_lines = 1401
    
    else:
        breaker=10
        n_lines = 201

    print(breaker)
   
    for i in range(radius.shape[0]):
        #plt.plot(radius_2d_arc[i,], csm_abel[i,])
        if i%breaker==0:
            if (i!=prev_i or i==0) and count>=line_a and count<=line_b:
                line_index=count-line_a
                ax[line_index].fill_between(radius[i,],data[i,]+data[i,]*430,data[i,]+data[i,]*800,color = color[count],alpha=1,label = f"psi = {2*np.round(i/n_lines,2)}{"\u03C0"}")
                ax[line_index].legend(loc='lower left')
                ax[line_index].set_ylim(10**-20,10**-15)
                ax[line_index].set_xlim(1*10**-1,.4)

                if count==line_a:
                    psi_a = 2*np.round(i/n_lines,2)
                elif count==line_b:
                    psi_b = 2*np.round(i/n_lines,2)

                
                for mdot in mdotexp:
                    rho_mdot = 10**mdot*u.M_sun/u.yr / (4*np.pi*x_range_pc.to(u.cm)**2*v_yr)
                    xtext = x_range[10]
                    ytext = rho_mdot[35].to(u.g/u.cm**3)+rho_mdot[1].to(u.g/u.cm**3)/10
                    ax[line_index].plot(x_range, rho_mdot.to(u.g/u.cm**3).value, ls  = '-.',alpha = 0.6, c='grey')

                    if i == 0:
                        ax[line_index].text(xtext,ytext, f'$10^{{{mdot}}}$'+r' $M_\odot yr^{-1}$', fontsize=9, 
                            rotation=-3, alpha = 0.6)
                        ax[line_index].set_ylabel(r'Density g cm$^{-3}$')

                ax[line_index].semilogy()
                ax[line_index].semilogx()


                prev_i=i
            count+=1
    ax[line_index].set_xlabel("Radius (arcsec)")

    if save==True:
            filename = f"thesis/csm_abel_plots/csm_abel_single_rays_{psi_a}_{psi_b}pi.png"
            plt.savefig(filename)

def plot_sections(x_grid_csm,y_grid_csm,radius_2d_arc_csm,csm_abel,vmax=2e-19,shift=True,line_a=0,line_b=19,save_plots=False,rays_img_title=None,csm=False):
    '''
    produce both the image and single rays plots
    '''
    plot_rays_image(x_grid_csm,y_grid_csm,csm_abel,vmax=vmax,shift=True,line_a=line_a,line_b=line_b,save=save_plots, title=rays_img_title,csm=csm)
    plot_single_rays(radius_2d_arc_csm,csm_abel,line_a,line_b,save=save_plots,csm=csm)
