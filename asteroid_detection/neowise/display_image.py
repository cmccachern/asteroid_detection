"""
example code, will show a random FITS image
"""

import dippykit as dip
import neowise_api as neo
from fits_file import Fits


IMAGE_DETAILS = neo.find_params()
NAME = IMAGE_DETAILS[0]
IMAGE = neo.download_fits(NAME)
FITS = Fits(IMAGE, IMAGE_DETAILS)
FITS.filter_image()
FITS.scale_image()
FITS.circle_asteroid()
# FITS.image = np.clip(FITS.image, np.median(FITS.image), np.max(FITS.image))
# FITS.image = np.log(FITS.image - np.median(FITS.image) + 1)
# FITS.image = np.clip(FITS.image, 0.3*np.max(FITS.image), np.max(FITS.image))
print(FITS.coordinates())
dip.imshow(FITS.image(), cmap='gist_heat')
dip.colorbar()
dip.show()
