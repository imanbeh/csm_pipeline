# ALMA Data Reduction Script

# Calibration

thesteps = [15,16,17,18,19]
step_title = {0: 'Import of the ASDM',
              1: 'Fix of SYSCAL table times',
              2: 'listobs',
              3: 'A priori flagging',
              4: 'Generation and time averaging of the WVR cal table',
              5: 'Generation of the Tsys cal table',
              6: 'Generation of the antenna position cal table',
              7: 'Application of the WVR, Tsys and antpos cal tables',
              8: 'Split out science SPWs and time average',
              9: 'Listobs, and save original flags',
              10: 'Initial flagging',
              11: 'Putting a model for the flux calibrator(s)',
              12: 'Save flags before bandpass cal',
              13: 'Bandpass calibration',
              14: 'Save flags before gain cal',
              15: 'Gain calibration',
              16: 'Save flags before applycal',
              17: 'Application of the bandpass and gain cal tables',
              18: 'Split out corrected column',
              19: 'Save flags after applycal'}

if 'applyonly' not in globals(): applyonly = False
try:
  print 'List of steps to be executed ...', mysteps
  thesteps = mysteps
except:
  print 'global variable mysteps not set.'
if (thesteps==[]):
  thesteps = range(0,len(step_title))
  print 'Executing all steps: ', thesteps

# The Python variable 'mysteps' will control which steps
# are executed when you start the script using
#   execfile('scriptForCalibration.py')
# e.g. setting
#   mysteps = [2,3,4]# before starting the script will make the script execute
# only steps 2, 3, and 4
# Setting mysteps = [] will make it execute all steps.

import re

import os

if applyonly != True: es = aU.stuffForScienceDataReduction() 


#if re.search('^4.5.0', casadef.casa_version) == None:
# sys.exit('ERROR: PLEASE USE THE SAME VERSION OF CASA THAT YOU USED FOR GENERATING THE SCRIPT: 4.5.0')


# CALIBRATE_AMPLI: 
# CALIBRATE_ATMOSPHERE: Betelgeuse,J0510+1800,J0552+0313
# CALIBRATE_BANDPASS: J0510+1800
# CALIBRATE_FLUX: J0510+1800
# CALIBRATE_FOCUS: 
# CALIBRATE_PHASE: J0552+0313
# CALIBRATE_POINTING: J0510+1800
# OBSERVE_CHECK: J0605+0939
# OBSERVE_TARGET: Betelgeuse

# Using reference antenna = DV19

# Import of the ASDM
mystep = 0
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  if os.path.exists('uid___A002_Xaca510_X78d.ms') == False:
    importasdm('uid___A002_Xaca510_X78d', asis='Antenna Station Receiver Source CalAtmosphere CalWVR CorrelatorMode SBSummary', bdfflags=True, lazy=False, process_caldevice=False)
  if applyonly != True: es.fixForCSV2555('uid___A002_Xaca510_X78d.ms')

# Fix of SYSCAL table times
mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  from recipes.almahelpers import fixsyscaltimes
  fixsyscaltimes(vis = 'uid___A002_Xaca510_X78d.ms')

print "# A priori calibration"

# listobs
mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaca510_X78d.ms.listobs')
  listobs(vis = 'uid___A002_Xaca510_X78d.ms',
    listfile = 'uid___A002_Xaca510_X78d.ms.listobs')
  
  

# A priori flagging
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  flagdata(vis = 'uid___A002_Xaca510_X78d.ms',
    mode = 'manual',
    spw = '5~12,17~34',
    autocorr = T,
    flagbackup = F)
  
  flagdata(vis = 'uid___A002_Xaca510_X78d.ms',
    mode = 'manual',
    intent = '*POINTING*,*ATMOSPHERE*',
    flagbackup = F)
  
  flagcmd(vis = 'uid___A002_Xaca510_X78d.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'plot',
    plotfile = 'uid___A002_Xaca510_X78d.ms.flagcmd.png')
  
  flagcmd(vis = 'uid___A002_Xaca510_X78d.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'apply')
  

# Generation and time averaging of the WVR cal table
mystep = 4
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaca510_X78d.ms.wvr') 
  
  os.system('rm -rf uid___A002_Xaca510_X78d.ms.wvrgcal') 
  
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_Xaca510_X78d.ms.wvrgcal')
  
  wvrgcal(vis = 'uid___A002_Xaca510_X78d.ms',
    caltable = 'uid___A002_Xaca510_X78d.ms.wvr',
    spw = [25, 27, 29, 31, 33],
    smooth = '2.016s',
    toffset = 0,
    tie = ['J0605+0939,J0552+0313', 'Betelgeuse,J0552+0313'],
    statsource = 'Betelgeuse')
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: aU.plotWVRSolutions(caltable='uid___A002_Xaca510_X78d.ms.wvr', spw='25', antenna='DV19',
    yrange=[-199,199],subplot=22, interactive=False,
    figfile='uid___A002_Xaca510_X78d.ms.wvr.plots/uid___A002_Xaca510_X78d.ms.wvr') 
  
  #Note: If you see wraps in these plots, try changing yrange or unwrap=True 
  #Note: If all plots look strange, it may be a bad WVR on the reference antenna.
  #      To check, you can set antenna='' to show all baselines.
  

# Generation of the Tsys cal table
mystep = 5
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaca510_X78d.ms.tsys') 
  gencal(vis = 'uid___A002_Xaca510_X78d.ms',
    caltable = 'uid___A002_Xaca510_X78d.ms.tsys',
    caltype = 'tsys')
  
  # Flagging edge channels
  
  flagdata(vis = 'uid___A002_Xaca510_X78d.ms.tsys',
    mode = 'manual',
    spw = '17:0~3;124~127,19:0~3;124~127,21:0~3;124~127,23:0~3;124~127',
    flagbackup = F)
  
  if applyonly != True: aU.plotbandpass(caltable='uid___A002_Xaca510_X78d.ms.tsys', overlay='time', 
    xaxis='freq', yaxis='amp', subplot=22, buildpdf=False, interactive=False,
    showatm=True,pwv='auto',chanrange='92.1875%',showfdm=True, showBasebandNumber=True, showimage=False, 
    field='', figfile='uid___A002_Xaca510_X78d.ms.tsys.plots.overlayTime/uid___A002_Xaca510_X78d.ms.tsys') 
  
  
  if applyonly != True: es.checkCalTable('uid___A002_Xaca510_X78d.ms.tsys', msName='uid___A002_Xaca510_X78d.ms', interactive=False) 
  

# Generation of the antenna position cal table
mystep = 6
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Position for antenna DV12 is derived from baseline run made on 2015-11-08 11:41:22.
  
  # Note: the correction for antenna DA61 is larger than 2mm.
  
  # Position for antenna DA61 is derived from baseline run made on 2015-11-02 04:20:45.
  
  # Note: the correction for antenna PM03 is larger than 2mm.
  
  # Position for antenna PM03 is derived from baseline run made on 2015-11-02 04:20:45.
  
  # Note: the correction for antenna PM04 is larger than 2mm.
  
  # Position for antenna PM04 is derived from baseline run made on 2015-11-02 04:20:45.
  
  # Position for antenna DV19 is derived from baseline run made on 2015-11-02 04:20:45.
  
  # Note: no baseline run found for antenna DV02.
  
  # Position for antenna DV16 is derived from baseline run made on 2015-11-02 04:20:45.
  
  # Position for antenna DV13 is derived from baseline run made on 2015-11-08 11:41:22.
  
  os.system('rm -rf uid___A002_Xaca510_X78d.ms.antpos') 
  gencal(vis = 'uid___A002_Xaca510_X78d.ms',
    caltable = 'uid___A002_Xaca510_X78d.ms.antpos',
    caltype = 'antpos',
    antenna = 'DA61,DV12,DV13,DV16,DV19,PM03,PM04',
  #  parameter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    parameter = [9.96864e-04,-2.17635e-03,-4.92317e-04,-1.99738e-04,-3.09171e-05,-1.24390e-04,1.33581e-04,-7.59771e-04,1.52911e-04,3.43088e-04,3.70879e-04,-5.56884e-04,2.56176e-04,-8.58465e-04,-1.84210e-04,1.00564e-02,-4.45706e-03,-2.30534e-04,6.52816e-04,-1.62950e-03,-2.60157e-03])
  
  
  # antenna x_offset y_offset z_offset total_offset baseline_date
  # PM03     1.00564e-02   -4.45706e-03   -2.30534e-04    1.10022e-02      2015-11-02 04:20:45
  # PM04     6.52816e-04   -1.62950e-03   -2.60157e-03    3.13841e-03      2015-11-02 04:20:45
  # DA61     9.96864e-04   -2.17635e-03   -4.92317e-04    2.44389e-03      2015-11-02 04:20:45
  # DV19     2.56176e-04   -8.58465e-04   -1.84210e-04    9.14616e-04      2015-11-02 04:20:45
  # DV13     1.33581e-04   -7.59771e-04    1.52911e-04    7.86433e-04      2015-11-08 11:41:22
  # DV16     3.43088e-04    3.70879e-04   -5.56884e-04    7.51918e-04      2015-11-02 04:20:45
  # DV12    -1.99738e-04   -3.09171e-05   -1.24390e-04    2.37327e-04      2015-11-08 11:41:22
  

# Application of the WVR, Tsys and antpos cal tables
mystep = 7
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  
  from recipes.almahelpers import tsysspwmap
  tsysmap = tsysspwmap(vis = 'uid___A002_Xaca510_X78d.ms', tsystable = 'uid___A002_Xaca510_X78d.ms.tsys', tsysChanTol = 1)
  
  
  
  applycal(vis = 'uid___A002_Xaca510_X78d.ms',
    field = '0',
    spw = '25,27,29,31,33',
    gaintable = ['uid___A002_Xaca510_X78d.ms.tsys', 'uid___A002_Xaca510_X78d.ms.wvr', 'uid___A002_Xaca510_X78d.ms.antpos'],
    gainfield = ['0', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_Xaca510_X78d.ms',
    field = '1',
    spw = '25,27,29,31,33',
    gaintable = ['uid___A002_Xaca510_X78d.ms.tsys', 'uid___A002_Xaca510_X78d.ms.wvr', 'uid___A002_Xaca510_X78d.ms.antpos'],
    gainfield = ['1', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  # Note: J0605+0939 didn't have any Tsys measurement, so I used the one made on Betelgeuse. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xaca510_X78d.ms',
    field = '2',
    spw = '25,27,29,31,33',
    gaintable = ['uid___A002_Xaca510_X78d.ms.tsys', 'uid___A002_Xaca510_X78d.ms.wvr', 'uid___A002_Xaca510_X78d.ms.antpos'],
    gainfield = ['3', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_Xaca510_X78d.ms',
    field = '3',
    spw = '25,27,29,31,33',
    gaintable = ['uid___A002_Xaca510_X78d.ms.tsys', 'uid___A002_Xaca510_X78d.ms.wvr', 'uid___A002_Xaca510_X78d.ms.antpos'],
    gainfield = ['3', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  if applyonly != True: es.getCalWeightStats('uid___A002_Xaca510_X78d.ms') 
  

# Split out science SPWs and time average
mystep = 8
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaca510_X78d.ms.split') 
  os.system('rm -rf uid___A002_Xaca510_X78d.ms.split.flagversions') 
  split(vis = 'uid___A002_Xaca510_X78d.ms',
    outputvis = 'uid___A002_Xaca510_X78d.ms.split',
    datacolumn = 'corrected',
    spw = '25,27,29,31,33',
    keepflags = T)
  
  

print "# Calibration"

# Listobs, and save original flags
mystep = 9
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaca510_X78d.ms.split.listobs')
  listobs(vis = 'uid___A002_Xaca510_X78d.ms.split',
    listfile = 'uid___A002_Xaca510_X78d.ms.split.listobs')
  
  
  if not os.path.exists('uid___A002_Xaca510_X78d.ms.split.flagversions/Original.flags'):
    flagmanager(vis = 'uid___A002_Xaca510_X78d.ms.split',
      mode = 'save',
      versionname = 'Original')
  
  

# Initial flagging
mystep = 10
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Flagging shadowed data
  
  flagdata(vis = 'uid___A002_Xaca510_X78d.ms.split',
    mode = 'shadow',
    flagbackup = F)
  
  # Flagging edge channels
  
  flagdata(vis = 'uid___A002_Xaca510_X78d.ms.split',
    mode = 'manual',
    spw = '1:0~14;225~239',
    flagbackup = F)

  # Flagging antenna DV12

  flagdata(vis = 'uid___A002_Xaca510_X78d.ms.split',
    mode = 'manual',
    antenna = 'DV12',
    flagbackup = F)  
  

# Putting a model for the flux calibrator(s)
mystep = 11
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  setjy(vis = 'uid___A002_Xaca510_X78d.ms.split',
    standard = 'manual',
    field = 'J0510+1800',
    fluxdensity = [2.99526478415, 0, 0, 0],
    spix = -0.245608193826,
    reffreq = '339.467278454GHz')
  
  

# Save flags before bandpass cal
mystep = 12
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_Xaca510_X78d.ms.split',
    mode = 'save',
    versionname = 'BeforeBandpassCalibration')
  
  

# Bandpass calibration
mystep = 13
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaca510_X78d.ms.split.ap_pre_bandpass') 
  
  gaincal(vis = 'uid___A002_Xaca510_X78d.ms.split',
    caltable = 'uid___A002_Xaca510_X78d.ms.split.ap_pre_bandpass',
    field = '0', # J0510+1800
    spw = '0:384~576,1:96~144,2:768~1152,3:384~576,4:768~1152',
    scan = '1,3',
    solint = 'int',
    refant = 'DV19',
    calmode = 'p')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xaca510_X78d.ms.split.ap_pre_bandpass', msName='uid___A002_Xaca510_X78d.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xaca510_X78d.ms.split.bandpass') 
  bandpass(vis = 'uid___A002_Xaca510_X78d.ms.split',
    caltable = 'uid___A002_Xaca510_X78d.ms.split.bandpass',
    field = '0', # J0510+1800
    scan = '1,3',
    solint = 'inf,8MHz',
    combine = 'scan',
    refant = 'DV19',
    solnorm = True,
    bandtype = 'B',
    gaintable = 'uid___A002_Xaca510_X78d.ms.split.ap_pre_bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xaca510_X78d.ms.split.bandpass', msName='uid___A002_Xaca510_X78d.ms.split', interactive=False) 
  

# Save flags before gain cal
mystep = 14
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_Xaca510_X78d.ms.split',
    mode = 'save',
    versionname = 'BeforeGainCalibration')
  
  

# Gain calibration
mystep = 15
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaca510_X78d.ms.split.phase_int') 
  gaincal(vis = 'uid___A002_Xaca510_X78d.ms.split',
    caltable = 'uid___A002_Xaca510_X78d.ms.split.phase_int',
    field = '0~2', # J0510+1800,J0552+0313,J0605+0939
    solint = 'int',
    refant = 'DV19',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_Xaca510_X78d.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xaca510_X78d.ms.split.phase_int', msName='uid___A002_Xaca510_X78d.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xaca510_X78d.ms.split.ampli_inf') 
  gaincal(vis = 'uid___A002_Xaca510_X78d.ms.split',
    caltable = 'uid___A002_Xaca510_X78d.ms.split.ampli_inf',
    field = '0~2', # J0510+1800,J0552+0313,J0605+0939
    solint = 'inf',
    refant = 'DV19',
    gaintype = 'T',
    calmode = 'a',
    gaintable = ['uid___A002_Xaca510_X78d.ms.split.bandpass', 'uid___A002_Xaca510_X78d.ms.split.phase_int'])
  
  if applyonly != True: es.checkCalTable('uid___A002_Xaca510_X78d.ms.split.ampli_inf', msName='uid___A002_Xaca510_X78d.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xaca510_X78d.ms.split.flux_inf') 
  os.system('rm -rf uid___A002_Xaca510_X78d.ms.split.fluxscale') 
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_Xaca510_X78d.ms.split.fluxscale')
  
  fluxscaleDict = fluxscale(vis = 'uid___A002_Xaca510_X78d.ms.split',
    caltable = 'uid___A002_Xaca510_X78d.ms.split.ampli_inf',
    fluxtable = 'uid___A002_Xaca510_X78d.ms.split.flux_inf',
    reference = '0') # J0510+1800
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: es.fluxscale2(caltable = 'uid___A002_Xaca510_X78d.ms.split.ampli_inf', removeOutliers=True, msName='uid___A002_Xaca510_X78d.ms', writeToFile=True, preavg=10000)
  
  os.system('rm -rf uid___A002_Xaca510_X78d.ms.split.phase_inf') 
  gaincal(vis = 'uid___A002_Xaca510_X78d.ms.split',
    caltable = 'uid___A002_Xaca510_X78d.ms.split.phase_inf',
    field = '0~2', # J0510+1800,J0552+0313,J0605+0939
    solint = 'inf',
    refant = 'DV19',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_Xaca510_X78d.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xaca510_X78d.ms.split.phase_inf', msName='uid___A002_Xaca510_X78d.ms.split', interactive=False) 
  

# Save flags before applycal
mystep = 16
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_Xaca510_X78d.ms.split',
    mode = 'save',
    versionname = 'BeforeApplycal')
  
  

# Application of the bandpass and gain cal tables
mystep = 17
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  for i in ['0']: # J0510+1800
    applycal(vis = 'uid___A002_Xaca510_X78d.ms.split',
      field = str(i),
      gaintable = ['uid___A002_Xaca510_X78d.ms.split.bandpass', 'uid___A002_Xaca510_X78d.ms.split.phase_int', 'uid___A002_Xaca510_X78d.ms.split.flux_inf'],
      gainfield = ['', i, i],
      interp = 'linear,linear',
      calwt = T,
      flagbackup = F)
  
  applycal(vis = 'uid___A002_Xaca510_X78d.ms.split',
    field = '1,2~3', # J0605+0939,Betelgeuse
    gaintable = ['uid___A002_Xaca510_X78d.ms.split.bandpass', 'uid___A002_Xaca510_X78d.ms.split.phase_inf', 'uid___A002_Xaca510_X78d.ms.split.flux_inf'],
    gainfield = ['', '1', '1'], # J0552+0313
    interp = 'linear,linear',
    calwt = T,
    flagbackup = F)
  

# Split out corrected column
mystep = 18
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaca510_X78d.ms.split.cal') 
  os.system('rm -rf uid___A002_Xaca510_X78d.ms.split.cal.flagversions') 
  split(vis = 'uid___A002_Xaca510_X78d.ms.split',
    outputvis = 'uid___A002_Xaca510_X78d.ms.split.cal',
    datacolumn = 'corrected',
    keepflags = T)
  
  

# Save flags after applycal
mystep = 19
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_Xaca510_X78d.ms.split.cal',
    mode = 'save',
    versionname = 'AfterApplycal')
  
  

