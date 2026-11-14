# Ray Calculation
import numpy as np
from astropy import units as u
import csv
from matplotlib.pyplot import cm

from matplotlib import pyplot as plt
from radial_interpolation import *
from radial import sm
from interp_and_iat_2d import *

import matplotlib as mpl

csm_dense_bkg = 8.705564515074679e-05 # g / cm2
#%matplotlib inline
x_grid_csm,y_grid_csm,interp_csm,radius_2d_arc_csm,radius_2d_pc_csm,csm_abel = read_in_density_file("saved_data/csm_2d_density.csv",center_x=499,center_y=499,vmax_gcm2=0.0002, vmax_gcm3=2e-19,
                                                                   nlines=1401,npoints=500,pix_size_arcsec = 0.005 * u.arcsec,return_grids=True,csm=True,bkg = csm_dense_bkg)
plt.rcParams["axes.formatter.limits"] = (-99, 99)

csm_abel_zero = np.zeros_like(csm_abel)
for i in range(radius_2d_arc_csm.shape[0]):
    for j in range(radius_2d_arc_csm.shape[1]):
        if radius_2d_arc_csm[i,j]>0.1:
            csm_abel_zero[i,j]=csm_abel[i,j]
        else:
            csm_abel_zero[i,j] = 1e-99
csm_abel_zero[csm_abel_zero<=0] = 1e-99
#figure out how to get it in the right range

a=3
params = {
    'image.origin': 'lower',
    'image.interpolation': 'nearest',
    'image.cmap': 'gray',
    'axes.grid': False,
    'savefig.dpi': 150,  # to adjust notebook inline plot size
    'axes.labelsize': 10*a, # fontsize for x and y labels (was 10)
    'axes.titlesize': 14*a,
    'font.size': 12*a, # was 10
    'legend.fontsize': 10*a, # was 10
    'xtick.labelsize': 14*a,
    'ytick.labelsize': 14*a,
    'figure.figsize': [3.39, 2.10],
    'font.family': 'serif',
    'axes.linewidth': 4,
}

plt.rcParams.update(params)

from matplotlib import pyplot as plt
from radial_interpolation import *
from radial import sm
from interp_and_iat_2d import *

color = cm.cool(np.linspace(0, 1, 1401))
def plot_one_ray(radius, data, line_a, line_b,save=False,csm=False,rnge=0.4, 
                     label_r = False, label_l = False, label_b = False, label_t = False,hs=0):    
    

    num_plots = 1
    fig, ax = plt.subplots(num_plots, 1, figsize=(5*4, num_plots*(4/3)*4), sharex=True)
   # ax = axes.ravel()
    
    fig.suptitle("Density Along Each Ray", y= 1.02)
    #fig.tight_layout()
    fig.subplots_adjust(hspace=hs)

    x_range = np.linspace(1*10**-1,1.1)*u.arcsec
    x_range_pc = sm(168,x_range).value*u.pc

    count=0

    if csm==True:
        breaker =70
        n_lines = 1401
    
    else:
        breaker=10
        n_lines = 201

    #print(breaker)
    i = line_a
    
    #for i in range(radius.shape[0]):
    #plt.plot(radius_2d_arc[i,], csm_abel[i,])
    ax.fill_between(radius[i,],data[i,]+data[i,]*430,data[i,]+data[i,]*800,color = color[i],alpha=1,label = f"psi = {2*np.round(i/n_lines,2):{3}.{3}}{"\u03C0"}")
    ax.legend(loc='lower left')
    ax.set_ylim(10**-20,10**-15)
    ax.set_xlim(0.1,rnge)
    ax.tick_params(axis='both',which='both',direction='in', 
                                labelright = label_r, labelleft = label_l,labeltop = label_t, labelbottom = label_b)
    
    ax.yaxis.set_ticks_position('both')
    ax.xaxis.set_ticks_position('both')
    ax.tick_params(which='major', length=10*2, width = 3)
    ax.tick_params(which='minor', length=10*2, width = 3)#, color='r')  


    psi_a = 2*np.round(i/n_lines,4)
    
    for mdot in mdotexp:
        rho_mdot = 10**mdot*u.M_sun/u.yr / (4*np.pi*x_range_pc.to(u.cm)**2*v_yr)
        xtext = x_range[10]
        ytext = rho_mdot[35].to(u.g/u.cm**3)+rho_mdot[1].to(u.g/u.cm**3)/7
        ax.plot(x_range, rho_mdot.to(u.g/u.cm**3).value, ls  = (0,(12,2)),alpha = 0.6, c='darkgrey', linewidth=4)

        #if line_index%6==0:
        if(label_r==True):
            ax.yaxis.set_label_position("right")
        plt.rcParams['font.family'] = 'serif'
        #print("i%6==0. i = ",line_index)
        ax.text(xtext,ytext, f'$10^{{{mdot}}}$'+r' $M_\odot yr^{-1}$', fontsize=32, #was 7
            rotation=-2, alpha = 0.6, font = 'serif')
        ax.set_ylabel(r'Density [g cm$^{-3}$]')#, loc = 'right')
        #ax.ticklabel_format(style='plain', useOffset=False, axis='x')
        

        ax.semilogy()
        ax.semilogx()
        yticks = np.array([10**(-15), 10**(-16), 10**(-17), 10**(-18), 10**(-19)])
        ax.set_yticks(yticks)

        prev_i=i
        count+=1
        ax.set_xlabel("Radius [arcsec]")
        ax.xaxis.set_minor_formatter(matplotlib.ticker.ScalarFormatter())
        ax.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
        #ax.yaxis.set_minor_formatter(matplotlib.ticker.ScalarFormatter())
        #ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())


    ax.ticklabel_format(axis = 'x',style ='plain', scilimits=(-5, 8))

    if save==True:
            filename = f"thesis/single_rays/lines/csm_abel_single_ray_{'{:.3f}'.format(psi_a)}pi.png"
            plt.savefig(filename,bbox_inches='tight')
a=3
params = {
    'image.origin': 'lower',
    'image.interpolation': 'nearest',
    'image.cmap': 'gray',
    'axes.grid': False,
    'savefig.dpi': 150,  # to adjust notebook inline plot size
    'axes.labelsize': 12*a, # fontsize for x and y labels (was 10)
    'axes.titlesize': 14*a,
    'font.size': 12*a, # was 10
    'legend.fontsize': 10*a, # was 10
    'xtick.labelsize': 14*a,
    'ytick.labelsize': 14*a,
    'figure.figsize': [3.39, 2.10],
    'font.family': 'serif',
    'axes.linewidth': 4,
}

plt.rcParams.update(params)
# 2pi is at i= 1400. can go from i=0 to i= 1399
plot_one_ray(radius_2d_arc_csm,csm_abel_zero, line_a=1399,line_b=0,save=False,csm=True,rnge=0.4,
                 label_l=True,label_b=True, hs =0.35)
def plot_single_ray_image(x_grid,y_grid,interp_star,vmax=v_max,shift=True, line_a=0, line_b=19, title = None,save=False,no_rays=False,csm=True,rnge = 0.3):
    '''
    data validation step to show polar alignment
    '''
    # making temp dataset to add rays of a different value
    # this will plot as radial lines
    a=3
    interp_box_temp = np.zeros((len(interp_star),len(interp_star[0])))
    plt.figure(figsize=(6*a,5*a))
    # making rays for reference
    count = line_a
    prev_i=0

    #print("line_b: ",line_b)

    if csm==True:
        breaker =70
        n_lines = 1401
        
    else:
        breaker=10
        n_lines = 201

    ## get start and end psis
    psi_a = 2*np.round(count/1401,4)
    print("i: ", i)
    print("psi_a: ",psi_a)
    
    #thickening lines
    if count == 1400 or count == 0:
        c_plus_one = 1
        c_plus_two = 2
        c_plus_three = 3

        c_minus_one = 1399
        c_minus_two = 1398
        c_minus_three = 1397
    else:
        c_plus_one = count+1
        c_minus_one = count-1
        c_plus_two = count+2
        c_minus_two = count-2
        c_plus_three = count+3
        c_minus_three = count-3



    plt.plot(x_grid[count,],y_grid[count,],color = color[count])
    plt.plot(x_grid[c_plus_one,],y_grid[c_plus_one,],color = color[count])
    plt.plot(x_grid[c_minus_one,],y_grid[c_minus_one,],color = color[count])
    plt.plot(x_grid[c_plus_two,],y_grid[c_plus_two,],color = color[count])
    plt.plot(x_grid[c_minus_two,],y_grid[c_minus_two,],color = color[count])
    plt.plot(x_grid[c_plus_three,],y_grid[c_plus_two,],color = color[count])
    plt.plot(x_grid[c_minus_three,],y_grid[c_minus_two,],color = color[count])

    

    
    # elif count==line_b:
    #     psi_b = 2*np.round(i/n_lines,2)
    #     print("psi_b: ",psi_b)

    # elif i==line_b and csm==True:
    #     psi_b = 2*np.round(i/n_lines,2)
    #     print("psi_b: ",psi_b)


    plt.tick_params(axis='both',which='both')
    plt.tick_params(which='minor', length=10*2, width = 3)
    plt.tick_params(which='major', length=10*2, width = 3)
    plt.pcolormesh(x_grid,y_grid,interp_star,cmap='gist_heat',shading="gouraud",#, vmin = 3e-21, vmax = vmax)
                norm=colors.LogNorm(vmin=3e-20, vmax=interp_star.max()))

    

    plt.xlim(-rnge,rnge)
    plt.ylim(-rnge,rnge)
    plt.ylabel(r'$\Delta$ RA [arcsec]' , size = 14*a)
    plt.xlabel(r'$\Delta$ Dec [arcsec]' , size = 14*a)

    # plt.vlines(0,-10,10,colors='blue') 
    # plt.hlines(0,-10,10,colors='blue')
    if title is None:
        plt.title(f"Betelgeuse CSM density with rays from {psi_a}{"\u03C0"} to {psi_b}{"\u03C0"}",y=1.05)
    else:
        plt.title(title)
        
    plt.colorbar(extend = 'min', label = r'Density in [g cm$^{-3}]$')

    if save==True:
        filename = f"thesis/single_rays/imgs/csm_abel_image_rays_{'{:.3f}'.format(psi_a)}pi.png"
        plt.savefig(filename,bbox_inches='tight')

plot_single_ray_image(x_grid_csm,y_grid_csm, csm_abel_zero, vmax=2e-10,shift=True,line_a=800,title="Betelgeuse CSM Density Distribution",save=False,rnge=0.25)
# running it all to be saved

selected_indices = np.arange(0,1401,20)

for i in selected_indices:   
    plot_one_ray(radius_2d_arc_csm,csm_abel_zero, line_a=i,line_b=0,save=True,csm=True,rnge=0.4,
                 label_l=True,label_b=True, hs =0.35)
    plot_single_ray_image(x_grid_csm,y_grid_csm, csm_abel_zero, vmax=2e-10,shift=True,line_a=i,title="Betelgeuse CSM Density Distribution",save=True,rnge=0.25)
