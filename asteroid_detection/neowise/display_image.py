"""
example code, will show a random FITS image
"""

import dippykit as dip
import neowise_api as neo
from fits_file import Fits
import json
import numpy as np

with open('asteroid_catalog.json', 'r') as file:
    catalog = json.load(file)
catalog = list(catalog.items())
rand = np.random.randint(len(catalog))
item = catalog[int(rand)]
cake = [item]
#print(item[1]['asteroids'])
for i in catalog:
    if item[1]['asteroids'][0]['date'][:9] == i[1]['asteroids'][0]['date'][:9]:
        for ast in range(len(i[1]['asteroids'])):
            if item[1]['asteroids'][0]['name'] == i[1]['asteroids'][ast]['name']:
                cake.append(i)

#IMAGE_DETAILS = np.zeros(5)
NAME = ['' for i in range(5)]
IMAGE = []
FITS = []
IMAGE_DETAILS = [i for i in cake]

size = 5
if len(IMAGE_DETAILS) < 6:
    size = len(IMAGE_DETAILS) - 1

for idx in range(size):
    #print(cake[idx])
    #IMAGE_DETAILS[idx] = neo.find_params()
    #IMAGE_DETAILS[idx] = cake[idx]
    NAME[idx] = IMAGE_DETAILS[idx][0]
    IMAGE.append(neo.download_fits(NAME[idx]))
    FITS.append(Fits(IMAGE[idx], IMAGE_DETAILS[idx]))
    FITS[idx].filter_image()
    FITS[idx].scale_image()
    FITS[idx].circle_asteroid()
    # print(FITS.coordinates())
    dip.subplot(3, 2, idx+1)
    dip.title('image: ' + str(idx))
    dip.imshow(FITS[idx].image(), cmap='gist_heat')

dip.show()
