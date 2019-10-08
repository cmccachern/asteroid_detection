"""
Get data from the Neowise survey.
"""

import numpy as np
import matplotlib.pyplot as plt
import requests
import tempfile
from astropy.io import fits
import atpy


def retrieve_asteroid_data(asteroid, **argv):

    url = 'https://irsa.ipac.caltech.edu/cgi-bin/Gator/nph-query?outfmt=1&searchForm=MO&spatial=cone&catalog=neowiser_p1bs_psd&moradius=5&mobj=smo&mobjstr='
    html = requests.get(url + asteroid)
    html.raise_for_status()

    with tempfile.NamedTemporaryFile() as tbl:
        tbl.write(html.content)
        table = fits.open(tbl.name)
    return atpy.Table(table)

retrieve_asteroid_data('Ceres')
