"""
example code, will show a random FITS image
"""

import dippykit as dip
import neowise_api as neo
from fits_file import Fits
import json
import matplotlib as plt
import numpy as np
from astropy import wcs

with open('asteroid_catalog.json', 'r') as file:
    catalog = json.load(file)
catalog = list(catalog.items())
rand = np.random.randint(len(catalog))
item = catalog[int(rand)]
cake = [item]

disp = np.zeros((1016, 1016, 3))
canvas_r = np.zeros((1016*3, 1016*3))
canvas_g = np.zeros((1016*3, 1016*3))
canvas_b = np.zeros((1016*3, 1016*3))
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
    #FITS[idx].circle_asteroid()
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
FITS[0].circle_asteroid()
im1 = FITS[0].image()
im2 = FITS[1].image()
im3 = FITS[2].image()
# for x in range(1016):
#     for y in range(1016):
#         canvas_r[x + 1016][y + 1016] = im1[x][y]
#         canvas_g[x + 1016][y + 1016] = im2[x][y]
#         canvas_b[x + 1016][y + 1016] = im3[x][y]
print(np.shape(canvas_r[0][0]), np.shape(canvas_g[0][0]), np.shape(canvas_b[0][0]))
#overlay = np.stack((canvas_r, canvas_g, canvas_b), axis=2)
# print(np.shape(overlay))
# print(overlay[0][0])
# dip.imshow(overlay)
# dip.show()
shift_x = [0, 0, 0]
shift_y = [0, 0, 0]

for idx in range(size):
    coord = wcs.WCS(FITS[idx]._file)
    x_temp, y_temp = coord.wcs_world2pix(center[0], center[1], 0)
    if idx == 0:
        center_x, center_y = x_temp, y_temp
        print(center_x, center_y)
    else:
        shift_x[idx], shift_y[idx] = int(center_x - x_temp), int(center_y - y_temp)

for x in range(1016):
    for y in range(1016):
        canvas_r[y + 1016 + shift_y[0]][x + 1016 + shift_x[0]] = im1[y][x]
        canvas_g[y + 1016 + shift_y[1]][x + 1016 + shift_x[1]] = im2[y][x]
        canvas_b[y + 1016 + shift_y[2]][x + 1016 + shift_x[2]] = im3[y][x]
    #x, y = FITS[idx].coordinates()
    #img = FITS[idx].image()
    #cutout.append(img[int(y_temp)-70:int(y_temp)+70, int(x_temp)-70:int(x_temp)+70])
    #dip.subplot(3, 2, idx + 1)
    #dip.title('image: ' + str(idx))
    #dip.imshow(cutout[idx], cmap='gist_heat')
print(np.shape(canvas_r[0][0]), np.shape(canvas_g[0][0]), np.shape(canvas_b[0][0]))
overlay = np.stack((canvas_r, canvas_g, canvas_b), axis=2)
for a in range(1016):
    for b in range(1016):
        for c in range(3):
            disp[a][b][c] = overlay[a + int(center_y) + 508][b + int(center_x) + 508][c]
print(np.shape(overlay))
print(overlay[0][0])
dip.imshow(disp)
dip.show()
