"""
example code, will show a random FITS image
"""

import neowise_api as neo
from fits_file import Fits
import json
import matplotlib.image as mpimg
import numpy as np
from astropy import wcs
import warnings
from astropy.utils.exceptions import AstropyWarning

WIDTH = 1016
HEIGHT = 1016
UPDATE = True
GENERATE = True

warnings.simplefilter('ignore', category=AstropyWarning)

with open('asteroid_CATALOG.json', 'r') as file:
    CATALOG = json.load(file)
CATALOG = list(CATALOG.items())


def generate_images():
    while GENERATE:
        print('Beginning find and generate image...')
        random_catalog_index = np.random.randint(len(CATALOG))
        item = CATALOG[int(random_catalog_index)]
        catalog_items = [item]

        canvas_r = np.zeros((WIDTH*3, HEIGHT*3))
        canvas_g = np.zeros((WIDTH*3, HEIGHT*3))
        canvas_b = np.zeros((WIDTH*3, HEIGHT*3))
        placeholder = 'ab'

        for image in CATALOG:
            if item[1]['asteroids'][0]['date'][:9] == image[1]['asteroids'][0]['date'][:9]:
                if item[1]['asteroids'][0]['date'][11:13] != \
                        image[1]['asteroids'][0]['date'][11:13]:
                    if image[1]['asteroids'][0]['date'][11:13] != placeholder:
                        placeholder = image[1]['asteroids'][0]['date'][11:13]
                        for ast in range(len(image[1]['asteroids'])):
                            if item[1]['asteroids'][0]['name'] == \
                                    image[1]['asteroids'][ast]['name']:
                                catalog_items.append(image)
        placeholder = 'ab'

        if len(catalog_items) < 3:
            break

        NAME = ['' for index in range(5)]
        IMAGE = []
        FITS = []
        IMAGE_DETAILS = [catalog_item for catalog_item in catalog_items]
        total = np.zeros(2)
        center = [0, 0]
        count = 0
        ra = 0
        dec = 0
        size = 3
        ast = []
        date = []
        cutout = []

        for idx in range(size):
            NAME[idx] = IMAGE_DETAILS[idx][0]
            IMAGE.append(neo.download_fits(NAME[idx]))
            FITS.append(Fits(IMAGE[idx], IMAGE_DETAILS[idx]))
            FITS[idx].filter_image()
            FITS[idx].scale_image()
            FITS[idx].name()
            ra, dec = FITS[idx].coordinates(world=True)
            x, y = FITS[idx].coordinates(world=False)
            date_temp = FITS[idx].date()
            total[0] += ra[0]
            total[1] += dec[0]
            ast.append([x[0], y[0]])
            date.append(date_temp[0])
            count += 1
            FITS[idx].normalize()
            print('retrieved image ', idx + 1, '/', size)
        center = total/count

        if len(FITS) < 3:
            print('break!, not enough FITS files')
            break

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
            else:
                shift_x[idx], shift_y[idx] = int(center_x - x_temp), int(center_y - y_temp)
        print('images are shifted in x direction: ', shift_x,
              '\nimages are shifted in y direction: ', shift_y)

        if np.max(shift_x) > WIDTH or np.max(shift_y) > HEIGHT:
            print('break!, shift is greater than 1016')
            break

        for col in range(WIDTH):
            for pixel in range(HEIGHT):
                canvas_r[pixel + HEIGHT + shift_y[0]][col + WIDTH + shift_x[0]]\
                    = im1[pixel][col]
                canvas_g[pixel + HEIGHT + shift_y[1]][col + WIDTH + shift_x[1]]\
                    = im2[pixel][col]
                canvas_b[pixel + HEIGHT + shift_y[2]][col + WIDTH + shift_x[2]]\
                    = im3[pixel][col]

        horizontal_overlap = WIDTH - np.abs(np.max(shift_x) - np.min(shift_x))
        vertical_overlap = HEIGHT - np.abs(np.max(shift_y) - np.min(shift_y))
        print('combined image size: ', horizontal_overlap, 'x', vertical_overlap)

        if horizontal_overlap <= 0 or vertical_overlap <= 0:
            print('break!, overlap is less than 0')
            break

        disp = np.zeros((vertical_overlap, horizontal_overlap, 3))

        overlay = np.stack((canvas_r, canvas_g, canvas_b), axis=2)
        for col in range(vertical_overlap):
            for row in range(horizontal_overlap):
                for layer in range(3):
                    disp[col][row][layer] = overlay[col + np.max(shift_y) + WIDTH,
                                                    row + np.max(shift_x) + HEIGHT, layer]

        asteroid1 = [ast[0][0] - (np.max(shift_x) + shift_x[0]),
                     ast[0][1] - (np.max(shift_y)) + shift_y[0]]
        asteroid2 = [ast[1][0] - (np.max(shift_x)) + shift_x[1],
                     ast[1][1] - (np.max(shift_y)) + shift_y[1]]
        asteroid3 = [ast[2][0] - (np.max(shift_x)) + shift_x[2],
                     ast[2][1] - (np.max(shift_y)) + shift_y[2]]
        ast1date = date[0]
        ast2date = date[1]
        ast3date = date[2]
        print('red asteroid position: ', asteroid1)
        print('green asteroid position: ', asteroid2)
        print('blue asteroid position: ', asteroid3)

        if asteroid1[0] > 0 and asteroid2[0] > 0 and asteroid3[0] > 0 \
                and asteroid1[1] > 0 and asteroid2[1] > 0 and asteroid3[1] > 0 \
                and horizontal_overlap > 200 and vertical_overlap > 200:
            name = FITS[0].name()
            print('saving text file...')
            with open("images/" + str(name) + ".txt", 'w') as info:
                info.write("asteroid first location: " + "\n" + str(asteroid1) + "\n")
                info.write("asteroid first date: " + "\n" + str(ast1date) + "\n")
                info.write("asteroid second location: " + "\n" + str(asteroid2) + "\n")
                info.write("asteroid second location: " + "\n" + str(ast2date) + "\n")
                info.write("asteroid third location: " + "\n" + str(asteroid3) + "\n")
                info.write("asteroid third location: " + "\n" + str(ast3date))
            print(name + '.txt', 'text file saved')
            print('saving image...')
            mpimg.imsave("images/" + name + ".png", disp)
            print(name + '.png', 'image saved')


while UPDATE:
    generate_images()
