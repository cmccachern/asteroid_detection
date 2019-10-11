"""
Get data from the Neowise survey.
"""
import json
import tempfile
import numpy as np
import requests
from astropy.io import fits
import atpy



def search_points(**kwargs):
    """
    Get Metadata for an asteroid given asteroid name or number,

    For more infomation on bulk data searches, see:
    https://irsa.ipac.caltech.edu/applications/Gator/GatorAid/irsa/catsearch.html

    Other Parameters
    ------
    pos : string
        kwarg for coordinates, required when spatial = cone or box
        format: ##h+##m+##.##s+##d+##m+##.##s (hour-arcminute-arcsecond, degree-minute-second)
        (RA, DEC)
    spatial : string
        kwarg for search area(default is cone), options: box, polygon, upload, none
    format : int
        kwarg for output format. optional, default = 1. 0:HTML, 1: ASCII, 2: SVC, 3: VO Table, 6: XML
    radius : int
        kwarg for cone radius. optional, default value is 10 arcseconds
    size : int
        kwarg for box size. only required if spatial = box
    btime : string
        kwarg for beginning time. format: btime=2018+01+01+01:01:01
    etime : string
        kwarg for ending time. format: etime=2018+01+01+01:01:01

    Returns
    -------
    source_points : table
        Dictionary containing the astropy fits files for every band.
    """
    constraints = {'pos': '&objstr=', 'size': '&size=', 'format': '&outfmt=',
                   'spatial': '&spatial=', 'radius': '&radius=', 'btime': '&btime=',
                   'etime': '&etime='}
    query = ''
    url = "https://irsa.ipac.caltech.edu/cgi-bin/Gator/nph-query?" \
          "outfmt=1&searchForm=MO&catalog=neowiser_p1bs_psd"

    for key, value in kwargs.items():
        if key in constraints:
            query = query + constraints[key] + value

    if not kwargs['spatial']:
        query = query + '&spatial=cone'
    if not kwargs['pos']:
        query = query + '&objstr=' + str(np.random.randint(61)) + 'h+' + str(np.random.randint(61)) +\
            'm+' + str(np.random.randint(61)) + 's+' + str(np.random.randint(361)) + 'd+' + \
            str(np.random.randint(61)) + 'm+' + str(np.random.randint(6001)/100) + 's'
    if not kwargs['format']:
        query = query + '&outfmt=1'

    html = requests.get(url + query)
    html.raise_for_status()
    print('after request:', kwargs['pos'])
    with tempfile.NamedTemporaryFile(suffix='.tbl') as tbl:
        tbl.write(html.content)
        source_points = atpy.Table(tbl.name)
    return source_points


def search_asteroid(asteroid, **kwargs):
    """
    Get Metadata for an asteroid given asteroid name or number,

    For more infomation on bulk data searches, see:
    https://irsa.ipac.caltech.edu/applications/Gator/GatorAid/irsa/catsearch.html

    Parameters
    ----------
    asteroid : string
        search for all known sightings of a specific asteroid

    Other Parameters
    ------
    btime : string
        kwarg for beginning time. format: btime=2018+01+01+01:01:01
    etime : string
        kwarg for ending time. format: etime=2018+01+01+01:01:01

    Returns
    -------
    asteroid_sightings : table
        Dictionary containing the astropy fits files for every band.
    """
    constraints = {'btime': '&btime=', 'etime': '&etime='}
    query = ''
    for key, value in kwargs.items():
        if key in constraints:
            query = query + constraints[key] + value

    url = "https://irsa.ipac.caltech.edu/cgi-bin/Gator/nph-query?" \
          "outfmt=1&searchForm=MO&catalog=neowiser_p1bs_psd" \
          "&mobj=smo&mobjstr="

    html = requests.get(url + asteroid + query)
    html.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix='.tbl') as tbl:
        tbl.write(html.content)
        asteroid_sightings = atpy.Table(tbl.name)
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
    search = 'https://irsa.ipac.caltech.edu/ibe/search/wise/neowiser/p1bm_frm?POS=' + str(ra) + ',' + str(dec)
    html = requests.get(search)
    html.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix='.tbl') as tbl:
        tbl.write(html.content)
        image_metadata = atpy.Table(tbl.name)
    return image_metadata


def find_params():
    """
    load asteroid_catalog.json, find a random image to download from irsa,

    Returns
    -------
    catalog : list
        object with image parameters and known asteroid coordinates in image
    """
    with open('asteroid_catalog.json', 'r') as f:
        catalog = json.load(f)
    catalog = list(catalog.items())
    r = np.random.randint(len(catalog))
    return catalog[r]


def download_fits(fits_name):
    """
    Download FITS image from irsa website

    Parameters
    ------
    fits_name : dictionary or string
        the name of the fits image, so that it can be retrieved
        from the irsa database

    Returns
    -------
    fits_file : fits
        A neowise fits image with header
    """
    if type(fits_name) == str:
        for index, char in enumerate(fits_name):
            if char.isalpha():
                index = index+1
        params = {'scan_id': str(fits_name[:index]),
                  'frame_num': int(fits_name[index:-1]),
                  'band': int(fits_name[-1])
                  }
    else:
        params = fits_name
    params['scangrp'] = params['scan_id'][-2:]
    path = str.format(
        '{scangrp:s}/{scan_id:s}/{frame_num:03d}/{scan_id:s}{frame_num:03d}-w{band:1d}-int-1b.fits', **params)
    url = 'https://irsa.ipac.caltech.edu/ibe/data/wise/neowiser/p1bm_frm/' + path
    response = requests.get(url)
    response.raise_for_status()

    # Reading from a Bytes stream produces an error, use tempfile instead
    with tempfile.NamedTemporaryFile() as ff:
        ff.write(response.content)
        fits_file = fits.open(ff.name)
    return fits_file[0]


def filter_image(data):
    """
    average NaN pixels to reduce noise,

    Parameters
    ------
    data : Numpy array
        Image that is to be filtered

    Returns
    -------
    data : numpy array
        Filtered image
    """
    done = False
    while not done:
        done = True
        for row in range(len(data)):
            for col in range(len(data[row])):
                total = 0
                count = 0
                if np.isnan(data[row, col]):
                    for x_index in range(-1, 1):
                        for y_index in range(-1, 1):
                            if not np.isnan(data[row + x_index, col + y_index]):
                                total = total + data[row + x_index, col + y_index]
                                count = count + 1
                    if count and not np.isnan(total):
                        data[row, col] = total/count
                    else:
                        done = False
    return data

# fits directory = https://irsa.ipac.caltech.edu/ibe/data/wise/neowiser/p1bm_frm/       params
# Metadata table = https://irsa.ipac.caltech.edu/ibe/docs/wise/neowiser/p1bm_frm/
# neowise search = https://irsa.ipac.caltech.edu/ibe/search/wise/neowiser/p1bm_frm?     POS=
# Gator search = https://irsa.ipac.caltech.edu/cgi-bin/Gator/nph-query?
# catalog names = ['neowiser_p1bs_psd', 'neowiser_p1ba_mch', 'neowiser_p1bs_frm', 'neowiser_p1bl_lod']
