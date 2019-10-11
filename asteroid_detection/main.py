"""
example code, will show a random FITS image
"""

import numpy as np
import dippykit as dip
import neowise as neo


IMAGE_DETAILS = neo.find_params()
NAME = IMAGE_DETAILS[0]
FITS = neo.download_fits(NAME)
FITS.data = neo.filter_image(FITS.data)
FITS.data = np.clip(FITS.data, np.median(FITS.data), np.max(FITS.data))
FITS.data = np.log(FITS.data - np.median(FITS.data) + 1)
FITS.data = np.clip(FITS.data, 0.3*np.max(FITS.data), np.max(FITS.data))
dip.imshow(FITS.data, cmap='gist_heat')
dip.colorbar()
dip.show()
