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
from PIL import Image

with open('asteroid_catalog.json', 'r') as file:
    catalog = json.load(file)
catalog = list(catalog.items())
for object in range(1000):
    rand = np.random.randint(len(catalog))
    item = catalog[int(rand)]
    cake = [item]

    canvas_r = np.zeros((1016*3, 1016*3))
    canvas_g = np.zeros((1016*3, 1016*3))
    canvas_b = np.zeros((1016*3, 1016*3))

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
    ast = []
    date = []
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
        FITS[idx].name()
        ra, dec = FITS[idx].coordinates(world=True)
        x, y = FITS[idx].coordinates(world=False)
        date_temp = FITS[idx].date()
        total[0] += ra[0]
        total[1] += dec[0]
        ast.append([x[0], y[0]])
        date.append(date_temp[0])
        count += 1
        #dip.subplot(3, 2, idx+1)
        #dip.title('image: ' + str(idx))
        #dip.imshow(FITS[idx].image(), cmap='gist_heat')
        print('countdown: ', 3 - idx)
        print(np.size(FITS))
    center = total/count
    #dip.show()

    if len(FITS) >= 3:
        FITS[0].normalize()
        FITS[1].normalize()
        FITS[2].normalize()
        #FITS[0].circle_asteroid()
        im1 = FITS[0].image()
        im2 = FITS[1].image()
        im3 = FITS[2].image()

        shift_x = [0, 0, 0]
        shift_y = [0, 0, 0]

        for idx in range(size):
            coord = wcs.WCS(FITS[idx].file())
            x_temp, y_temp = coord.wcs_world2pix(center[0], center[1], 0)
            if idx == 0:
                center_x, center_y = x_temp, y_temp
                print(center_x, center_y)
            else:
                shift_x[idx], shift_y[idx] = int(center_x - x_temp), int(center_y - y_temp)
        print(shift_x, shift_y)
        if np.max(shift_x) < 1016 and np.max(shift_y) < 1016:
            for x in range(1016):
                for y in range(1016):
                    canvas_r[y + 1016 + shift_y[0]][x + 1016 + shift_x[0]] = im1[y][x]
                    canvas_g[y + 1016 + shift_y[1]][x + 1016 + shift_x[1]] = im2[y][x]
                    canvas_b[y + 1016 + shift_y[2]][x + 1016 + shift_x[2]] = im3[y][x]

            hor = 1016 - np.abs(np.max(shift_x) - np.min(shift_x))
            ver = 1016 - np.abs(np.max(shift_y) - np.min(shift_y))
            disp = np.zeros((ver, hor, 3))

            print(hor, ver)

            overlay = np.stack((canvas_r, canvas_g, canvas_b), axis=2)
            for a in range(ver):
                for b in range(hor):
                    for c in range(3):
                        disp[a][b][c] = overlay[a + np.max(shift_y) + 1016][b + np.max(shift_x) + 1016][c]

            # print(ast[0][0] - (np.max(shift_x) + shift_x[0]), ast[0][1] - (np.max(shift_y)) + shift_y[0])
            # print(ast[1][0] - (np.max(shift_x)) + shift_x[1], ast[1][1] - (np.max(shift_y)) + shift_y[1])
            # print(ast[2][0] - (npmi.max(shift_x)) + shift_x[2], ast[2][1] - (np.max(shift_y)) + shift_y[2])
            asteroid1 = [ast[0][0] - (np.max(shift_x) + shift_x[0]), ast[0][1] - (np.max(shift_y)) + shift_y[0]]
            asteroid2 = [ast[1][0] - (np.max(shift_x)) + shift_x[1], ast[1][1] - (np.max(shift_y)) + shift_y[1]]
            asteroid3 = [ast[2][0] - (np.max(shift_x)) + shift_x[2], ast[2][1] - (np.max(shift_y)) + shift_y[2]]
            ast1date = date[0]
            ast2date = date[1]
            ast3date = date[2]
            print(asteroid1)
            print(asteroid2)
            print(asteroid3)
            print(ast1date)
            print(ast2date)
            print(ast3date)

            disp[0][0] = [1.0, 1.0, 1.0]
            disp[0][20] = [1.0, 1.0, 1.0]
            # dip.imshow(disp)
            # dip.show()
            if asteroid1[0] > 0 and asteroid2[0] > 0 and asteroid3[0] > 0 and asteroid1[1] > 0 and asteroid2[1] > 0 and asteroid3[1] > 0and hor > 200 and ver > 200:
                name = FITS[0].name()
                with open("images/" + str(name) + ".txt", 'w') as info:
                    info.write("asteroid first location: " + str(asteroid1) + "\n")
                    info.write("asteroid first date: " + str(ast1date) + "\n")
                    info.write("asteroid second location: " + str(asteroid2) + "\n")
                    info.write("asteroid second location: " + str(ast2date) + "\n")
                    info.write("asteroid third location: " + str(asteroid3) + "\n")
                    info.write("asteroid third location: " + str(ast3date))

                plt.image.imsave("images/" + name + ".jpg", disp)
