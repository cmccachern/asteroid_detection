"""
example code, will show a random fits image
"""

import json
import warnings
import matplotlib.image as mpimg
import numpy as np
from astropy.utils.exceptions import AstropyWarning
from astropy import wcs
import neowise_api as neo
from fits_file import Fits

WIDTH = 1016
HEIGHT = 1016
UPDATE = True
GENERATE = True
SIZE = 3


warnings.simplefilter('ignore', category=AstropyWarning)

with open('asteroid_CATALOG.json', 'r') as file:
    CATALOG = json.load(file)
CATALOG = list(CATALOG.items())


def pick_images():
    """
     picks images from a list

     """
    print('Beginning find and generate image...')
    random_catalog_index = np.random.randint(len(CATALOG))
    item = CATALOG[int(random_catalog_index)]
    catalog_items = [item]

    placeholder = 'ab'
    for image in CATALOG:
        if (item[1]['asteroids'][0]['date'][:9] == image[1]['asteroids'][0]['date'][:9]) and \
                (item[1]['asteroids'][0]['date'][11:13] !=
                 image[1]['asteroids'][0]['date'][11:13]):
            if image[1]['asteroids'][0]['date'][11:13] != placeholder:
                placeholder = image[1]['asteroids'][0]['date'][11:13]
                for ast in range(len(image[1]['asteroids'])):
                    if item[1]['asteroids'][0]['name'] == \
                            image[1]['asteroids'][ast]['name']:
                        catalog_items.append(image)
    return catalog_items


def download_images(catalog_items):
    """
     downloads, images

     """
    name = [''] * 5
    images = []
    fits = []
    image_details = [cat_item for cat_item in catalog_items]
    center = np.zeros(2)
    count = 0
    asteroid_xy = []
    date = []

    for idx in range(SIZE):
        name[idx] = image_details[idx][0]
        images.append(neo.download_fits(name[idx]))
        fits.append(Fits(images[idx], image_details[idx]))
        fits[idx].filter_image()
        fits[idx].scale_image()
        fits[idx].name()
        rad_asc, declination = fits[idx].coordinates(world=True)
        center[0] = rad_asc[0]
        center[1] = declination[0]
        x_coord, y_coord = fits[idx].coordinates(world=False)
        date_temp = fits[idx].date()
        asteroid_xy.append([x_coord[0], y_coord[0]])
        date.append(date_temp[0])
        count += 1
        fits[idx].normalize()
        print('retrieved image ', idx + 1, '/', SIZE)
    return asteroid_xy, date, center, fits


def shift_images(center, fits):
    """
     shifts and translates images

     """

    center_x, center_y = 0, 0
    shift_x = [0, 0, 0]
    shift_y = [0, 0, 0]

    for idx in range(SIZE):
        coord = wcs.WCS(fits[idx].file())
        x_temp, y_temp = coord.wcs_world2pix(center[0], center[1], 0)
        if idx == 0:
            center_x, center_y = x_temp, y_temp
        else:
            shift_x[idx], shift_y[idx] = int(center_x - x_temp), int(center_y - y_temp)
    print('images are shifted in x direction: ', shift_x,
          '\nimages are shifted in y direction: ', shift_y)

    return shift_x, shift_y


def overlap(vertical_overlap, horizontal_overlap, shift_x, shift_y):
    """
        combines images

    """
    disp = np.zeros((vertical_overlap, horizontal_overlap, 3))
    overlay = np.stack((CANVAS_R, CANVAS_G, CANVAS_B), axis=2)
    for col in range(vertical_overlap):
        for row in range(horizontal_overlap):
            for layer in range(3):
                disp[col][row][layer] = overlay[col + np.max(shift_y) + WIDTH,
                                                row + np.max(shift_x) + HEIGHT, layer]
    return disp


def combine_images(asteroid_xy, fits, shift_x, shift_y):
    """
     combines images

     """
    fits_image = [fits[0].image(), fits[1].image(), fits[2].image()]

    for col in range(WIDTH):
        for pixel in range(HEIGHT):
            CANVAS_R[pixel + HEIGHT + shift_y[0]][col + WIDTH + shift_x[0]]\
                = fits_image[0][pixel][col]
            CANVAS_G[pixel + HEIGHT + shift_y[1]][col + WIDTH + shift_x[1]]\
                = fits_image[1][pixel][col]
            CANVAS_B[pixel + HEIGHT + shift_y[2]][col + WIDTH + shift_x[2]]\
                = fits_image[2][pixel][col]

    horizontal_overlap = WIDTH - np.abs(np.max(shift_x) - np.min(shift_x))
    vertical_overlap = HEIGHT - np.abs(np.max(shift_y) - np.min(shift_y))
    print('combined image size: ', horizontal_overlap, 'x', vertical_overlap)

    if horizontal_overlap <= 0 or vertical_overlap <= 0:
        print('break!, overlap is less than 0')
        return 0, 0, True
    display = overlap(vertical_overlap, horizontal_overlap, shift_x, shift_y)

    asteroid = [[asteroid_xy[0][0] - (np.max(shift_x) + shift_x[0]),
                 asteroid_xy[0][1] - (np.max(shift_y)) + shift_y[0]],
                [asteroid_xy[1][0] - (np.max(shift_x)) + shift_x[1],
                 asteroid_xy[1][1] - (np.max(shift_y)) + shift_y[1]],
                [asteroid_xy[2][0] - (np.max(shift_x)) + shift_x[2],
                 asteroid_xy[2][1] - (np.max(shift_y)) + shift_y[2]]]

    print('red asteroid position: ', asteroid[0])
    print('green asteroid position: ', asteroid[1])
    print('blue asteroid position: ', asteroid[2])

    if np.max(asteroid[0]) < 0 or np.max(asteroid[1]) < 0 or np.max(asteroid[2]) < 0 \
            or horizontal_overlap < 200 or vertical_overlap < 200:
        return asteroid, display, True

    return asteroid, display, False


def save_files(date, asteroid, fits, disp):
    """
     saves files

     """
    ast1date = date[0]
    ast2date = date[1]
    ast3date = date[2]

    name = fits[0].name()
    print('saving text file...')
    with open("images/" + str(name) + ".txt", 'w') as info:
        info.write("asteroid first location: " + "\n" + str(asteroid[0]) + "\n")
        info.write("asteroid first date: " + "\n" + str(ast1date) + "\n")
        info.write("asteroid second location: " + "\n" + str(asteroid[1]) + "\n")
        info.write("asteroid second location: " + "\n" + str(ast2date) + "\n")
        info.write("asteroid third location: " + "\n" + str(asteroid[2]) + "\n")
        info.write("asteroid third location: " + "\n" + str(ast3date))
    print(name + '.txt', 'text file saved')
    print('saving image...')
    mpimg.imsave("images/" + name + ".png", disp)
    print(name + '.png', 'image saved')


while UPDATE:
    while GENERATE:

        CANVAS_R = np.zeros((WIDTH * 3, HEIGHT * 3))
        CANVAS_G = np.zeros((WIDTH * 3, HEIGHT * 3))
        CANVAS_B = np.zeros((WIDTH * 3, HEIGHT * 3))

        PICKED_IMAGES = pick_images()
        if len(PICKED_IMAGES) < 3:
            break

        ASTEROID_POSITIONS, DATE_IMAGES, CENTER_ASTEROID, FITS_LIST = \
            download_images(PICKED_IMAGES)
        if len(FITS_LIST) < 3:
            print('break!, not enough fits files')
            break

        HOR_SHIFT, VER_SHIFT = shift_images(CENTER_ASTEROID, FITS_LIST)
        if np.max(HOR_SHIFT) > WIDTH or np.max(VER_SHIFT) > HEIGHT:
            print('break!, shift is greater than 1016')
            break

        ASTEROID, FINAL_IMAGE, REDO = \
            combine_images(ASTEROID_POSITIONS, FITS_LIST, HOR_SHIFT, VER_SHIFT)
        if REDO:
            break

        save_files(DATE_IMAGES, ASTEROID, FITS_LIST, FINAL_IMAGE)
