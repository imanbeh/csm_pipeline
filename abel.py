'''
Abel transform notebook

'''

import numpy as np
from astropy import units as u
from matplotlib import pyplot as plt


def all_abel(data,rad,info):
    titles = list(data.keys())
    f_rs = {}

    for t in titles:
        f_rs[t] = do_abel(data[t].value,rad[t]['pc_1d'].to(u.cm).value,info[t]['median_dens'])

    return f_rs



def do_abel(F,s,med):
    '''
    F = radial profile of surface density
    s = radii corresponding with radial profile
    med = background median- sets all neg values in F array to bkg median
    '''
    F[F<0] = med
    dF_ds = np.gradient(F,s)
    dF_ds = dF_ds[~np.isnan(dF_ds)] #this likely only works for this data bc it 
    s = s[:len(dF_ds)] # only cuts off nans if theyre all at the end of image
    f_r = np.zeros(len(s))
    r_arr = np.zeros(len(s))

    for i in range(len(s)-1):
        r = (s[i]+s[i+1])/2
        r_arr[i] = r

        integ = np.trapz(dF_ds[i+1:]/ np.sqrt(s[s>r]**2-r**2),s[s>r])

        f_r[i]= (-1/np.pi)* integ # integrate from r to highest radial value

    # print(f_r)

    return f_r
 

def plot_1d_abel(data_abel_1d,info,radius,ax_ymin=1e-2, ax_ymax=1e4,xmin=0,xmax=0.45, suptitle = "1D Abel Transformation (g/cm3)", dent=False):
    '''
    plot 1d density and intensity functions.
    can select plot x and y limits. default values inputted otherwise
    '''


    plt.rcParams["font.family"] = "times"
    fig, ax = plt.subplots(1, 1, figsize = [7,4])
    fig.suptitle(suptitle)

    title = ['hr','lr','reproj','csm']
    labels = ['{res}"'.format(res = np.round(info['hr']['kspatres'],3)),
             '{res}"'.format(res = np.round(info['lr']['kspatres'],3)),
             'Reprojected {res}"'.format(res = np.round(info['hr']['kspatres'],3)),
             "CSM"]    
    
    color = ['C6','C0','C2','C4']

    for j in range(len(title)):


            ax.plot(radius[title[j]]['arc_1d'][:len(data_abel_1d[title[j]])],data_abel_1d[title[j]],'o-',alpha=0.4, label = labels[j], c = color[j])
            #ax.errorbar(radius[title[c]]['arc_1d'],data_1d[title[c]].value,yerr=info[title[c]]['error'].value, c = color[c])

    

    if(dent == True):
         m_e = 9.109e-28 # electron mass in g
         m_p = 1.6726e-24
         plt.axhline(y=(m_e+m_p)*3e8/(0.7), label = "Dent 2025",color = 'black', ls = ':')
         plt.axhline(y=(m_e+m_p)*2e8/(0.7), label = "Judge 1998", color = 'red', ls = '--')
         plt.axhline(y=(m_e+m_p)*1e9/(0.7), label = "Harper 2006", color = 'orange',ls = '-.')



    ax.legend(loc = 'best', bbox_to_anchor=(0.5, 0.5, 0.5, 0.5))
    ax.set_xlim(xmin,xmax)
    ax.set_xlim(0,0.45)
    ax.set_ylim(ax_ymin, ax_ymax)
    ax.set_ylim(ax_ymin, ax_ymax)

    ax.semilogy()
#     ax.set_title("1-D Density (g/cm3)")
    ax.set_xlabel('Radius (arc)')
    ax.set_ylabel(r'Density (g cm$^{-3}$)')

    fig.show()
