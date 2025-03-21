import re

ms2='calibrated_cont_shift.ms'

flagdata(vis=ms2, antenna='DV03', spw='4', mode='manual')
flagdata(vis=ms2, antenna='DA49&DV20;DV20&PM03', spw='3', mode='manual')
flagdata(vis=ms2, antenna='DV20', spw='1', mode='manual')

clearcal(ms2)
spwmap = [0,0,0,0,0]
plotms(vis = ms2, spw=spw, xaxis = 'uvdist', yaxis = 'real', ydatacolumn = 'corrected', selectdata = True, avgchannel= '999999', avgtime='99999', avgscan=True, coloraxis='spw', plotfile='sc0_real_uvdist.png')

print "clean the continuum using interactive clean"

clean(vis = ms2,
  imagename = ms2+'.image',
  spw = '',
  mode = 'mfs',
  interpolation = 'linear',
  niter = 50000,
  nterms = 2,
  selectdata=True,
  psfmode = 'clark',
  imagermode = 'csclean',
  gain = 0.1,
  threshold = '3.0mJy',
  usescratch=True,
  weighting='briggs',
  robust=0.5,
  interactive = F,
  mask = 'Aori.mask',
  imsize = [450, 450],
  cell = '0.002arcsec')

print "First round of phase-only self-cal"
gaincal(vis=ms2,
  caltable='Aori_X78d_cal_pcal0',gaintype='T',
  refant='DV19',calmode='p',combine='',
  solint='inf',minsnr=3.0,minblperant=6)

## Check the solution
#plotcal(caltable='Aori_X78d_cal_pcal0', xaxis='time', yaxis='phase', timerange='', iteration='antenna', subplot=421, plotrange=[0,0,-180,180])

print "Apply the solutions"
applycal(vis=ms2,spwmap=[spwmap],spw='', field='',
  gaintable=['Aori_X78d_cal_pcal0'],calwt=F,flagbackup=F)

plotms(vis = ms2, spw=spw, xaxis = 'uvdist', yaxis = 'real', ydatacolumn = 'corrected', selectdata = True, avgchannel= '999999', avgtime='99999', avgscan=True, coloraxis='spw', plotfile='sc1_real_uvdist.png')

clean(vis = ms2,
  imagename = ms2+'.image.sc0.cont',
  spw = '',
  mode = 'mfs',
  interpolation = 'linear',
  niter = 50000,
  nterms = 2,
  selectdata=True,
  psfmode = 'clark',
  imagermode = 'csclean',
  gain = 0.1,
  threshold = '1.0mJy',
  usescratch=True,
  weighting='briggs',
  robust = 0.5,
  interactive = F,
  mask = 'Aori.mask',
  imsize = [450, 450],
  cell = '0.002arcsec')

print "Second round of phase-only self-cal"
gaincal(vis=ms2,
  caltable='Aori_X78d_cal_pcal1',gaintype='T',
  refant='DV19',calmode='p',combine='',
  solint='45s',minsnr=3.0,minblperant=6)

## Check the solution
##plotcal(caltable='Aori_X78d_cal_pcal1', xaxis='time', yaxis='phase', timerange='', iteration='antenna', subplot=421, plotrange=[0,0,-180,180])

print "Apply the solutions"
applycal(vis=ms2,spwmap=[spwmap],spw='', field='',
  gaintable=['Aori_X78d_cal_pcal1'],calwt=F,flagbackup=F)

plotms(vis = ms2, spw=spw, xaxis = 'uvdist', yaxis = 'real', ydatacolumn = 'corrected', selectdata = True, avgchannel= '999999', avgtime='99999', avgscan=True, coloraxis='spw', plotfile='sc2_real_uvdist.png')

clean(vis = ms2,
  imagename = ms2+'.image.sc1.cont',
  spw = '',
  mode = 'mfs',
  interpolation = 'linear',
  niter = 50000,
  nterms = 2,
  selectdata=True,
  psfmode = 'clark',
  imagermode = 'csclean',
  gain = 0.1,
  threshold = '0.5mJy',
  usescratch=True,
  weighting='briggs',
  robust=0.5,
  interactive = F,
  mask = 'Aori.mask',
  imsize = [450, 450],
  cell = '0.002arcsec')


print "Third round of phase-only self-cal"
gaincal(vis=ms2,
  caltable='Aori_X78d_cal_pcal2',gaintype='T',
  refant='DV19',calmode='p',combine='',
  solint='15s',minsnr=3.0,minblperant=6)

# Check the solution
#plotcal(caltable='Aori_X78d_cal_pcal2', xaxis='time', yaxis='phase', timerange='', iteration='antenna', subplot=421, plotrange=[0,0,-180,180])

print "Apply the solutions"
applycal(vis=ms2,spwmap=[spwmap],spw='', field='',
  gaintable=['Aori_X78d_cal_pcal2'],calwt=F,flagbackup=F)

plotms(vis = ms2, spw=spw, xaxis = 'uvdist', yaxis = 'real', ydatacolumn = 'corrected', selectdata = True, avgchannel= '999999', avgtime='99999', avgscan=True, coloraxis='spw', plotfile='sc3_real_uvdist.png')

clean(vis = ms2,
  imagename = ms2+'.image.sc2.cont',
  spw = '',
  mode = 'mfs',
  interpolation = 'linear',
  niter = 50000,
  nterms = 2,
  selectdata=True,
  psfmode = 'clark',
  imagermode = 'csclean',
  gain = 0.1,
  threshold = '0.3mJy',
  usescratch=True,
  weighting='briggs',
  robust=0.5,
  interactive = F,
  mask = 'Aori.mask',
  imsize = [450, 450],
  cell = '0.002arcsec')

print "Amplitude calibration"
gaincal(vis=ms2,
  caltable='apcal',
  gaintype='T',
  refant='DV19',
  calmode='ap',
  solint='inf',
  minsnr=3.0,
  minblperant=6,
  gaintable='Aori_X78d_cal_pcal2',
  spwmap=spwmap,
  solnorm=True)

#plotcal(caltable='apcal',xaxis='time',yaxis='amp',timerange='', spw='',iteration='antenna',subplot=421,plotrange=[0,0,0.4,1.6])

applycal(vis=ms2,
  spwmap=[spwmap,spwmap], # select which spws to apply the solutions for each table
  gaintable=['Aori_X78d_cal_pcal2','apcal'],
  gainfield='',
  calwt=F,
  flagbackup=F)

plotms(vis = ms2, spw=spw, xaxis = 'uvdist', yaxis = 'real', ydatacolumn = 'corrected', selectdata = True, avgchannel= '999999', avgtime='99999', avgscan=True, coloraxis='spw', plotfile='sc4_real_uvdist.png')

clean(vis = ms2,
  imagename = ms2+'.image.ap.cont',
  spw = '',
  mode = 'mfs',
  interpolation = 'linear',
  niter = 50000,
  nterms = 2,
  selectdata=True,
  psfmode = 'clark',
  imagermode = 'csclean',
  gain = 0.1,
  threshold = '0.15mJy',
  usescratch=True,
  weighting='briggs',
  robust=0.5,
  interactive = F,
  mask = 'Aori.mask',
  imsize = [450, 450],
  cell = '0.002arcsec')

