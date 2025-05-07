# csm_pipeline
MS thesis on calculating the circumstellar material distribution of a star of a star using high and low resolution data

___________________________________________________________________________________

template.ipynb
Use the template notebook with your choice high and low resolution files. Download all .py files in order for it to run.

___________________________________________________________________________________

Lowhigh, medhigh and lowmed.ipynb
all document trials of different comparisons between different resolution datasets.

___________________________________________________________________________________

pandas.ipynb
puts important info about each resolution dataset in a table

___________________________________________________________________________________

abel.py
plotting and parsing code for my specific setup \
do_abel takes in a radial profile of surface density, radius at each point in the radial profile, and the background median. \
returns radial profile of volumetric density


___________________________________________________________________________________

DATA VALIDATION
blanktest.ipynb
data validation for radial profile and inverse abel transform 
For radial profile:
Makes an arbitrary 2D star with linearly decreasing intensity with radius and a constant background.
Runs star through radial profile process to validate the profile will appear as a line with a slope of -1 and a y intercept of the max intensity of the star, and a sharp drop to the background median beyond the stellar radius. Also verifies standard deviation calculations within each annulus
For inverse abel transform:
Performs inverse abel transforms on test cases with verifyable analytic solutions

___________________________________________________________________________________

thesis\
Figures for thesis!

___________________________________________________________________________________

The data used in this notebook is not public. However, this pipeline will still be usable with your choice ALMA data.

___________________________________________________________________________________
