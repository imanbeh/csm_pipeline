vis0='uid___A002_Xb6d0c2_X4e01.ms.split.cal'

spws=[0,1,2,3,4]
cwds=[8,16,16,16,16]
contcata=[]

os.system('rm -rf X200.fxvs')
fixvis(vis=vis0,field='Betelgeuse', outputvis='X200.fxvs', phasecenter='J2000 05h55m10.331s 07d24m25.571s')

for s in spws:
    os.system('rm -rf X200_spw'+str(s)+'.ms'),
    mstransform(vis='X200.fxvs',
                outputvis='X200_spw'+str(s)+'.ms',
                field='Betelgeuse',
                spw=str(s),
                datacolumn='data',
                regridms=T,
                width=cwds[s])
    contcata.append('X200_spw'+str(s)+'.ms')

os.system('rm -rf Betelgeuse_TC_cont.ms')
concat(vis=contcata,
       concatvis='Betelgeuse_TC_cont.ms',
       freqtol='2MHz',
       dirtol='1arcsec')

***********DIFFERNT NUMBERING aargh check
contchansavg='0:0~10;18~23,1:4~9;24~59,2:25~39;59~119,3:0~28;42~59,4:0~37;41~68;88~97;100~119'

#LINE
linecata=[]

for s in spws:
    os.system('rm -rf X200_spw'+str(s)+'L.ms')
    mstransform(vis='X200.fxvs',
                outputvis='X200_spw'+str(s)+'L.ms',
                field='Betelgeuse',
                spw=str(s),
                datacolumn='data',
                outframe='lsrk',
                regridms=T)
    linecata.append('X200_spw'+str(s)+'L.ms')

os.system('rm -rf Betelgeuse_TC_line.ms')
concat(vis=linecata,
       concatvis='Betelgeuse_TC_line.ms',
       dirtol='1arcsec')

#######################
os.system('rm -rf Betelgeuse_TC_cont.image*')
tclean(vis ='Betelgeuse_TC_cont.ms',
  imagename ='Betelgeuse_TC_cont.image',
  spw = contchansavg,
  specmode = 'mfs',
  interpolation = 'linear',
  niter = 100,
  threshold = '0.3mJy',
  weighting='briggs',
  robust=0.5,
  interactive = T,
  imsize = [300,300],
  cell = '0.03arcsec',
  savemodel='virtual')
#S/N 2.573192e-01/1.866166e-03  137

ft(vis='Betelgeuse_TC_cont.ms',
   model='Betelgeuse_TC_cont.image.model')

os.system('rm -rf Betelgeuse_TC_cont.p1')
gaincal(vis ='Betelgeuse_TC_cont.ms',
        caltable='Betelgeuse_TC_cont.p1',
        spw=contchansavg,
        calmode='p',
        refant='DA49',
        solint='inf')

applycal(vis ='Betelgeuse_TC_cont.ms',
         gaintable='Betelgeuse_TC_cont.p1',
         applymode='calonly',
         calwt=False)

os.system('rm -rf Betelgeuse_TC_contp1.image*')
tclean(vis ='Betelgeuse_TC_cont.ms',
  imagename ='Betelgeuse_TC_contp1.image',
  spw = contchansavg,
  specmode = 'mfs',
  deconvolver='mtmfs',
  nterms=2,
  interpolation = 'linear',
  niter = 1000,
  threshold = '0.03mJy',
  weighting='briggs',
  robust=0.5,
  interactive = T,
  imsize = [300,300],
  cell = '0.03arcsec',
  savemodel='virtual')
# S/N 2.528105e-01/4.317704e-04 585
##

### amp

ft(vis='Betelgeuse_TC_cont.ms',
   nterms=2,
   model=['Betelgeuse_TC_contp1.image.model.tt0','Betelgeuse_TC_contp1.image.model.tt1'])

os.system('rm -rf Betelgeuse_TC_cont.a1')
gaincal(vis ='Betelgeuse_TC_cont.ms',
        caltable='Betelgeuse_TC_cont.a1',
        spw=contchansavg,
        refant='DA49',
        solint='inf',
        gaintable='Betelgeuse_TC_cont.p1')

applycal(vis ='Betelgeuse_TC_cont.ms',
         gaintable=['Betelgeuse_TC_cont.a1','Betelgeuse_TC_cont.p1'],
         applymode='calonly',
         calwt=False)

os.system('rm -rf Betelgeuse_TC_contap1.image*')
tclean(vis ='Betelgeuse_TC_cont.ms',
  imagename ='Betelgeuse_TC_contap1.image',
  spw = contchansavg,
  specmode = 'mfs',
  deconvolver='mtmfs',
  nterms=2,
  interpolation = 'linear',
  niter = 1000,
  threshold = '0.03mJy',
  weighting='briggs',
  robust=0.5,
  interactive = T,
  imsize = [300,300],
  cell = '0.03arcsec',
  savemodel='virtual')
# S/N 2.528105e-01/4.328816e-04 584.0176621043721
##
# try ap with shorter solint?


ft(vis='Betelgeuse_TC_cont.ms',
   nterms=2,
   model=['Betelgeuse_TC_contap1.image.model.tt0','Betelgeuse_TC_contap1.image.model.tt1'])

os.system('rm -rf Betelgeuse_TC_cont.ap2')
gaincal(vis ='Betelgeuse_TC_cont.ms',
        caltable='Betelgeuse_TC_cont.ap2',
        spw=contchansavg,
        refant='DA49',
        solint='30s',
        gaintable=['Betelgeuse_TC_cont.a1','Betelgeuse_TC_cont.p1'])

applycal(vis ='Betelgeuse_TC_cont.ms',
         gaintable=['Betelgeuse_TC_cont.ap2','Betelgeuse_TC_cont.a1','Betelgeuse_TC_cont.p1'],
         applymode='calonly',
         calwt=False)

os.system('rm -rf Betelgeuse_TC_contap2.image*')
tclean(vis ='Betelgeuse_TC_cont.ms',
  imagename ='Betelgeuse_TC_contap2.image',
  spw = contchansavg,
  specmode = 'mfs',
  deconvolver='mtmfs',
  nterms=2,
  interpolation = 'linear',
  niter = 1000,
  threshold = '0.03mJy',
  weighting='briggs',
  robust=0.5,
  interactive = T,
  imsize = [300,300],
  cell = '0.03arcsec',
  savemodel='virtual')
#3.352876e-01/2.515584e-04  1332.841996132906

flagmanager(vis ='Betelgeuse_TC_cont.ms',
            mode='save',
            versionname='preapplyap2')


applycal(vis ='Betelgeuse_TC_cont.ms',
         gaintable=['Betelgeuse_TC_cont.ap2','Betelgeuse_TC_cont.a1','Betelgeuse_TC_cont.p1'],
         applymode='calflag',
         calwt=True)

os.system('rm -rf Betelgeuse_TC_contap2_wt.image*')
tclean(vis ='Betelgeuse_TC_cont.ms',
  imagename ='Betelgeuse_TC_contap2_wt.image',
  spw = contchansavg,
  specmode = 'mfs',
  deconvolver='mtmfs',
  nterms=2,
  interpolation = 'linear',
  niter = 1000,
  threshold = '0.03mJy',
  weighting='briggs',
  robust=0.5,
  interactive = T,
  imsize = [300,300],
  cell = '0.03arcsec',
  savemodel='virtual')
#3.309371e-01/ 2.679652e-04 1235  beam 0".20x0".17
# marginally worse but sideobes slightly better

# apply to line

applycal(vis ='Betelgeuse_TC_line.ms',
         gaintable=['Betelgeuse_TC_cont.ap2','Betelgeuse_TC_cont.a1','Betelgeuse_TC_cont.p1'],
         spw='0,1,2,3,4',
         spwmap=[[0,1,2,3,4],[0,1,2,3,4],[0,1,2,3,4]],
         applymode='calflag',
         calwt=True)

# Examine in plotms

contchline='0:0~100;140~239,1:0~160;300~959,2:1~160;465~650;1070~1919,3:0~440;540~958,4:0~530;900~1919'

#subtract continuum
os.system('rm -rf Betelgeuse_TC_line.ms.contsub')
uvcontsub3(vis ='Betelgeuse_TC_line.ms',
          combine='spw',
          fitspw=contchline,
          fitorder=1)

# image line
# 12CO spw 0
os.system('rm -rf Betelgeuse_TC_12CO.image*')
tclean(vis ='Betelgeuse_TC_line.ms.contsub',
  imagename ='Betelgeuse_TC_12CO.image',
  spw = '0',
  specmode = 'cube',
  restfreq='345.79599GHz',
  outframe='lsrk',
  start=100,
  nchan=41,
  niter = 1000000,
  threshold = '2mJy',
  weighting='briggs',
  robust=0.5,
  interactive = T,
  imsize = [800,800],
  cell = '0.03arcsec')
# rms off-peak 1 mJy/bm

# forgot to make pbcor images, catch-up!
impbcor(imagename='Betelgeuse_TC_cont.image.image',
        pbimage='Betelgeuse_TC_cont.image.pb',
        outfile='Betelgeuse_TC_cont.image.image.pbcor')

impbcor(imagename='Betelgeuse_TC_contap2_wt.image.image.tt0',
        pbimage='Betelgeuse_TC_contap2_wt.image.pb.tt0',
        outfile='Betelgeuse_TC_contap2_wt.image.image.tt0.pbcor')

impbcor(imagename='Betelgeuse_TC_12CO.image.image',
        pbimage='Betelgeuse_TC_12CO.image.pb',
        outfile='Betelgeuse_TC_12CO.image.image.pbcor')
###################
# spw1
os.system('rm -rf Betelgeuse_TC_SO2.image*')
tclean(vis ='Betelgeuse_TC_line.ms.contsub',
  imagename ='Betelgeuse_TC_SO2.image',
  spw = '1',
  specmode = 'cube',
  restfreq='345.1489708GHz',
  outframe='lsrk',
  start=175,
  nchan=101,
  niter = 1000000,
  pbcor=True,
  threshold = '3mJy',
  weighting='briggs',
  robust=0.5,
  interactive = F,
  mask='circle[[400pix, 400pix],100pix]',
  imsize = [800,800],
  cell = '0.03arcsec')

os.system('mv Betelgeuse_TC_SO2.image.mask  Betelgeuse_TC_SO2.image.mask200')
tclean(vis ='Betelgeuse_TC_line.ms.contsub',
  imagename ='Betelgeuse_TC_SO2.image',
  spw = '1',
  specmode = 'cube',
  restfreq='345.1489708GHz',
  outframe='lsrk',
  start=175,
  nchan=101,
  niter = 1000000,
  pbcor=True,
  threshold = '3mJy',
  weighting='briggs',
  robust=0.5,
#  interactive = T,
  mask='circle[[400pix, 400pix],380pix]',
  imsize = [800,800],
  cell = '0.03arcsec',
  calcpsf=False,
  calcres=False)
# rms off-peak  mJy/bm

###################
# 29SiO spw2
os.system('rm -rf Betelgeuse_TC_29SiO.image*')
tclean(vis ='Betelgeuse_TC_line.ms.contsub',
  imagename ='Betelgeuse_TC_29SiO.image',
  spw = '2',
  specmode = 'cube',
  restfreq='342.980848GHz',
  outframe='lsrk',
  start=695,
  nchan=101,
  niter = 1000000,
  pbcor=True,
  threshold = '3mJy',
  weighting='briggs',
  robust=0.5,
  interactive = F,
  mask='circle[[400pix, 400pix],100pix]',
  imsize = [800,800],
  cell = '0.03arcsec')

##################
# 13CO spw3
os.system('rm -rf Betelgeuse_TC_13CO.image*')
tclean(vis ='Betelgeuse_TC_line.ms.contsub',
  imagename ='Betelgeuse_TC_13CO.image',
  spw = '3',
  specmode = 'cube',
  restfreq='330.5879653GHz',
  outframe='lsrk',
  start=440,
  nchan=101,
  niter = 1000000,
  pbcor=True,
  threshold = '3mJy',
  weighting='briggs',
  robust=0.5,
#  interactive = T,
  mask='circle[[400pix, 400pix],100pix]',
  imsize = [800,800],
  cell = '0.03arcsec')

os.system('mv Betelgeuse_TC_13CO.image.mask  Betelgeuse_TC_13CO.image.mask200')
tclean(vis ='Betelgeuse_TC_line.ms.contsub',
  imagename ='Betelgeuse_TC_13CO.image',
  spw = '3',
  specmode = 'cube',
  restfreq='330.5879653GHz',
  outframe='lsrk',
  start=440,
  nchan=101,
  niter = 1000000,
  pbcor=True,
  threshold = '3mJy',
  weighting='briggs',
  robust=0.5,
#  interactive = T,
  mask='circle[[400pix, 400pix],380pix]',
  imsize = [800,800],
  cell = '0.03arcsec',
  calcpsf=False,
  calcres=False)
# rms off-peak  mJy/bm




#######
# per spw
###################
thresh=['2mJy','3mJy','3mJy','3mJy','3mJy']
for s in range(5):
#    s=4
    os.system('rm -rf Betelgeuse_TC_spw'+str(s)+'.image*')
    tclean(vis ='Betelgeuse_TC_line.ms.contsub',
           imagename ='Betelgeuse_TC_spw'+str(s)+'.image',
           spw = str(s),
           specmode = 'cube',
           outframe='lsrk',
           niter = 1000000,
           pbcor=True,
           threshold = thresh[s],
           weighting='briggs',
           robust=0.5,
           interactive = F,
           mask='circle[[400pix, 400pix],100pix]',
           imsize = [800,800],
           cell = '0.03arcsec')

    os.system('mv Betelgeuse_TC_spw'+str(s)+'.image.mask  Betelgeuse_TC_spw'+str(s)+'.image.mask200')
    tclean(vis ='Betelgeuse_TC_line.ms.contsub',
           imagename ='Betelgeuse_TC_spw'+str(s)+'.image',
           spw = str(s),
           specmode = 'cube',
           outframe='lsrk',
           niter = 1000000,
           pbcor=True,
           threshold = thresh[s],
           weighting='briggs',
           robust=0.5,
           #  interactive = T,
           mask='circle[[400pix, 400pix],380pix]',
           imsize = [800,800],
           cell = '0.03arcsec',
           calcpsf=False,
           calcres=False)
# rms off-peak  mJy/bm

###################




Betelgeuse
==============

cubes1=['Betelgeuse_TC_cont.image.image','Betelgeuse_TC_cont.image.image.pbcor','Betelgeuse_TC_contap2_wt.image.image.tt0','Betelgeuse_TC_contap2_wt.image.image.tt0.pbcor','Betelgeuse_TC_12CO.image.image','Betelgeuse_TC_12CO.image.image.pbcor','Betelgeuse_TC_13CO.image.image','Betelgeuse_TC_13CO.image.image.pbcor','Betelgeuse_TC_29SiO.image.image','Betelgeuse_TC_29SiO.image.image.pbcor']

allcubes=['Betelgeuse_TC_spw0.image.image','Betelgeuse_TC_spw0.image.image.pbcor','Betelgeuse_TC_spw1.image.image','Betelgeuse_TC_spw1.image.image.pbcor','Betelgeuse_TC_spw2.image.image','Betelgeuse_TC_spw2.image.image.pbcor','Betelgeuse_TC_spw3.image.image','Betelgeuse_TC_spw3.image.image.pbcor','Betelgeuse_TC_spw4.image.image','Betelgeuse_TC_spw4.image.image.pbcor']

for c in cubes1:
    exportfits(imagename=c,fitsimage=c+'.fits')
    os.system('tar -zcvf '+c+'.tgz '+c)

for c in allcubes:
    exportfits(imagename=c,fitsimage=c+'.fits')
    os.system('tar -zcvf '+c+'.tgz '+c)

==================
# Betelgeuse_TE_cont_ap1.image.image.tt0
# Fit by eye to outer 25mJy contour (Gaussian fit is biased by hot spot)
# use ellipse, get centre from region manager in pixels (directly in
# radians insufficient precision)
# TE 05:55:10.3315, 07:24:25.565
# TE centre   1.549731039026925, 0.12927830726515604
# TC 05:55:10.335149, 07.24.25.532869  (imfit)
# TC centre 1.5497313043896932, 0.12927815148967217

# Current phase centre is
aU.radec2rad('J2000 05h55m10.331s 07d24m25.571s')
ph_c= 1.5497310026658988, 0.12927833635397692

dTC=dTE=ph_c - TE centre =  -3.6361e-08, 2.9089e-08

Need to shift by TC-TE =  2.6536276820365856e-07,-1.5577548387324391e-07

os.system('rm -rf Betelgeuse_TC_cont_shift.ms')
os.system('cp -r Betelgeuse_TC_cont.ms Betelgeuse_TC_cont_shift.ms')

inpms='Betelgeuse_TC_cont_shift.ms'
tb.open(inpms+'/FIELD')
pdin=tb.getcol('PHASE_DIR')
tb.close

a=pdin[0][0][0]
d=pdin[1][0][0]
# just to check

da=2.6536276820365856e-07
dd=-1.5577548387324391e-07

dpd= [[[da]], [[dd]]]

inpms='Betelgeuse_TC_cont_shift.ms'
tb.open(inpms+'/FIELD',nomodify=False)
pdin=tb.getcol('PHASE_DIR')
pdnew=pdin-dpd
tb.putcol('PHASE_DIR',pdnew)
pdin=tb.getcol('REFERENCE_DIR')
pdnew=pdin-dpd
tb.putcol('REFERENCE_DIR',pdnew)
tb.close()


# now shift the visibilties so both data sets have same
# reference again

inpms='Betelgeuse_TE_cont.ms'
tb.open(inpms+'/FIELD')
ref=tb.getcol('PHASE_DIR')
tb.close

os.system('rm -rf Betelgeuse_TC_cont_shiftfix.ms')
fixvis(vis='Betelgeuse_TC_cont_shift.ms',
       outputvis='Betelgeuse_TC_cont_shiftfix.ms',
       phasecenter='J2000 '+str(ref[0][0][0])+'rad '+ str(ref[1][0][0])+'rad')


#check # nb cellsize
os.system('rm -rf Betelgeuse_TC_shift.image*')
tclean(vis ='Betelgeuse_TC_cont_shiftfix.ms',
  imagename ='Betelgeuse_TC_shift.image',
  spw = contchansavg,
  specmode = 'mfs',
  deconvolver='mtmfs',
  nterms=2,
  interpolation = 'linear',
  niter = 1000,
  threshold = '0.03mJy',
  weighting='briggs',
  robust=0.5,
  interactive = T,
  imsize = [300,300],
  cell = '0.005arcsec')


START HERE
### Repeat for line
os.system('rm -rf Betelgeuse_TC_line_shift.ms.contsub')
os.system('cp -r Betelgeuse_TC_line.ms.contsub Betelgeuse_TC_line_shift.ms.contsub')

inpms='Betelgeuse_TC_line_shift.ms.contsub'
tb.open(inpms+'/FIELD')
pdin=tb.getcol('PHASE_DIR')
tb.close

a=pdin[0][0][0]
d=pdin[1][0][0]
# just to check

da=2.6536276820365856e-07
dd=-1.5577548387324391e-07

dpd= [[[da]], [[dd]]]

inpms='Betelgeuse_TC_line_shift.ms.contsub'
tb.open(inpms+'/FIELD',nomodify=False)
pdin=tb.getcol('PHASE_DIR')
pdnew=pdin-dpd
tb.putcol('PHASE_DIR',pdnew)
pdin=tb.getcol('REFERENCE_DIR')
pdnew=pdin-dpd
tb.putcol('REFERENCE_DIR',pdnew)
tb.close()

os.system('rm -rf Betelgeuse_TC_lnshift.image*')
tclean(vis ='Betelgeuse_TC_line_shiftfix.ms.contsub',
  imagename ='Betelgeuse_TC_lnshift.image',
  specmode = 'cube',
  spw='0',
  start=115,
  nchan=10,
  interpolation = 'linear',
  niter = 1000,
  threshold = '0.03mJy',
  weighting='briggs',
  robust=0.5,
  interactive = T,
  imsize = [300,300],
  cell = '0.005arcsec')


# now shift the visibilties so both data sets have same
# reference again

inpms='Betelgeuse_TEtav_line.ms.contsub'
tb.open(inpms+'/FIELD')
ref=tb.getcol('PHASE_DIR')
tb.close

os.system('rm -rf Betelgeuse_TC_line_shiftfix.ms.contsub')
fixvis(vis='Betelgeuse_TC_line_shift.ms.contsub',
       outputvis='Betelgeuse_TC_line_shiftfix.ms.contsub',
       phasecenter='J2000 '+str(ref[0][0][0])+'rad '+ str(ref[1][0][0])+'rad')

####

Also need to rescale by 600/420?
uvmod script 
1.428  
Betelgeuse_TC_cont_shfxscl.ms
