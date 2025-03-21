import re
#
#########################################################################################################################################
############################################# PRE-IMAGING ###############################################################################
#########################################################################################################################################
#
print 'Split off the continuum, averaging in frequency'
finalvis= '../calibrated/uid___A002_Xaca510_X78d.ms.split.cal'
contspws = '0,1,2,3,4'
#
## We have complex line emission and no dedicated continuum windows, so will need to flag the line channels prior to averaging.
flagmanager(vis=finalvis,mode='save', versionname='before_cont_flags')
#
## Flag the "line channels"
flagchannels='0:190~280, 1:80~140, 2:200~450;680~1100, 3:450~600, 4:450~1000;1200~1650' # Channels where there are (may be!) lines
flagdata(vis=finalvis,mode='manual', spw=flagchannels,flagbackup=False)
#
## Average the channels within spws
contvis='calibrated_final_cont.ms'
rmtables(contvis)
os.system('rm -rf ' + contvis + '.flagversions')
#
## IF YOU ARE USING CASA VERSION 4.4 AND ABOVE TO IMAGE, UNCOMMENT THE FOLLOWING. DELETE IF NOT APPROPRRIATE.
split2(vis=finalvis, field='3', spw=contspws,  outputvis=contvis, width=[128,64,128,128,128], datacolumn='data')
#
## In CASA 4.4 and above, you should check the weights. You will need to change antenna and field to appropriate values
##plotms(vis=contvis, yaxis='wtsp',xaxis='freq',spw='',antenna='DV19',field='0', plotfile='weights_freq.png')
#
## If you flagged any line channels, restore the previous flags
flagmanager(vis=finalvis,mode='restore', versionname='before_cont_flags')
#
# Shift Betelgeuse to phase center
fixvis(vis=contvis, outputvis='calibrated_cont_shift.ms', phasecenter='J2000 05h55m10.331s 07d24m25.571s')

## Inspect continuum for any problems
plotms(vis='calibrated_cont_shift.ms', xaxis='uvdist', yaxis='real', coloraxis='spw', plotfile='uvdist_amp.png', ydatacolumn = 'corrected', selectdata = True, avgchannel = '99999', avgtime='99999', avgscan=True)
