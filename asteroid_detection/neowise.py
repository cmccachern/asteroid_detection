"""
Get data from the Neowise survey.
"""

import numpy as np
import matplotlib.pyplot as plt
import requests
import tempfile
from astropy.io import fits
import atpy


def retrieve_asteroid_data(asteroid, **kwargs):
    """
    Get Metadata for an asteroid given asteroid name or number,

    For more infomation on bulk data searches, see:


    Parameters
    ----------
    asteroid : string

    Other Parameters
    ------
    pos : string
        kwarg for coordinates, format: ##h+##m+##.##s+##d+##m+##.##s (hour-arcminute-arcsecond, degree-minute-second)
        (RA, DEC)
    spatial : string
        kwarg for search area, options: box, polygon, upload, none
    format : int
        kwarg for output format. 0:HTML, 1: ASCII, 2: SVC, 3: VO Table, 6: XML
    size : int


    Returns
    -------
    asteroid_sightings : table
        Dictionary containing the astropy fits files for every band.
    """
    url = "https://irsa.ipac.caltech.edu/cgi-bin/Gator/nph-query?" \
          "outfmt=1&searchForm=MO&spatial=cone&catalog=neowiser_p1bs_psd" \
          "&moradius=5&mobj=smo&mobjstr="

    kw = {'pos': '', 'spatial': '', 'format': None, 'size': None}
    for key, value in kwargs.items():
        if key in kw:
            kw[key] = value

    pos = '&objstr=' + kw['pos']
    size = '&size=' + kw['size']
    fmt = '&outfmt=' + kw['format']
    spatial = '&spatial=' + kw['spatial']
    html = requests.get(url + asteroid)
    html.raise_for_status()

    with tempfile.NamedTemporaryFile() as tbl:
        tbl.write(html.content)
        table = fits.open(tbl.name)
    asteroid_sightings = atpy.Table(table)
    return asteroid_sightings


def search_for_fits(ra, dec):
    """
    Get Metadata for images at a specific coordinate,

    For more infomation on bulk data searches, see:


    Parameters
    ----------
    ra : float
        Right ascension (0 - 360)
    dec : float
        Declination (0 - 360)

    Returns
    -------
    image_metadata : table
        Dictionary containing the astropy fits files for every band.
    """
    search = 'https://irsa.ipac.caltech.edu/ibe/search/wise/neowiser/p1bm_frm?POS=' + str(ra) + str(dec)
    html = requests.get(search)
    with tempfile.NamedTemporaryFile() as tbl:
        tbl.write(html.content)
        table = fits.open(tbl.name)
    image_metadata = atpy.Table(table)
    return image_metadata







# fits directory = https://irsa.ipac.caltech.edu/ibe/data/wise/neowiser/p1bm_frm/       params
# Metadata table = https://irsa.ipac.caltech.edu/ibe/docs/wise/neowiser/p1bm_frm/
# neowise search = https://irsa.ipac.caltech.edu/ibe/search/wise/neowiser/p1bm_frm?     POS=
# Gator search = https://irsa.ipac.caltech.edu/cgi-bin/Gator/nph-query?
# catalog names = ['neowiser_p1bs_psd', 'neowiser_p1ba_mch', 'neowiser_p1bs_frm', 'neowiser_p1bl_lod']

tb = retrieve_asteroid_data('Ceres')
print(tb.columns)
