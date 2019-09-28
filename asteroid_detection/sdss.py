"""
Get data from the Sloan Digital Sky Survey (SDSS).
"""

import io
import tempfile
import requests
from PIL import Image

from astropy.io import fits

def jpg_from_rcf(run, camcol, field):
    """
    Get a jpg image from sdss given run, camcol, and field.

    Parameters
    ----------
    run : int
    camcol : int
    field : int

    Returns
    -------
    img : PIL.JpegImagePlugin.JpegImageFile
        This image can be plotted with matplotlib or converted to numpy array with np.array(img).
    """
    zoom = 0
    assert zoom in [0, 12, 25, 50]
    url = "http://skyserver.sdss.org/dr13/SkyServerWS/ImgCutout/getJpegCodec?"\
          "R={}&C={}&F={}&Z={}".format(run, camcol, field, 0)
    response = requests.get(url)
    response.raise_for_status()
    ff = io.BytesIO(response.content)
    img = Image.open(ff)
    return img

def fits_from_rcf(run, camcol, field, rerun=301, bands=["g", "r", "u", "i", "z"]):
    """
    Get fits image from sdss given run, camcol, and field.

    For more infomation on bulk data searches, see:
    https://www.sdss.org/dr15/data_access/bulk/#ImagingData

    Parameters
    ----------
    run : int
    camcol : int
        Camera column
    field : int
    rerun : int
        Rerun specifies a particular processing pipeline that the original data
        has been sent through.
    bands : list
        Specify which bands of imagery to get.  To get only the green channel,
        this value should be ["g"].

    Returns
    -------
    fits_files : dict
        Dictionary containing the astropy fits files for every band.
    """
    fits_files = {}
    for band in bands:
        url = "https://data.sdss.org/sas/dr15/eboss/photoObj/frames/"\
              "{rerun}/{run}/{camcol}/frame-{band}-{run:06d}-{camcol}"\
              "-{field:04d}.fits.bz2".format(rerun=rerun, run=run, camcol=camcol,
                                             field=field, band=band)
        response = requests.get(url)
        response.raise_for_status()
        # Reading from a Bytes stream produces an error, use tempfile instead
        with tempfile.NamedTemporaryFile() as ff:
            ff.write(response.content)
            hdul = fits.open(ff.name)
        fits_files[band] = hdul
    return fits_files
