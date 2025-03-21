import re
"""
#
############
# uid___A002_Xac9223_X58, uid___A002_Xac97ce_X14e 
# faint phase-ref: used calibration from spw 2,4 for 0,1,2 and 3,4

# Average in frequency for speed of imaging
#
path='/raid1/scratch/amsr/Betelgeuse/ALMA/2015.1.00206.S/science_goal.uid___A001_X2de_Xf5/group.uid___A001_X2de_Xf6/member.uid___A001_X2de_Xf7/'

# CONT
viss=[path+'calibrated/uid___A002_Xaca510_X78d.calibration/uid___A002_Xaca510_X78d.ms.split.cal',path+'raw/X58/uid___A002_Xac9223_X58.ms.split.cal',path+'/raw/X14e/uid___A002_Xac97ce_X14e.ms.split.cal']
vroot=['X78d', 'X58','X14e']


spws=[0,1,2,3,4]
cwds=[16,8,16,16,16]
contcata=[]
"""
"""
# Shift Betelgeuse to phase center
for v in [1,2]:  
    fixvis(vis=viss[v],field='Betelgeuse', outputvis=vroot[v]+'.fxvs', phasecenter='J2000 05h55m10.331s 07d24m25.571s')


for v in range(3):
    for s in spws:
        os.system('rm -rf '+vroot[v]+'_spw'+str(s)+'.ms')
        mstransform(vis=vroot[v]+'.fxvs',
                    outputvis=vroot[v]+'_spw'+str(s)+'.ms',
                    field='Betelgeuse',
                    spw=str(s),
                    datacolumn='data',
                    regridms=T,
                    width=cwds[s])

        contcata.append(vroot[v]+'_spw'+str(s)+'.ms')


os.system('rm -rf Betelgeuse_TE_cont.ms')
concat(vis=contcata,
       concatvis='Betelgeuse_TE_cont.ms',
       freqtol='2MHz',
       dirtol='1arcsec')

contchansavg='0:0~9;24~59,1:2~10;18~23,2:25~39;59~119,3:0~28;42~59,4:0~37;88~97;100~119'

#LINE
linecata=[]
for v in range(3):
    for s in spws:

v=2
for s in range(4):
    mstransform(vis=vroot[v]+'.fxvs',
                outputvis=vroot[v]+'_spw'+str(s)+'L.ms',
                field='Betelgeuse',
                spw=str(s),
                datacolumn='data',
                outframe='lsrk',
                regridms=T)
 
for v in range(3):
    for s in spws:
        os.system('rm -rf '+vroot[v]+'_spw'+str(s)+'L.ms')
        mstransform(vis=vroot[v]+'.fxvs',
                    outputvis=vroot[v]+'_spw'+str(s)+'L.ms',
                    field='Betelgeuse',
                    spw=str(s),
                    datacolumn='data',
                    outframe='lsrk',
                    regridms=T)
        linecata.append(vroot[v]+'_spw'+str(s)+'L.ms')


linecata=['X78d_spw0L.ms','X78d_spw1L.ms','X78d_spw2L.ms','X78d_spw3L.ms','X78d_spw4L.ms','X58_spw0L.ms','X58_spw1L.ms','X58_spw2L.ms','X58_spw3L.ms','X58_spw4L.ms','X14e_spw0L.ms','X14e_spw1L.ms','X14e_spw2L.ms','X14e_spw3L.ms','X14e_spw4L.ms']

os.system('rm -rf Betelgeuse_TE_line.ms')
concat(vis=linecata,
       concatvis='Betelgeuse_TE_line.ms',
       freqtol='2MHz',
       dirtol='1arcsec')



###############################

# check bad data - see Eamon's script
# orig data scan='137~202'

os.system('rm -rf Betelgeuse_TE_cont.image*')
tclean(vis ='Betelgeuse_TE_cont.ms',
  imagename ='Betelgeuse_TE_cont.image',
  spw = contchansavg,
  specmode = 'mfs',
  interpolation = 'linear',
  niter = 50000,
  scan='137~202',
  threshold = '0.3mJy',
  weighting='briggs',
  robust=0.5,
  interactive = True,
  imsize = [300,300],
  cell = '0.002arcsec',
  savemodel='virtual')
# S/N  6.012807e-02/  5.926911e-04   101

ft(vis='Betelgeuse_TE_cont.ms',
   model='Betelgeuse_TE_cont.image.model')

os.system('rm -rf Betelgeuse_TE_cont.p1')
gaincal(vis ='Betelgeuse_TE_cont.ms',
        caltable='Betelgeuse_TE_cont.p1',
        spw=contchansavg,
        calmode='p',
        refant='DV19,DA58',
        solint='inf')

applycal(vis ='Betelgeuse_TE_cont.ms',
         gaintable='Betelgeuse_TE_cont.p1',
#         applymode='calonly',
         calwt=False)

##########

os.system('rm -rf Betelgeuse_TE_cont_p1.image*')
tclean(vis ='Betelgeuse_TE_cont.ms',
  imagename ='Betelgeuse_TE_cont_p1.image',
  spw = contchansavg,
  specmode = 'mfs',
  deconvolver='mtmfs',
  nterms=2,
  interpolation = 'linear',
  niter = 50000,
  scan='137~202',
  threshold = '0.3mJy',
  weighting='briggs',
  robust=0.5,
  interactive = True,
  imsize = [300,300],
  cell = '0.002arcsec',
  savemodel='virtual')
#7.161076e-02 / 1.493844e-04  479

####### a 
ft(vis='Betelgeuse_TE_cont.ms',
   nterms=2,
   model=['Betelgeuse_TE_cont_p1.image.model.tt0','Betelgeuse_TE_cont_p1.image.model.tt1'],
   usescratch=True)# needed in 5.1?

os.system('rm -rf Betelgeuse_TE_cont.a1')
gaincal(vis ='Betelgeuse_TE_cont.ms',
        caltable='Betelgeuse_TE_cont.a1',
        spw=contchansavg,
        refant='DV19,DA48',
        calmode='a',
        solint='inf',
        gaintable='Betelgeuse_TE_cont.p1')

applycal(vis ='Betelgeuse_TE_cont.ms',
         gaintable=['Betelgeuse_TE_cont.a1','Betelgeuse_TE_cont.p1'],
#         applymode='calonly',
         calwt=False)
#execfile('../Scripts/scal_imag_aori.py')

os.system('rm -rf Betelgeuse_TE_cont_ap1.image*')
tclean(vis ='Betelgeuse_TE_cont.ms',
  imagename ='Betelgeuse_TE_cont_apa.image',
  spw = contchansavg,
  specmode = 'mfs',
  deconvolver='mtmfs',
  nterms=2,
  interpolation = 'linear',
  niter = 50000,
#  scan='137~202',
  threshold = '0.3mJy',
  weighting='briggs',
  robust=0.5,
  interactive = True,
  imsize = [300,300],
  cell = '0.002arcsec',
  savemodel='virtual')
#6.888715e-02/5.329439e-05  1292.577886715656  


######

ft(vis='Betelgeuse_TE_cont.ms',
   nterms=2,
   model=['Betelgeuse_TE_cont_ap1.image.model.tt0','Betelgeuse_TE_cont_ap1.image.model.tt1'])

# Shorter solint fails too many solutions
# try weighting

### 
# and with weighting:
flagmanager(vis ='Betelgeuse_TE_cont.ms',
            mode='save',
            versionname='preapplyap1')

applycal(vis ='Betelgeuse_TE_cont.ms',
         gaintable=['Betelgeuse_TE_cont.a1','Betelgeuse_TE_cont.p1'],
         applymode='calflag',
         calwt=True)

os.system('rm -rf Betelgeuse_TE_cont_ap1wt.image*')
tclean(vis ='Betelgeuse_TE_cont.ms',
  imagename ='Betelgeuse_TE_cont_ap1wt.image',
  spw = contchansavg,
  specmode = 'mfs',
  deconvolver='mtmfs',
  nterms=2,
  interpolation = 'linear',
  niter = 50000,
#  scan='137~202',
  threshold = '0.1mJy',
  weighting='briggs',
  robust=0.5,
  interactive = T,
  imsize = [300,300],
  cell = '0.002arcsec',
  savemodel='virtual')

flagmanager(vis ='Betelgeuse_TE_cont.ms',
            mode='save',
            versionname='preapplyap2')

ft(vis='Betelgeuse_TE_cont.ms',
   nterms=2,
   model=['Betelgeuse_TE_cont_ap1wt.image.model.tt0','Betelgeuse_TE_cont_ap1wt.image.model.tt1'])

os.system('rm -rf Betelgeuse_TE_cont.a2')
gaincal(vis ='Betelgeuse_TE_cont.ms',
        caltable='Betelgeuse_TE_cont.a2',
        spw=contchansavg,
        gaintype='T',
        calmode='a',
        refant='DV19,DA48',
        solint='30s',
        gaintable=['Betelgeuse_TE_cont.a1','Betelgeuse_TE_cont.p1'])


applycal(vis ='Betelgeuse_TE_cont.ms',
         gaintable=['Betelgeuse_TE_cont.a2','Betelgeuse_TE_cont.a1','Betelgeuse_TE_cont.p1'],
         applymode='calflag',
         calwt=True,
         flagbackup=False)

os.system('rm -rf Betelgeuse_TE_cont_ap2wt.image*')
tclean(vis ='Betelgeuse_TE_cont.ms',
  imagename ='Betelgeuse_TE_cont_ap2wt.image',
  spw = contchansavg,
  specmode = 'mfs',
  deconvolver='mtmfs',
  nterms=2,
  interpolation = 'linear',
  niter = 50000,
  threshold = '0.1mJy',
  weighting='briggs',
  robust=0.5,
  interactive = T,
  imsize = [300,300],
  cell = '0.002arcsec',
  savemodel='virtual')
# NO IMPROVEMENT use ap1wt


#################
# pbcor
impbcor(imagename='Betelgeuse_TE_cont.image.image',
        pbimage='Betelgeuse_TE_cont.image.pb',
        outfile='Betelgeuse_TE_cont.image.image.pbcor')

impbcor(imagename='Betelgeuse_TE_cont_ap1wt.image.image.tt0',
        pbimage='Betelgeuse_TE_cont_ap1wt.image.pb.tt0',
        outfile='Betelgeuse_TE_cont_ap1wt.image.tt0.pbcor')



#### apply to line
applycal(vis ='Betelgeuse_TE_line.ms',
         gaintable=['Betelgeuse_TE_cont.a1','Betelgeuse_TE_cont.p1'],
         spw='0,1,2,3,4',
         spwmap=[[0,1,2,3,4],[0,1,2,3,4]],
         applymode='calflag',
         calwt=True)

# Average in time now calibration done

contchline='0:1~160;300~959,1:1~100;140~239,2:1~160;465~650;1070~1919,3:0~440;540~958,4:0~530;900~1918'

# Test image 
# image line   
# 12CO spw 1           DONE
os.system('rm -rf Betelgeuse_TEtav_nocontsub_12CO.image*')
tclean(vis ='Betelgeuse_TEtav_line.ms',
  imagename ='Betelgeuse_TEtav_nocontsub_12CO.image',
  spw = '1',
  specmode = 'cube',
  restfreq='345.79599GHz',
  outframe='lsrk',
  start=100,
  nchan=41,
  niter = 1000000,
  threshold = '1mJy',
  weighting='briggs',
  robust=0.5,
  interactive = T,
  imsize = [2000,2000],
  cell = '0.002arcsec')
# rms off-peak 1** mJy/bm


#subtract continuum
os.system('rm -rf Betelgeuse_TEtav_line.ms.contsub')
uvcontsub3(vis ='Betelgeuse_TEtav_line.ms',
          combine='spw',
          fitspw=contchline,
          fitorder=1)

# 
# image line   
# 12CO spw 1           DONE
os.system('rm -rf Betelgeuse_TEtav_12CO.image*')
tclean(vis ='Betelgeuse_TEtav_line.ms.contsub',
  imagename ='Betelgeuse_TEtav_12CO.image',
  spw = '1',
  specmode = 'cube',
  restfreq='345.79599GHz',
  outframe='lsrk',
  start=100,
  nchan=41,
  niter = 1000000,
  threshold = '1mJy',
  weighting='briggs',
  robust=0.5,
  interactive = T,
  imsize = [2000,2000],
  cell = '0.002arcsec')
# rms off-peak 1 mJy/bm

#### SO2
os.system('rm -rf Betelgeuse_TEtav_SO2.image*')
tclean(vis ='Betelgeuse_TEtav_line.ms.contsub',
  imagename ='Betelgeuse_TEtav_SO2.image',
  spw = '0',
  specmode = 'cube',
  restfreq='345.1489708GHz',
  outframe='lsrk',
  start=185,
  nchan=81,
  niter = 1000000,
#  pbcor=True,
  threshold = '2mJy',
  weighting='briggs',
  robust=0.5,
  interactive = T,
  imsize = [2000,2000],
  cell = '0.002arcsec')

342.5043830E9 28SiOv2
342.9808470E9 29SiOv0 '595~894'
344.9163321E9 28SiOv1 89 28SiO(v=1, J=8-7) : 344.9163321 GHz
345.7959899E9 12COv0

###################
# 29SiO spw2 DONE
os.system('rm -rf Betelgeuse_TEtav_29SiOv0.image*')
tclean(vis ='Betelgeuse_TEtav_line.ms.contsub',
  imagename ='Betelgeuse_TEtav_29SiOv0.image',
  spw = '2',
  specmode = 'cube',
  restfreq='342.980848GHz',
  outframe='lsrk',
  start=595,
  nchan=300,
  niter = 1000000,
#  pbcor=True,
  threshold = '2mJy',
  weighting='briggs',
  robust=0.5,
  interactive = T,
  imsize = [2000,2000],
  cell = '0.002arcsec')

# 28SiO spw2  D
os.system('rm -rf Betelgeuse_TEtav_28SiOv2.image*')
tclean(vis ='Betelgeuse_TEtav_line.ms.contsub',
  imagename ='Betelgeuse_TEtav_28SiOv2.image',
  spw = '2',
  specmode = 'cube',
  restfreq='342.504383GHz',
  outframe='lsrk',
  start=157,
  nchan=200,
  niter = 1000000,
#  pbcor=True,
  threshold = '2mJy',
  weighting='briggs',
  robust=0.5,
  interactive = T,
  imsize = [2000,2000],
  cell = '0.002arcsec')

344.9163321E9 28SiOv1 89 28SiO(v=1, J=8-7) : 344.9163321 GHz

os.system('rm -rf Betelgeuse_TEtav_28SiOv1.image*')
tclean(vis ='Betelgeuse_TEtav_line.ms.contsub',
  imagename ='Betelgeuse_TEtav_28SiOv1.image',
  spw = '0',
  specmode = 'cube',
  restfreq='344.9163321GHz',
  outframe='lsrk',
  start=89,
  nchan=300,
  niter = 1000000,
#  pbcor=True,
  threshold = '2mJy',
  weighting='briggs',
  robust=0.5,
  interactive = T,
  imsize = [2000,2000],
  cell = '0.002arcsec')

os.system('rm -rf Betelgeuse_TEtav_spw2_29SiOv0_300ch.image')
imsubimage(imagename = 'Betelgeuse_TEtav_29SiOv0.image.image',
    box='750,750,1249,1249',
    chans='0~299',
    outfile='Betelgeuse_TEtav_spw2_29SiOv0_300ch.image')

os.system('rm -rf Betelgeuse_TEtav_spw2_28SiOv2_?00ch.image')
imsubimage(imagename = 'Betelgeuse_TEtav_28SiOv2.image.image',
    box='750,750,1249,1249',
    chans='0~199',
    outfile='Betelgeuse_TEtav_spw2_28SiOv2_200ch.image')

os.system('rm -rf Betelgeuse_TEtav_spw0_28SiOv1_300ch.image')
imsubimage(imagename = 'Betelgeuse_TEtav_28SiOv1.image.image',
    box='750,750,1249,1249',
    outfile='Betelgeuse_TEtav_spw0_28SiOv2_200ch.image')

##################
# 13CO spw3
os.system('rm -rf Betelgeuse_TEtav_13CO.image*')
tclean(vis ='Betelgeuse_TEtav_line.ms.contsub',
  imagename ='Betelgeuse_TEtav_13CO.image',
  spw = '3',
  specmode = 'cube',
  restfreq='330.5879653GHz',
  outframe='lsrk',
  start=500,
  nchan=81,
  niter = 1000000,
#  pbcor=True,
  threshold = '2mJy',
  weighting='briggs',
  robust=0.5,
  interactive = True,
  imsize = [2000,2000],
  cell = '0.002arcsec')


####### execfile('../Scripts/scal_imag_aori.py')##########

#Allch
"""
"""
# REDO with CASA 5
# per spw
###################
thresh=['2mJy','1.5mJy','2mJy','2mJy','2mJy']
for s in range(1):
    os.system('rm -rf Betelgeuse_TEtav_spw'+str(s)+'.image*')
    tclean(vis ='Betelgeuse_TEtav_line.ms.contsub',
           imagename ='Betelgeuse_TEtav_spw'+str(s)+'.image',
           spw = str(s),
           specmode = 'cube',
           outframe='lsrk',
           niter = 1000000,
#           pbcor=True,
           threshold = thresh[s],
           weighting='briggs',
           robust=0.5,
           interactive = True,
           chanchunks=4,
           mask='circle[[500pix, 500pix],480pix]',
           imsize = [1000,1000],
           cell = '0.002arcsec')
# spw 0 SiO v=1 abs. against str, more extended emission
# spw 1 12CO emission, some abs.
# spw 2 SiO v=2, 29SiO v=0 mainly abs.
# spw 3 13CO
# spw 4




thresh=['2mJy','1.5mJy','2mJy','2mJy','2mJy']
for s in range(3,5):
    os.system('rm -rf Betelgeuse_TEtav_spw'+str(s)+'_withcont.image*')
    tclean(vis ='Betelgeuse_TEtav_line.ms',
           imagename ='Betelgeuse_TEtav_spw'+str(s)+'_withcont.image',
           spw = str(s),
           specmode = 'cube',
           outframe='lsrk',
           niter = 1000000,
#           pbcor=True,
           threshold = thresh[s],
           weighting='briggs',
           robust=0.5,
           interactive = True,
           chanchunks=4,
           mask='circle[[500pix, 500pix],480pix]',
           imsize = [1000,1000],
           cell = '0.002arcsec')
#
"""
"""
'Betelgeuse_TEtav_13CO.image.image',
ims=['Betelgeuse_TE_cont.image.image','Betelgeuse_TE_cont_ap1wt.image.image.tt0','Betelgeuse_TE_cont_ap1wt.image.alpha','Betelgeuse_TE_cont_ap1wt.image.alpha.error','Betelgeuse_TEtav_12CO.image.image','Betelgeuse_TEtav_spw0.image.image','Betelgeuse_TEtav_spw1.image.image','Betelgeuse_TEtav_spw2.image.image','Betelgeuse_TEtav_spw3.image.image','Betelgeuse_TEtav_spw4.image.image']
for i in ims: 
    exportfits(imagename=i,
               fitsimage=i+'.fits')
    os.system('tar -zcvf '+i+'.tgz '+i)

TEf=['345.2GHz','345.8GHz','343.2GHz','330.6GHz','332.6GHz']
TCf=['345.8GHz','345.2GHz','343.2GHz','330.6GHz','332.6GHz']                

for s in range(5):
    mstransform(vis ='Betelgeuse_TE_cont.ms',
                outputvis='Betelgeuse_TEcont'+TEf[s]+'.ms',
                spw=str(s),
                timeaverage=True,
                timebin='6.048s')

#** BUT TC 60-100 m baselines ~420 mJy; TE ~600 mJy
# See 206.txt. TC may be underscaled by at least 20%? 
# but that only accounts for half the difference. TE overscaled?
# shift the TC data to the TE position - see TC py and .listobs
#Also need to rescale by 600/420? x 1.428  
# uvmod script  Betelgeuse_TC_cont_shfxscl.ms

os.system('rm -rf Betelgeuse_TCcont*GHz.ms')
for s in range(5):
    mstransform(vis ='Betelgeuse_TC_cont_shfxscl.ms',
                outputvis='Betelgeuse_TCcont'+TCf[s]+'.ms',
                spw=str(s))

contvis=['Betelgeuse_TCcont330.6GHz.ms','Betelgeuse_TCcont332.6GHz.ms','Betelgeuse_TCcont343.2GHz.ms','Betelgeuse_TCcont345.2GHz.ms','Betelgeuse_TCcont345.8GHz.ms','Betelgeuse_TEcont330.6GHz.ms','Betelgeuse_TEcont332.6GHz.ms','Betelgeuse_TEcont343.2GHz.ms','Betelgeuse_TEcont345.2GHz.ms','Betelgeuse_TEcont345.8GHz.ms']

os.system('rm -rf Betelgeuse_all_cont_1-1.ms')
concat(vis=contvis,
       concatvis='Betelgeuse_all_cont_1-1.ms',
       freqtol='2MHz',
       dirtol='1arcsec')

# old spw in new order, TE first: 3,4,2,0,1  3,4,2,1,0
contchall='0:0~28;42~59, 1:0~37;88~97;100~119,2:25~39;59~119,3:0~9;24~59,4:2~10;18~23,5:0~28;42~59, 6:0~37;88~97;100~119,7:25~39;59~119,8:4~9;24~59,9:0~10;18~23'

# Using rescaled, aligned TC
os.system('rm -rf Betelgeuse_all_cont_1-1.image*')
tclean(vis ='Betelgeuse_all_cont_1-1.ms',
  imagename ='Betelgeuse_all_cont_1-1.image',
  spw = contchall,
  specmode = 'mfs',
  deconvolver='mtmfs',
  nterms=2,
  interpolation = 'linear',
  niter = 1000,
  threshold = '0.03mJy',
  weighting='briggs',
  robust=1.5,
  uvtaper='10000klambda',
  interactive = T,
  imsize = [1000,1000],
  cell = '0.005arcsec')
# ~40-mas beam

for s in range(5):  
    mstransform(vis='Betelgeuse_TEtav_line.ms.contsub',
                outputvis='Betelgeuse_TEline'+TEf[s]+'.ms.contsub',
                spw=str(s),
                datacolumn='data')

#** SCALE TC FIRST
#** Guess that 25% is mis-flux-scaling, 
# Betelgeuse_TC_line_shfxscl.ms.contsub
for s in range(5):  
    mstransform(vis='Betelgeuse_TC_line_shfxscl.ms.contsub',
                outputvis='Betelgeuse_TCline_shfxscl'+TCf[s]+'.ms.contsub',
                spw=str(s),
                datacolumn='data')


# concat just each spw separately
Ff=['330.6GHz','332.6GHz','343.2GHz','345.2GHz','345.8GHz']

TElines=['Betelgeuse_TEline330.6GHz.ms.contsub','Betelgeuse_TEline332.6GHz.ms.contsub','Betelgeuse_TEline343.2GHz.ms.contsub','Betelgeuse_TEline345.2GHz.ms.contsub','Betelgeuse_TEline345.8GHz.ms.contsub']
TClines=['Betelgeuse_TCline_shfxscl330.6GHz.ms.contsub','Betelgeuse_TCline_shfxscl332.6GHz.ms.contsub','Betelgeuse_TCline_shfxscl343.2GHz.ms.contsub','Betelgeuse_TCline_shfxscl345.2GHz.ms.contsub','Betelgeuse_TCline_shfxscl345.8GHz.ms.contsub']

for i in range(5):
    os.system('rm -rf Betelgeuse_allines_'+Ff[i]+'.ms.contsub')
    concat(vis=[TElines[i],TClines[i]],
       concatvis='Betelgeuse_allines_'+Ff[i]+'.ms.contsub',
       dirtol='1arcsec')

"""
#### IMAGE ALL ****
#
Ff=['330.6GHz','332.6GHz','343.2GHz','345.2GHz','345.8GHz']

# redo 330.6, don't mask first ~40 chan as no T1

chch=[4,8,8,4,1]
st=[32,32,32,32,16]
nch=[896,1856,1856,896,208]
thresh=['3.5mJy','3.5mJy','3.5mJy','3.5mJy','2.5mJy']
for i in range(1**):
#    listobs(vis='Betelgeuse_allines_'+Ff[i]+'.ms.contsub',
#            listfile='Betelgeuse_allines_'+Ff[i]+'.ms.contsub.listobs')
    os.system('rm -rf Betelgeuse_allines_'+Ff[i]+'.image*')
    tclean(vis='Betelgeuse_allines_'+Ff[i]+'.ms.contsub',
           imagename='Betelgeuse_allines_'+Ff[i]+'.image',
           specmode='cube',
           outframe='lsrk',
           start=st[i]
           nchan=nch[i],
           niter = nch[i]*5000,
           threshold = thresh[i],
           mask='circle[[500pix, 500pix],480pix]',
           weighting='briggs',
           robust=0.5,
           cell = '0.002arcsec',
           interactive = True,
           deconvolver='multiscale',
           scales=[0,8,16,32],
           imsize = [1000,1000],
           pbcor=False,
           chanchunks=chch[i])

#### Continuum

os.system('rm -rf Betelgeuse_all_cont_1-1.image*')
tclean(vis ='Betelgeuse_all_cont_1-1.ms',
  imagename ='Betelgeuse_all_cont_1-1.image',
  spw = contchall,
  specmode = 'mfs',
  deconvolver='mtmfs',
  nterms=2,
  interpolation = 'linear',
  niter = 1000,
  threshold = '0.03mJy',
  weighting='briggs',
  robust=0.5,
  interactive = True,
  imsize = [1000,1000],
  cell = '0.002arcsec')

6:50
1:50  332.7

"""

#HIRES ALL TEST
tclean(vis='Betelgeuse_allines_345.8GHz.ms.contsub',
       imagename='Betelgeuse_allines_12COTESTChCh.image',
       specmode='cube',
       restfreq='345.79599GHz',
       outframe='lsrk',
       start=100,
       nchan=36,
       niter = 100000,
       threshold = '3.5mJy',                  
       mask='circle[[500pix, 500pix],400pix]',
       weighting='briggs',
       robust=0.5,
       interactive = False,
       deconvolver='multiscale',
       scales=[0,8,16,32],
       imsize = [1000,1000],
       pbcor=False,
       chanchunks=4,
       cell = '0.002arcsec')

tclean(vis='Betelgeuse_allines_345.8GHz.ms.contsub',
       imagename='Betelgeuse_allines_12COTEST.image',
       specmode='cube',
       restfreq='345.79599GHz',
       outframe='lsrk',
       start=100,
       nchan=36,
       niter = 100000,
       threshold = '3.5mJy',                  
       mask='circle[[500pix, 500pix],400pix]',
       weighting='briggs',
       robust=0.5,
       interactive = False,
       deconvolver='multiscale',
       scales=[0,8,16,32],
       imsize = [1000,1000],
       pbcor=False,
       cell = '0.002arcsec')
# 26x24 mas



# Just 12CO:
tclean(vis='Betelgeuse_allines_345.8GHz.ms.contsub',
       imagename='Betelgeuse_allines_12CO.image',
       specmode='cube',
       restfreq='345.79599GHz',
       outframe='lsrk',
       start=100,
       nchan=36,
       niter = 1000000,
       threshold = '2mJy',                  
       mask='circle[[2000pix, 2000pix],600pix]',
       weighting='briggs',
       robust=1.5,
       uvtaper='10000klambda',
       interactive = T,
       deconvolver='multiscale',
       scales=[0,8,16,32],
       imsize = [4000,4000],
       pbcor=True,
       chanchunks=4,
       cell = '0.005arcsec')


# 13CO
    tclean(vis='Betelgeuse_allines_330.6GHz.ms.contsub',
           imagename='Betelgeuse_allines_13CO.image',
           specmode='cube',
           restfreq='330.5879653GHz',
           outframe='lsrk',
           start=457,
           nchan=41,
           niter = 1000000,
           threshold = '3mJy',
           mask='circle[[2000pix, 2000pix],600pix]',
           weighting='briggs',
           robust=1.5,
           uvtaper='10000klambda',
           interactive = T,
           deconvolver='multiscale',
           scales=[0,8,16,32],
           imsize = [4000,4000],
           pbcor=True,
           chanchunks=4,
           cell = '0.005arcsec')

# 28SiO v=1 Betelgeuse_allines_345.2GHz.ms.contsub
os.system('rm -rf Betelgeuse_allines_28SiOv1.image*')
    tclean(vis='Betelgeuse_allines_345.2GHz.ms.contsub',
           imagename='Betelgeuse_allines_28SiOv1.image',
           specmode='cube',
           restfreq='344.9163321GHz',
           outframe='lsrk',
           start=190,
           nchan=86,
           niter = 1000000,
           threshold = '3mJy',
           weighting='briggs',
           robust=1.5,
           uvtaper='10000klambda',
           interactive = T,
           deconvolver='multiscale',
           scales=[0,8,16,32],
           imsize = [512,512],
           pbcor=True,
           cell = '0.005arcsec')

345.79 GHz: extremely extended 12CO emission
DONE

28SiO(v=1, J=8-7) : 344.9163321 GHz
DONE

330.58 GHz: extended 13CO emission, at least to 8" in radius
DONE

342.49 GHz: compact, less than 0.2" in radius
line 28SiO(v=0, J=8-7), rest 342.5043830 +/- 0.00001 GHz (CDMS)

342.98 GHz: extension to about 0.4" in radius
 29SiO(v=0, J=8-7), rest 342.9808470

os.system('rm -rf Betelgeuse_allines_28SiOv0.image*')
    tclean(vis='Betelgeuse_allines_343.2GHz.ms.contsub',
           imagename='Betelgeuse_allines_28SiOv0.image',
           specmode='cube',
           restfreq='342.5043830GHz',
           outframe='lsrk',
           start=210,
           nchan=86,
           niter = 1000000,
           threshold = '25mJy',
           weighting='briggs',
           robust=1.5,
           uvtaper='10000klambda',
           interactive = T,
           deconvolver='multiscale',
           scales=[0,8,16,32],
           imsize = [2000,2000],
           pbcor=True,
           cell = '0.005arcsec')

os.system('rm -rf Betelgeuse_allines_29SiOv0.image*')
    tclean(vis='Betelgeuse_allines_343.2GHz.ms.contsub',
           imagename='Betelgeuse_allines_29SiOv0.image',
           specmode='cube',
           restfreq='342.9808470GHz',
           outframe='lsrk',
           start=690,
           nchan=86,
           niter = 1000000,
           threshold = '2.5mJy',
           weighting='briggs',
           robust=1.5,
           uvtaper='10000klambda',
           interactive = T,
           deconvolver='multiscale',
           scales=[0,8,16,32],
           imsize = [2000],
           pbcor=True,
           cell = '0.005arcsec')

 



ims=['Betelgeuse_allines_12CO.image.image.pbcor','Betelgeuse_allines_13CO.image.image.pbcor','Betelgeuse_allines_28SiOv0.image.image.pbcor','Betelgeuse_allines_28SiOv1.image.image.pbcor','Betelgeuse_allines_29SiOv0.image.image.pbcor','Betelgeuse_all_cont_1-1.image.image.tt0']

ims=['Betelgeuse_allines_330.6GHz.image.image','Betelgeuse_allines_345.8GHz.image.image','Betelgeuse_allines_345.2GHz.image.image','Betelgeuse_allines_343.2GHz.image.image','Betelgeuse_allines_332.6GHz.image.image']


ims=['Betelgeuse_TEtav_spw4_withcont.image.image','Betelgeuse_TEtav_spw3_withcont.image.image','Betelgeuse_TEtav_spw2_withcont.image.image','Betelgeuse_TEtav_spw1_withcont.image.image','Betelgeuse_TEtav_spw0_withcont.image.image']

for i in ims:
    exportfits(imagename=i,fitsimage=i+'.fits')
    os.system('cp '+i+'.fits /scratch/almanas/amsr/Betelgeuse/ALMA')
    os.system('tar -zcvf '+i+'.tgz '+i)
    os.system('cp '+i+'.tgz /scratch/almanas/amsr/Betelgeuse/ALMA')


#NB the combined continuum image is not very good; no more emission
#seems to appear than in the TC image and it is dynamic range limited
#(~1000), as is the TE continuum image I made using all 3 executions
#of the continuum, possibly becaues of slight amp mis-scaling which
#could be due to variability or to the less-good data sets. However,
#the line images do seem to have good increased sensitivity!

wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_all_cont_1-1.image.alpha.error.tgz
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_all_cont_1-1.image.alpha.tgz
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_all_cont_1-1.image.image.tt0.tgz
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_all_cont_1-1.image.tt0.tgz
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_12CO.image.image.pbcor.tgz
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_12CO.image.image.tgz
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_12CO.image.pbcor.tgz
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_13CO.image.image.pbcor.tgz
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_13CO.image.image.tgz
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_13CO.image.pbcor.tgz
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_28SiOv0.image.image.pbcor.tgz
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_28SiOv0.image.image.tgz
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_28SiOv0.image.pbcor.tgz
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_28SiOv1.image.image.pbcor.tgz
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_28SiOv1.image.image.tgz
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_28SiOv1.image.pbcor.tgz
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_29SiOv0.image.image.pbcor.tgz
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_29SiOv0.image.image.tgz
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_29SiOv0.image.pbcor.tgz

wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_all_cont_1-1.image.alpha.error.fits
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_all_cont_1-1.image.alpha.fits
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_all_cont_1-1.image.image.tt0.fits
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_12CO.image.image.pbcor.fits
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_12CO.image.image.fits
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_13CO.image.image.fits
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_13CO.image.image.pbcor.fits
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_28SiOv0.image.image.fits
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_28SiOv0.image.image.pbcor.fits
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_28SiOv1.image.image.fits
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_28SiOv1.image.image.pbcor.fits
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_29SiOv0.image.image.fits
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/All/Betelgeuse_allines_29SiOv0.image.image.pbcor.fits

# Image made with no continuum subtraction for checking ; the spectral
# profile seems identical but displaced, very slight difefrenrces
# probably solely due to different masking as I did it interactively.
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/Betelgeuse_TEtav_nocontsub_12CO.image.image.fits
wget -c /scratch/almanas/amsr/Betelgeuse/ALMA/Betelgeuse_TEtav_nocontsub_12CO.image.image.tgz
#(compare with Betelgeuse_TEtav_12CO.image.image.fits etc.)


#########


# Try R0?
os.system('rm -rf Betelgeuse_TEtavR0_12CO.image*')
tclean(vis ='Betelgeuse_TEtav_line.ms.contsub',
  imagename ='Betelgeuse_TEtavR0_12CO.image',
  spw = '1',
  specmode = 'cube',
  restfreq='345.79599GHz',
  outframe='lsrk',
  start=100,
  nchan=41,
  niter = 1000000,
  threshold = '2mJy',
  weighting='briggs',
  robust=0,
  interactive = T,
  imsize = [2000,2000],
  cell = '0.002arcsec')
# Beam 0.0209 0.0159 71

# Make continuum at exact same beam
# and per-spw:
# contchansavg='0:0~9;24~59,1:2~10;18~23,2:25~39;59~119,3:0~28;42~59,4:0~37;88~97;100~119'
sconts=['0:0~9;24~59','1:2~10;18~23','2:25~39;59~119','3:0~28;42~59','4:0~37;41~68;88~97;100~119']
sbeams=[['0.0185arcsec','0.0172arcsec', '63deg'],['0.0209arcsec','0.0159arcsec', '71deg'],['0.0182arcsec','0.0174arcsec', '64deg'],['0.0196arcsec','0.0182arcsec', '80deg'],['0.0187arcsec','0.0179arcsec', '82deg']]
sr=[0.5,0.0,0.5,0.5,0.5]

i=2
os.system('rm -rf Betelgeuse_TE_cont_spw'+str(i)+'.image*')
tclean(vis ='Betelgeuse_TE_cont.ms',
  imagename ='Betelgeuse_TE_cont_spw'+str(i)+'.image',
  spw = sconts[i],
  specmode = 'mfs',
  deconvolver='mtmfs',
  nterms=2,
  interpolation = 'linear',
  niter = 50000,
  threshold = '0.2mJy',
  weighting='briggs',
  robust=sr[i],
  interactive = T,
  imsize = [500,500],
  restoringbeam=sbeams[i],
  cell = '0.002arcsec',
  savemodel='virtual')


#spw 1  12CO
# Try R0?
os.system('rm -rf Betelgeuse_TEtavR0_12CO_200ch.image*')
tclean(vis ='Betelgeuse_TEtav_line.ms.contsub',
  imagename ='Betelgeuse_TEtavR0_12CO_200ch.image',
  spw = '1',
  specmode = 'cube',
  restfreq='345.79599GHz',
  outframe='lsrk',
  start=19,
  nchan=200,
  niter = 1000000,
  threshold = '2mJy',
  weighting='briggs',
  robust=0,
  restoringbeam=['0.0209arcsec','0.0159arcsec', '71deg'],
  interactive = T,
  imsize = [2000,2000],
  cell = '0.002arcsec')
# Beam 0.0209 0.0159 71

#spw 0
imagename = 'Betelgeuse_TEtav_spw0.image.image'
box='750,750,1249,1249'
chans='89~388'
outfile='Betelgeuse_TEtav_spw0_28SiOv1_300ch.image'

#spw 1
imagename ='Betelgeuse_TEtavR0_12CO_200ch.image.image'
box='750,750,1249,1249'
outfile='Betelgeuse_TEtav_spw1_12CO_200ch.image'

#spw 2
imagename = 'Betelgeuse_TEtav_spw2.image.image'
box='750,750,1249,1249'
chans='157~356'
outfile='Betelgeuse_TEtav_spw2_28SiOv2_300ch.image'

imagename = 'Betelgeuse_TEtav_spw2.image.image'
box='750,750,1249,1249'
chans='595~894'
outfile='Betelgeuse_TEtav_spw2_29SiOv0_300ch.image'
NOT 2

************FIX HEADERS**********
for correct rest freqs

Betelgeuse_TE_cont_spw0.image.image.tt0
Betelgeuse_TEtav_spw0_28SiOv1_300ch.image.

Betelgeuse_TE_cont_spw1.image.image.tt0

Betelgeuse_TE_cont_spw2.image.image.tt0
Betelgeuse_TEtav_spw2_28SiOv2_300ch.image
Betelgeuse_TEtav_spw2_29SiOv0_300ch.image  not 2


342.5043830E9 28SiOv2
342.9808470E9 29SiOv0 **
344.9163321E9 28SiOv1 89 28SiO(v=1, J=8-7) : 344.9163321 GHz
345.7959899E9 12COv0

342.

29SiOv=0

ims=['Betelgeuse_TEtav_spw0_28SiOv1_300ch.image','Betelgeuse_TEtav_spw2_28SiOv2_300ch.image','Betelgeuse_TEtav_spw2_29SiOv2_300ch.image']

rfrqs=['344.9163321E9Hz','342.5043830E9Hz','342.9808470E9Hz',]#,345.7959899E9]

for i in range(3):
    imhead(imagename=ims[i],mode='put',hdkey='restfreq',
           hdvalue=rfrqs[i])

for i in range(3):
    exportfits(imagename=ims[i],fitsimage=ims[i]+'.fits')
    os.system('tar -zcvf '+ims[i]+'.tgz '+ims[i])

thresh=['2mJy','1.5mJy','2mJy','2mJy','2mJy']
for s in range(5):

    os.system('rm -rf Betelgeuse_TEtav_nosub_spw'+str(s)+'.image*')
    tclean(vis ='Betelgeuse_TEtav_line.ms',
           imagename ='Betelgeuse_TEtav_nosub_spw'+str(s)+'.image',
           spw = str(s),
           specmode = 'cube',
           outframe='lsrk',
           niter = 1000000,
#           pbcor=True,
           threshold = thresh[s],
           weighting='briggs',
           robust=0.5,
           interactive = F,
           chanchunks=4,
           mask='circle[[1000pix, 1000pix],150pix]',
           imsize = [2000,2000],
           cell = '0.002arcsec',
 #          calcres=F,
 #          calcpsf=F)


Betelgeuse_TE_cont.ms
Betelgeuse_TEtav_line.ms
Betelgeuse_TEtav_line.ms.contsub

Betelgeuse_all_cont_1-1.ms
Betelgeuse_allines_*.ms.contsub



ims=['Betelgeuse_TEtavR0_12CO_200ch.image.image','Betelgeuse_TEtav_spw0_28SiOv2_200ch.image','Betelgeuse_TEtav_spw1_12CO_200ch.image','Betelgeuse_TEtav_spw2_28SiOv2_200ch.image','Betelgeuse_TEtav_spw2_29SiOv0_300ch.image']

for i in ims:
    exportfits(imagename=i,fitsimage=i+'.fits')
    os.system('tar -zcvf '+i+'.tgz '+i) 
"""
