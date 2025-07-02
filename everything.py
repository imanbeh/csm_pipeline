from conv_reproj import match
from align_and_diff import a_d
from header_setup import read

from matplotlib import pyplot as plt
import numpy as np

from astropy.io import fits
from pm import pm_correct
from astropy import units as u
from astropy.wcs import WCS
import cmasher as cmr

from radial import radial_read
from dens import density_model

from astropy.stats import sigma_clipped_stats

#import abel 


print("Ready to go!")


def full_analysis(hr,lr):
    '''
    enter two datasets here. must be in order hr, lr.
    this function will process from start to finish. pm correction, 
    '''
    hduhr_raw = fits.open(hr)
    hdulr_raw = fits.open(lr)

    hduhr, hdulr = pm_correct(hduhr_raw, hdulr_raw)

    dlr, infolr = read(hdulr)
    dhr, infohr = read(hduhr)   

    data_reproj, info_reproj = match(dhr,dlr, infohr, infolr)

    data_csm, data_lr_add, data_reproj_add, info_csm, info_lr_add, info_reproj_add = a_d(data_reproj['jy_pix_norm'][0,0,...], dlr['jy_pix'][0,0,...], info_reproj,infolr)

    data = {'hr': dhr, 'lr': dlr, 'reproj': data_reproj, 'csm': data_csm,
             'lr_add': data_lr_add, 'reproj_add': data_reproj_add}
    info = {'hr': infohr, 'lr': infolr, 'reproj': info_reproj, 'csm': info_csm, 'lr_add': info_lr_add, 'reproj_add': info_reproj_add}

    title = ['hr', 'lr', 'reproj', 'csm', 'lr_add', 'reproj_add']
    
    data_1d = {}
    radius = {}
    data_dens_1d = {}
    data_dens_2d = {}

    for i in range(len(data)):
        sig = 1
        info[title[i]]['cmap'] = cmr.flamingo


        if i<2:
            # print(title[i])
            # print(np.any(np.isnan(data[title[i]]['jy_arc2'][0,0,...])))


            temp = data[title[i]]['jy_arc2'][0,0,...].copy()
            temp[np.isnan(temp)]=(10*np.std(temp))
            mask = np.abs(temp-np.median(temp))>(3*np.std(temp))
            info[title[i]]['mean'], info[title[i]]['median'], info[title[i]]['std'] = sigma_clipped_stats(data[title[i]]['jy_arc2'][0,0,...], sigma = sig,mask=mask)

            radius[title[i]],data_1d[title[i]],info[title[i]]['error'] = radial_read(data[title[i]]['jy_arc2'][0,0,...],info[title[i]])
            data_dens_2d[title[i]] = density_model(data[title[i]]['jy_arc2'][0,0,...]*u.Jy/u.arcsec**2, radius[title[i]]['pc_2d'])

            ### GATHERING MEDIAN BACKGROUND DATA
            info[title[i]]['mean_dens'], info[title[i]]['median_dens'], info[title[i]]['std_dens'] = sigma_clipped_stats(data_dens_2d[title[i]], sigma = sig,mask = mask)


        elif i==2:
            # print(title[i])
            # print(np.any(np.isnan(data[title[i]]['jy_arc2_norm'])))

            temp = data[title[i]]['jy_arc2_norm'][0,0,...].copy()
            temp[np.isnan(temp)]=(10*np.std(temp))
            mask = np.abs(np.median(temp)-temp)>(3*np.std(temp))
            
            mask[np.isnan(mask)]=True
            #mask = data[title[i]]['jy_arc2_norm'][0,0,...]>(3*np.std(data[title[i]]['jy_arc2_norm'][0,0,...]))
            info[title[i]]['mean'], info[title[i]]['median'], info[title[i]]['std'] = sigma_clipped_stats(data[title[i]]['jy_arc2_norm'][0,0,...], sigma = sig,mask=mask)

            radius[title[i]],data_1d[title[i]],info[title[i]]['error'] = radial_read(data[title[i]]['jy_arc2_norm'][0,0,...],info[title[i]])
            data_dens_2d[title[i]] = density_model(data[title[i]]['jy_arc2_norm'][0,0,...]*u.Jy/u.arcsec**2, radius[title[i]]['pc_2d'])

            ### GATHERING MEDIAN BACKGROUND DATA
            info[title[i]]['mean_dens'], info[title[i]]['median_dens'], info[title[i]]['std_dens'] = sigma_clipped_stats(data_dens_2d[title[i]], sigma = sig,mask=mask)

        else:
            # temp = data[title[i]]['jy_arc2']
            # temp[np.isnan(temp)]=0
            # mask = temp>(3*np.std(temp))
            ##mask = data[title[i]]['jy_arc2']>(3*np.std(data[title[i]]['jy_arc2']))
            # print(title[i])
            # print(np.any(np.isnan(data[title[i]]['jy_arc2'])))
            
            temp = data[title[i]]['jy_arc2'].copy()
            temp[np.isnan(temp)]=(10*np.std(temp))
            mask = np.abs(np.median(temp)-temp)>(3*np.std(temp))
            
            info[title[i]]['mean'], info[title[i]]['median'], info[title[i]]['std'] = sigma_clipped_stats(data[title[i]]['jy_arc2'], sigma = sig,mask=mask)

            radius[title[i]],data_1d[title[i]],info[title[i]]['error'] = radial_read(data[title[i]]['jy_arc2'],info[title[i]])
            data_dens_2d[title[i]] = density_model(data[title[i]]['jy_arc2']*u.Jy/u.arcsec**2, radius[title[i]]['pc_2d'])

            ### GATHERING MEDIAN BACKGROUND DATA
            info[title[i]]['mean_dens'], info[title[i]]['median_dens'], info[title[i]]['std_dens'] = sigma_clipped_stats(data_dens_2d[title[i]], sigma =sig,mask=mask)

        data_dens_1d[title[i]]= density_model(data_1d[title[i]],radius[title[i]]['pc_1d'])

    data_plot = {'hr': dhr['jy_arc2'][0,0,...], 'lr': dlr['jy_arc2'][0,0,...], 'reproj': data_reproj['jy_arc2_norm'][0,0,...], 'csm': data_csm['jy_arc2'], 
                 'hr_dens': data_dens_2d['hr'],'lr_dens': data_dens_2d['lr'], 'reproj_dens': data_dens_2d['reproj'], 'csm_dens': data_dens_2d['csm']}
    

    return data, data_1d, radius, data_dens_1d, data_dens_2d, data_plot, info


def plot_2d(data, info, vminmax, minn=-0.3, suptitle = "Intensity and Density Plots"):

    maxx=-minn #define x and y axis limits
    titles = ['{res}"'.format(res = np.round(info['hr']['kspatres'],3)) + r' Intensity (Jy arc$^{-2}$)',
              '{res}"'.format(res = np.round(info['lr']['kspatres'],3)) + r' Intensity (Jy arc$^{-2}$)',
              '{res}"'.format(res = np.round(info['hr']['kspatres'],3)) + r' After Reprojection Intensity (Jy arc$^{-2}$)',
               r'Circumstellar Material Intensity (Jy arc$^{-2}$)', 
          '{res}"'.format(res = np.round(info['hr']['kspatres'],3)) + r' Density (g cm$^{-2}$)', 
          '{res}"'.format(res = np.round(info['lr']['kspatres'],3)) + r' Density (g cm$^{-2}$)', 
          '{res}"'.format(res = np.round(info['hr']['kspatres'],3)) + r' After Reprojection Density (g cm$^{-2}$)', 
          r'Circumstellar Material Density (g cm$^{-2}$)']
    
    title = ['hr','lr','reproj','csm', 'hr_dens','lr_dens', 'reproj_dens','csm_dens']
    

    figure,axs = plt.subplots(nrows = 4, ncols=2, figsize = (10,16))#, subplot_kw={'projection': wcs})
    figure.suptitle(suptitle, fontsize = 18, y=1.01)

    for i,ax in zip(range(len(data)), axs.ravel()):
        j=i
        if j > 3:
            j-=4
        

        xaxis = range(data[title[i]].shape[0])*info[title[j]]['pix_size_arcsec']-((info[title[j]]['position'][0])*info[title[j]]['pix_size_arcsec'])
        yaxis = range(data[title[i]].shape[1])*info[title[j]]['pix_size_arcsec']-((info[title[j]]['position'][1])*info[title[j]]['pix_size_arcsec'])


        im = ax.pcolormesh(yaxis.value,xaxis.value,data[title[i]].value, cmap=info[title[j]]['cmap'],shading="nearest", vmin = vminmax[i][0], vmax = vminmax[i][1])
        ax.plot((info[title[j]]['position'][1])*info[title[j]]['pix_size_arcsec']-((info[title[j]]['position'][1])*info[title[j]]['pix_size_arcsec']),
                (info[title[j]]['position'][0])*info[title[j]]['pix_size_arcsec']-((info[title[j]]['position'][0])*info[title[j]]['pix_size_arcsec']),'rx')
        ax.plot(0,0,'rx')

        ax.set_title(titles[i])
        ax.set_xlim(minn, maxx)
        ax.set_ylim(minn, maxx)

        figure.colorbar(im,ax=ax)
        ax.set_xlabel(r'$\Delta$ RA (arc)' , size = 14)
        ax.set_ylabel(r'$\Delta$ DEC (arc)' , size = 14)


    figure.tight_layout(pad = 1)
    plt.show()





color = ['C6','C0','C2','C4']
def plot_1d_err(info,radius,ax1_ymin=1e-2,ax2_ymin=1e-3, ax1_ymax=1e4,ax2_ymax=1e3,xmin=0,xmax=0.45, suptitle = "Standard Deviations"):
    '''
    plot 1d density and intensity functions.
    can select plot x and y limits. default values inputted otherwise
    '''



    plt.rcParams["font.family"] = "times"
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize = [14,4])
    fig.suptitle(suptitle)

    title = ['hr','lr','reproj','csm', 'hr_dens','lr_dens', 'reproj_dens','csm_dens']
    labels = ['{res}"'.format(res = np.round(info['hr']['kspatres'],3)),
             '{res}"'.format(res = np.round(info['lr']['kspatres'],3)),
               "reproj", "csm"]    
    
    #color = [highcolor,lowcolor,'maroon','fuchsia']


    c=0
    j=0
    for j in range(len(title)):
        if j==4:
            c=0
        
        if j<4:
            ax1.plot(radius[title[c]]['arc_1d'],info[title[c]]['error'],'o-',alpha=0.4, label = labels[c], c = color[c])
        else:
            
            ax2.plot(radius[title[c]]['arc_1d'],info[title[c]]['error_dens'],'o-',alpha=0.4,label = labels[c], c = color[c])
    
        c+=1

    ax2.legend(loc = 'best', bbox_to_anchor=(0.5, 0.5, 0.5, 0.5))
    ax2.set_xlim(xmin,xmax)
    ax1.set_xlim(0,0.45)
    ax1.set_ylim(ax1_ymin, ax1_ymax)
    ax2.set_ylim(ax2_ymin, ax2_ymax)

    ax1.semilogy()
    ax2.semilogy()
    ax1.set_title("1-D Radial Intensity Comparison")
    ax2.set_title("1-D Radial Density Comaprison")
    ax1.set_xlabel('Radius (arc)')
    ax2.set_xlabel('Radius (arc)')
    ax1.set_ylabel(r'Intensity Error (Jy arc$^{-2}$)')
    ax2.set_ylabel(r'Density Error (g cm$^{-2}$')

    fig.show()


def plot_1d(data_1d,data_dens_1d,info,radius,ax1_ymin=1e-2,ax2_ymin=1e-3, ax1_ymax=1e4,ax2_ymax=1e3,xmin=0,xmax=0.45, suptitle = "1D Radial Intensity and Density Plots using original dimension data"):
    '''
    plot 1d density and intensity functions.
    can select plot x and y limits. default values inputted otherwise
    '''


    plt.rcParams["font.family"] = "times"
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize = [8,11])
    fig.suptitle(suptitle, size= '25')

    title = ['hr','lr','reproj','csm', 'hr_dens','lr_dens', 'reproj_dens','csm_dens']
    labels = ['{res}"'.format(res = np.round(info['hr']['kspatres'],3)),
             '{res}"'.format(res = np.round(info['lr']['kspatres'],3)),
            'Reprojected {res}"'.format(res = np.round(info['hr']['kspatres'],3)),
            "CSM"]    
    

    c=0
    j=0
    for j in range(len(title)):
        if j==4:
            c=0
        
        if j<4:
            ax1.plot(radius[title[c]]['arc_1d'],data_1d[title[c]].value,'o-',alpha=0.4, label = labels[c], c = color[c])
            ax1.errorbar(radius[title[c]]['arc_1d'],data_1d[title[c]].value,yerr=info[title[c]]['error'].value, c = color[c],alpha= .4)
        else:
            info[title[c]]['error_dens'] = density_model(info[title[c]]['error'],radius[title[c]]['pc_1d'])

            ax2.plot(radius[title[c]]['arc_1d'],data_dens_1d[title[c]].value,'o-',alpha=0.4,label = labels[c], c = color[c])
            ax2.errorbar(radius[title[c]]['arc_1d'],data_dens_1d[title[c]].value,yerr=info[title[c]]['error_dens'].value, c = color[c], alpha=.4)
    
        c+=1

    ax2.legend(loc = 'best', bbox_to_anchor=(0.5, 0.5, 0.5, 0.5))
    ax2.set_xlim(xmin,xmax)
    ax1.set_xlim(0,0.45)
    ax1.set_ylim(ax1_ymin, ax1_ymax)
    ax2.set_ylim(ax2_ymin, ax2_ymax)

    ax1.semilogy()
    
    ax1.yaxis.set_ticks_position('both')
    ax2.yaxis.set_ticks_position('both')
    ax1.xaxis.set_ticks_position('both')
    ax2.xaxis.set_ticks_position('both')

    ax2.semilogy()
    ax1.tick_params(direction = 'in')
    ax2.tick_params(direction = 'in')


    ax1.set_title("Radial Intensity",size=18)
    ax2.set_title("Radial Density",size=18)
    ax1.set_xlabel('Radius (arc)',size=15)
    ax2.set_xlabel('Radius (arc)',size=15)
    ax1.set_ylabel(r'Intensity (Jy arc$^{-2}$)',size=15)
    ax2.set_ylabel(r'Density (g cm$^{-2}$)',size=15)

    fig.show()


def plot_1d_skip(data_1d,data_dens_1d,info,radius,ax1_ymin=1e-2,ax2_ymin=1e-3, ax1_ymax=1e4,ax2_ymax=1e3,xmin=0,xmax=0.45, suptitle = "1D Radial Intensity and Density Plots using original dimension data"):
    '''
    plot 1d density and intensity functions.
    can select plot x and y limits. default values inputted otherwise
    '''


    plt.rcParams["font.family"] = "times"
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize = [8,11])
    fig.suptitle(suptitle,size= 25)

    title = ['lr','reproj','csm', 'lr_dens', 'reproj_dens','csm_dens']
    labels = ['{res}"'.format(res = np.round(info['lr']['kspatres'],3)),
              'Reprojected {res}"'.format(res = np.round(info['hr']['kspatres'],3)),
               "CSM"]    



    c=0
    j=0
    for j in range(len(title)):
        if j==3:
            c=0
        
        if j<3:
            #print(title[c])
            ax1.plot(radius[title[c]]['arc_1d'],data_1d[title[c]].value,'o-',alpha=0.4, label = labels[c], c = color[1:][c])
            ax1.errorbar(radius[title[c]]['arc_1d'],data_1d[title[c]].value,yerr=info[title[c]]['error'].value, c = color[1:][c],alpha=0.4)
        else:
            #print([title[c]])
            ax2.plot(radius[title[c]]['arc_1d'],data_dens_1d[title[c]].value,'o-',alpha=0.4,label = labels[c], c = color[1:][c])
            ax2.errorbar(radius[title[c]]['arc_1d'],data_dens_1d[title[c]].value,yerr=info[title[c]]['error_dens'].value, c = color[1:][c],alpha=0.4)
    
        c+=1

    ax2.legend(loc = 'best', bbox_to_anchor=(0.5, 0.5, 0.5, 0.5))
    ax2.set_xlim(xmin,xmax)
    ax1.set_xlim(0,0.45)
    ax1.set_ylim(ax1_ymin, ax1_ymax)
    ax2.set_ylim(ax2_ymin, ax2_ymax)

    ax1.semilogy()
    ax2.semilogy()

    

    ax1.yaxis.set_ticks_position('both')
    ax2.yaxis.set_ticks_position('both')
    ax1.xaxis.set_ticks_position('both')
    ax2.xaxis.set_ticks_position('both')

    ax1.tick_params(direction = 'in')
    ax2.tick_params(direction = 'in')


    ax1.set_title("1-D Radial Intensity Comparison")
    ax2.set_title("1-D Radial Density Comaprison")
    ax1.set_xlabel('Radius (arc)')
    ax2.set_xlabel('Radius (arc)')
    ax1.set_ylabel(r'Intensity (Jy arc$^{-2}$)',size=15)
    ax2.set_ylabel(r'Density (g cm$^{-2}$)',size=15)

    fig.show()