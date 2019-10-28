"""
example code, will show a random FITS image
"""

import dippykit as dip
import neowise_api as neo
from fits_file import Fits
import json
import numpy as np
from astropy import wcs

with open('asteroid_catalog.json', 'r') as file:
    catalog = json.load(file)
catalog = list(catalog.items())
rand = np.random.randint(len(catalog))
item = catalog[int(rand)]
cake = [item]

# overlay = np.zeros((1016, 1016, 3))

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
total = np.zeros(2)
center = [0, 0]
count = 0
ra = 0
dec = 0
size = 3
cutout = []
if len(IMAGE_DETAILS) < 6:
    size = len(IMAGE_DETAILS) - 1

for idx in range(size):
    NAME[idx] = IMAGE_DETAILS[idx][0]
    IMAGE.append(neo.download_fits(NAME[idx]))
    FITS.append(Fits(IMAGE[idx], IMAGE_DETAILS[idx]))
    FITS[idx].filter_image()
    FITS[idx].scale_image()
    FITS[idx].circle_asteroid()
    ra, dec = FITS[idx].coordinates(world=True)
    total[0] += ra[0]
    total[1] += dec[0]
    count += 1
    dip.subplot(3, 2, idx+1)
    dip.title('image: ' + str(idx))
    dip.imshow(FITS[idx].image(), cmap='gist_heat')
    print('finished number ', idx)
    print(np.shape(FITS[idx].image()))
center = total/count
dip.show()

# overlay[::][::][0] = FITS[0].image()
# overlay[::][::][1] = FITS[1].image()
# overlay[::][::][2] = FITS[2].image()
FITS[0].normalize()
FITS[1].normalize()
FITS[2].normalize()
im1 = FITS[0].image()
im2 = FITS[1].image()
im3 = FITS[2].image()
print(im1[0][0], im2[0][0], im3[0][0])
overlay = np.stack((im1, im2, im3), axis=2)
print(overlay[0][0])
dip.imshow(overlay)
dip.show()

exit()
for idx in range(size):
    coord = wcs.WCS(FITS[idx]._file)
    x_temp, y_temp = coord.wcs_world2pix(center[0], center[1], 0)
    #x, y = FITS[idx].coordinates()
    img = FITS[idx].image()
    cutout.append(img[int(y_temp)-70:int(y_temp)+70, int(x_temp)-70:int(x_temp)+70])
    dip.subplot(3, 2, idx + 1)
    dip.title('image: ' + str(idx))
    dip.imshow(cutout[idx], cmap='gist_heat')
dip.show()
