vis = 'Betelgeuse_TC_line_shfxscl.ms.contsub'

# factor = 1.42857  for continuum - 25% mis-scale, rest variability
factor = 1.25   # for line
nspw = 5


ms.open(vis,nomodify=False)
# do 1 spw at a time in case different nchan i.e. different data shapes

for i in range(nspw):
  ms.selectinit(datadescid=i)
#  mydata = ms.getdata(['data','corrected_data'])
  mydata = ms.getdata(['data'])
  mydata['data'] *= factor
#  mydata['corrected_data'] *= factor
  ms.putdata(mydata)

ms.close()
