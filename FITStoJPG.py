# Need to install Anaconda Python Distribution, but make sure
# it does not mess up PyCharm as your default IDE
# https://www.astropy.org/
# then run in the Windows command window: conda update astropy


import sys
import numpy as np

try:
    from astropy.io import fits
except ImportError:
    import pyfits as fits
from PIL import Image

# Read command line arguments
# try:
#    fitsfilename = sys.argv[1]
#    vmin, vmax = float(sys.argv[2]), float(sys.argv[3])
# except IndexError:
#    sys.exit('Usage: ' + sys.argv[0] + ' FITSFILENAME VMIN VMAX')

# Try to read data from first HDU in fits file
fitsfilename = "C:/Users/Andres/Documents/GATech/ECE6258_DigitalImageProcessing/FinalProject/iris-100.fits"
data = fits.open(fitsfilename)[0].data
# If nothing is there try the second one
if data is None:
    data = fits.open(fitsfilename)[1].data

# Clip data to brightness limits
vmin = 2 # this controls the intensity of the darker values. I found 2 and 3 look nice.
vmax = 5 # this controls the intensity of the lighter values. I found 5 and 6 look nice.
data[data > vmax] = vmax
data[data < vmin] = vmin
# Scale data to range [0, 1]
data = (data - vmin) / (vmax - vmin)
# Convert to 8-bit integer
data = (255 * data).astype(np.uint8)
# Invert y axis
data = data[::-1, :]

# Create image from data array and save as jpg
image = Image.fromarray(data, 'L')
imagename = fitsfilename.replace('.fits', '.jpg')

image.save(imagename)

