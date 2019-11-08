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
        if item[1]['asteroids'][0]['date'][:9] == image[1]['asteroids'][0]['date'][:9]:
            if item[1]['asteroids'][0]['date'][11:13] != \
                    image[1]['asteroids'][0]['date'][11:13]:
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
    name = ['' for index in range(5)]
    images = []
    fits = []
    image_details = [cat_item for cat_item in catalog_items]
    total = np.zeros(2)
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
        x_coord, y_coord = fits[idx].coordinates(world=False)
        date_temp = fits[idx].date()
        total[0] += rad_asc[0]
        total[1] += declination[0]
        asteroid_xy.append([x_coord[0], y_coord[0]])
        date.append(date_temp[0])
        count += 1
        fits[idx].normalize()
        print('retrieved image ', idx + 1, '/', SIZE)
    center = total/count

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


def combine_images(asteroid_xy, fits, shift_x, shift_y):
    """
     combines images

     """
    canvas_r = np.zeros((WIDTH*3, HEIGHT*3))
    canvas_g = np.zeros((WIDTH*3, HEIGHT*3))
    canvas_b = np.zeros((WIDTH*3, HEIGHT*3))
    im1 = fits[0].image()
    im2 = fits[1].image()
    im3 = fits[2].image()

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

    restart = False
    if horizontal_overlap <= 0 or vertical_overlap <= 0:
        print('break!, overlap is less than 0')
        restart = True
        return 0, 0, 0, 0, restart

    disp = np.zeros((vertical_overlap, horizontal_overlap, 3))

    overlay = np.stack((canvas_r, canvas_g, canvas_b), axis=2)
    for col in range(vertical_overlap):
        for row in range(horizontal_overlap):
            for layer in range(3):
                disp[col][row][layer] = overlay[col + np.max(shift_y) + WIDTH,
                                                row + np.max(shift_x) + HEIGHT, layer]

    asteroid1 = [asteroid_xy[0][0] - (np.max(shift_x) + shift_x[0]),
                 asteroid_xy[0][1] - (np.max(shift_y)) + shift_y[0]]
    asteroid2 = [asteroid_xy[1][0] - (np.max(shift_x)) + shift_x[1],
                 asteroid_xy[1][1] - (np.max(shift_y)) + shift_y[1]]
    asteroid3 = [asteroid_xy[2][0] - (np.max(shift_x)) + shift_x[2],
                 asteroid_xy[2][1] - (np.max(shift_y)) + shift_y[2]]

    print('red asteroid position: ', asteroid1)
    print('green asteroid position: ', asteroid2)
    print('blue asteroid position: ', asteroid3)

    if np.max(asteroid1) < 0 or np.max(asteroid2) < 0 or np.max(asteroid3) < 0 \
            or horizontal_overlap < 200 or vertical_overlap < 200:
        restart = True

    return asteroid1, asteroid2, asteroid3, disp, restart


def save_files(date, asteroid1, asteroid2, asteroid3, fits, disp):
    """
     saves files

     """
    ast1date = date[0]
    ast2date = date[1]
    ast3date = date[2]

    name = fits[0].name()
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
    while GENERATE:

        picked_catalog_items = pick_images()
        if len(picked_catalog_items) < 3:
            break

        asteroid_positions, date_images, center_asteroid, fits_list = download_images(picked_catalog_items)
        if len(fits_list) < 3:
            print('break!, not enough fits files')
            break

        hor_shift, ver_shift = shift_images(center_asteroid, fits_list)
        if np.max(hor_shift) > WIDTH or np.max(ver_shift) > HEIGHT:
            print('break!, shift is greater than 1016')
            break

        ast_1, ast_2, ast_3, final_image, redo = \
            combine_images(asteroid_positions, fits_list, hor_shift, ver_shift)
        if redo:
            break

        save_files(date_images, ast_1, ast_2, ast_3, fits_list, final_image)


