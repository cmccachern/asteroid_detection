=========================
Read FITS files in Python
=========================

The FITS file is a storage file format for astronomical imaging data. To read a FITS file from python,
see `astropy <https://docs.astropy.org/en/stable/io/fits/>`_.  Conveniently, astropy is installed with
the `anaconda <https://www.anaconda.com/distribution/>`_ distribution of python 3.  Install astropy if you
do not have it already.

Start by downloading a FITS file that we can work with.  In this example, we will use the green channel
of `this image <https://dr12.sdss.org/fields/runCamcolField?run=752&camcol=1&field=373>`_ that contains an asteroid.
Now, we can open and display the image

>>> from astropy.io import fits
>>> import numpy as np
>>> import matplotlib.pyplot as plt
>>> fits_file = "frame-g-000752-1-0373.fits"
>>> hdul = fits.open(fits_file)
>>> data = hdul[0].data
>>> plt.imshow(np.log10(data))
>>> plt.show()

To see how SDSS converts their FITS files into jpg images, look
`here <https://www.sdss.org/dr14/imaging/jpg-images-on-skyserver/>`_.
