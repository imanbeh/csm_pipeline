ms1= 'uid___A002_Xaca510_X78d.ms.split.cal'

print "clean the continuum"

clean(vis = ms1,
  imagename = ms1+'.image.cont',
  field = '3',
  spw = '0:0~190;280~958, 1:15~100;130~220, 2:0~200;300~700;800~1918, 3:5~490;580~950, 4:0~580;670~1510;1608~1910',
  mode = 'mfs',
  interpolation = 'linear',
  niter = 5000,
  selectdata=True,
  uvrange='0~10000m',
  uvtaper=T,
  outertaper='0.02arcsec',
  weighting='natural',
  restoringbeam='0.04arcsec',
  psfmode = 'clark',
  imagermode = 'csclean',
  interactive = F,
  mask = 'circle[[900pix,900pix],200pix]',
  imsize = [1800, 1800],
  cell = '0.005arcsec',
  gain = 0.1,
  threshold = '0.15mJy')

myimagebase = ms1+'.image.cont'
impbcor(imagename=myimagebase+'.image', pbimage=myimagebase+'.flux', outfile=myimagebase+'.image.pbcor', overwrite=True) # perform PBcorr
exportfits(imagename=myimagebase+'.image.pbcor', fitsimage=myimagebase+'.image.pbcor.fits') # export the corrected image
exportfits(imagename=myimagebase+'.flux', fitsimage=myimagebase+'.flux.fits') # export the PB image




print "# Subtract the continuum"

uvcontsub(vis=ms1,  
  field='3',  
  spw='',              # all spw
  fitspw='0:0~190;280~958, 1:15~100;130~220, 2:0~200;300~700;800~1918, 3:5~490;580~950, 4:0~580;670~1510;1608~1910', 
  combine='scan',
  solint='',        
  fitorder=0) 

print "# Running clean on the spw 0"

clean(vis = ms1+'.contsub',
  imagename = ms1+'.image.linesub.spw0',
  field = '0',
  spw = '0',
  mode = 'channel',
  nchan = -1,
  start = 1,
  outframe = 'lsrk',
  veltype = 'radio',
  interpolation = 'linear',
  niter = 1000,
  gain = 0.1,
  threshold = '0.008Jy',
  selectdata=True,
  uvrange='0~10000m',
  uvtaper=T,
  outertaper='0.02arcsec',
  weighting='natural',
  restoringbeam='0.04arcsec',
  psfmode = 'clark',
  imagermode = 'csclean',
  interactive = F,
  mask = 'circle[[900pix,900pix],200pix]',
  imsize = [1800, 1800],
  cell = '0.005arcsec')

myimagebase = ms1+'.image.linesub.spw0'
impbcor(imagename=myimagebase+'.image', pbimage=myimagebase+'.flux', outfile=myimagebase+'.image.pbcor', overwrite=True) # perform PBcorr
exportfits(imagename=myimagebase+'.image.pbcor', fitsimage=myimagebase+'.image.pbcor.fits') # export the corrected image
exportfits(imagename=myimagebase+'.flux', fitsimage=myimagebase+'.flux.fits') # export the PB image

print "# Running clean on the spw 1"

clean(vis = ms1+'.contsub',
  imagename = ms1+'.image.linesub.spw1',
  field = '0',
  spw = '1',
  mode = 'channel',
  nchan = -1,
  start = 1,
  outframe = 'lsrk',
  veltype = 'radio',
  interpolation = 'linear',
  niter = 1000,
  gain = 0.1,
  threshold = '0.008Jy',
  selectdata=True,
  uvrange='0~10000m',
  uvtaper=T, 
  outertaper='0.02arcsec',
  weighting='natural',
  restoringbeam='0.04arcsec',
  psfmode = 'clark',
  imagermode = 'csclean',
  interactive = F,
  mask = 'circle[[900pix,900pix],200pix]',
  imsize = [1800, 1800],
  cell = '0.005arcsec')

myimagebase = ms1+'.image.linesub.spw1'
impbcor(imagename=myimagebase+'.image', pbimage=myimagebase+'.flux', outfile=myimagebase+'.image.pbcor', overwrite=True) # perform PBcorr
exportfits(imagename=myimagebase+'.image.pbcor', fitsimage=myimagebase+'.image.pbcor.fits') # export the corrected image
exportfits(imagename=myimagebase+'.flux', fitsimage=myimagebase+'.flux.fits') # export the PB image

print "# Running clean on the spw 2"

clean(vis = ms1+'.contsub',
  imagename = ms1+'.image.linesub.spw2',
  field = '0',
  spw = '2',
  mode = 'channel',
  nchan = -1,
  start = 1,
  outframe = 'lsrk',
  veltype = 'radio',
  interpolation = 'linear',
  niter = 1000,
  gain = 0.1,
  threshold = '0.008Jy',
  selectdata=True,
  uvrange='0~10000m',
  uvtaper=T,
  outertaper='0.02arcsec',
  weighting='natural',
  restoringbeam='0.04arcsec',
  psfmode = 'clark',
  imagermode = 'csclean',
  interactive = F,
  mask = 'circle[[900pix,900pix],200pix]',
  imsize = [1800, 1800],
  cell = '0.005arcsec')

myimagebase = ms1+'.image.linesub.spw2'
impbcor(imagename=myimagebase+'.image', pbimage=myimagebase+'.flux', outfile=myimagebase+'.image.pbcor', overwrite=True) # perform PBcorr
exportfits(imagename=myimagebase+'.image.pbcor', fitsimage=myimagebase+'.image.pbcor.fits') # export the corrected image
exportfits(imagename=myimagebase+'.flux', fitsimage=myimagebase+'.flux.fits') # export the PB image

print "# Running clean on the spw 3"

clean(vis = ms1+'.contsub',
  imagename = ms1+'.image.linesub.spw3',
  field = '0',
  spw = '3',
  mode = 'channel',
  nchan = -1,
  start = 1,
  outframe = 'lsrk',
  veltype = 'radio',
  interpolation = 'linear',
  niter = 1000,
  gain = 0.1,
  threshold = '0.008Jy',
  selectdata=True,
  uvrange='0~10000m',
  uvtaper=T,
  outertaper='0.02arcsec',
  weighting='natural',
  restoringbeam='0.04arcsec',
  psfmode = 'clark',
  imagermode = 'csclean',
  interactive = F,
  mask = 'circle[[900pix,900pix],200pix]',
  imsize = [1800, 1800],
  cell = '0.005arcsec')

myimagebase = ms1+'.image.linesub.spw3'
impbcor(imagename=myimagebase+'.image', pbimage=myimagebase+'.flux', outfile=myimagebase+'.image.pbcor', overwrite=True) # perform PBcorr
exportfits(imagename=myimagebase+'.image.pbcor', fitsimage=myimagebase+'.image.pbcor.fits') # export the corrected image
exportfits(imagename=myimagebase+'.flux', fitsimage=myimagebase+'.flux.fits') # export the PB image

print "# Running clean on the spw 4"

clean(vis = ms1+'.contsub',
  imagename = ms1+'.image.linesub.spw4',
  field = '0',
  spw = '4',
  mode = 'channel',
  nchan = -1,
  start = 1,
  outframe = 'lsrk',
  veltype = 'radio',
  interpolation = 'linear',
  niter = 1000,
  gain = 0.1,
  threshold = '0.008Jy',
  selectdata=True,
  uvrange='0~10000m',
  uvtaper=T,
  outertaper='0.02arcsec',
  weighting='natural',
  restoringbeam='0.04arcsec',
  psfmode = 'clark',
  imagermode = 'csclean',
  interactive = F,
  mask = 'circle[[900pix,900pix],200pix]',
  imsize = [1800, 1800],
  cell = '0.005arcsec')

myimagebase = ms1+'.image.linesub.spw4'
impbcor(imagename=myimagebase+'.image', pbimage=myimagebase+'.flux', outfile=myimagebase+'.image.pbcor', overwrite=True) # perform PBcorr
exportfits(imagename=myimagebase+'.image.pbcor', fitsimage=myimagebase+'.image.pbcor.fits') # export the corrected image
exportfits(imagename=myimagebase+'.flux', fitsimage=myimagebase+'.flux.fits') # export the PB image

