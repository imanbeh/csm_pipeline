# Ideally, use the original CASA format images.  Otherwise these
#  commands may work on fits but probably you will need to use
#  importfits to import the images into CASA

# You can use the casa viewer and the spectral tool to guide you in
#  working out what sort of size regions you want to extract the
#  emission in (use 'flux')

# First, identify the region - you can use any coordinate system, here
# pixels (you can also use fractional pixels).

# If you want to centre on the continuum peak, you can get its centre
#  using imstat (but check that the image is the same size and pixel
#  size as the fits cubes, or adjust accordingly. To check, you can
#  use the viewer or task 'imhead'.

# If you want something more complex than a circle, use 
# 'help par.region' in CASA
# These are just example values

imbase='Betelgeuse_TC_spw'
#imbase='Betelgeuse_allines_'
spws=['345.8GHz.image.image','345.2GHz.image.image','343.2GHz.image.image','332.6GHz.image.image','330.6GHz.image.image']
# centre of 20% contour, excluding E bulge
cen='[398pix,399pix]' # TC
#cen='[497pix,496.5pix]' # all_hires
# 90 mas,  300 mas, 4.5 asec radii
#radii=['14.5pix','75pix','500pix'] #all
#rads=['.029asec','.15asec','1asec'] #all
#rms='[100pix, 100pix],[899pix,249pix]' # all
radii=['3pix','10pix','150pix'] # TC
# 90 mas,  300 mas, 4.5 asec radii
rms='[330pix, 50pix],[669pix,149pix]' # TC
rads=['.09asec','.3asec','4.5asec']

# TC cube cell  30 mas
# All cell 2 mas
"""
for s in range(5):
#    ia.open(imbase+str(s)+'.image.image') # TC
    ia.open(imbase+spws[s]) # whatever input cube is called
    for r in range(3):
        outfile=open(imbase+spws[s][0:-12]+'_R'+rads[r]+'.spec', 'w') # spectrum
        f=ia.getprofile(axis = 3, function = "flux", 
                        region = 'circle['+cen+','+radii[r]+']')
        freq=f['coords']
        flux=f['values']
        for z in  zip(f['coords'],f['values']):
            print >> outfile, z[0], z[1]
        outfile.close()
    outfile=open(imbase+spws[s][0:-12]+'_rms.spec', 'w')  # rms
    f=ia.getprofile(axis = 3, function = "rms", region ='box['+rms+']')
    freq=f['coords']
    flux=f['values']
    for z in  zip(f['coords'],f['values']):
        print >> outfile, z[0], z[1]
    outfile.close()
    ia.close()
"""
# TC cube cell  30 mas

for s in range(5):
    ia.open(imbase+str(s)+'.image.image') # whatever input cube is called
    for r in range(3):
        outfile=open(imbase+str(s)+'_R'+rads[r]+'.spec', 'w') # spectrum
        f=ia.getprofile(axis = 3, function = "flux", 
                        region = 'circle['+cen+','+radii[r]+']')
        freq=f['coords']
        flux=f['values']
        for z in  zip(f['coords'],f['values']):
            print >> outfile, z[0], z[1]
        outfile.close()
    outfile=open(imbase+str(s)+'_rms.spec', 'w')  # rms
    f=ia.getprofile(axis = 3, function = "rms", region ='box['+rms+']')
    freq=f['coords']
    flux=f['values']
    for z in  zip(f['coords'],f['values']):
        print >> outfile, z[0], z[1]
    outfile.close()
    ia.close()
