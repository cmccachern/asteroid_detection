"""
Functions for manipulating fits images to find asteroids.
"""

#pylint: disable=no-member
#pylint: disable=unsubscriptable-object

import os
import numpy as np
import pandas as pd
from scipy.signal import correlate2d
import cv2
from astropy.io import fits
from astropy import wcs
import matplotlib.pyplot as plt
import logging

from sdss import fits_from_rcf, jpg_from_rcf

def data_from_fits(fits_file):
    """
    Return the image data from a fits file.
    """
    hdul = fits.open(fits_file)
    data = hdul[0].data
    return data

def stack_images(images):
    img = np.dstack([images["r"], images["g"], images["i"]])
    
    return img

def align_images(fits_file):
    w = wcs.WCS(fits_file["r"][0].header)
    x, y = 0, 0
    ra_temp, dec_temp = w.wcs_pix2world(x, y, 0)

    images =  {"r": fits_file["r"][0].data}

    for band in ["i", "g"]:
        hdul = fits_file[band]
        w = wcs.WCS(hdul[0].header)
        x_temp, y_temp = w.wcs_world2pix(ra_temp, dec_temp, 0)
        x_shift = -1*int(np.round(x_temp)) 
        y_shift = -1*int(np.round(y_temp)) 
        img = fits_file[band][0].data

        images[band] = np.roll(img, [x_shift, y_shift], [1,0])

    return images

def xy_to_celestial(fits_file, xy):
    celestial_coords = []
    for x, y in xy:
        w = wcs.WCS(fits_file["r"][0].header)
        ra, dec = w.wcs_pix2world(x, y, 0)
        celestial_coords.append([ra, dec])
    
    return celestial_coords

def mask_img(img, mask):
    """
    Return an image with all the masked data zeroed out.
    """
    masked_img = np.zeros(img.shape)
    masked_img[mask] = img[mask]
    return masked_img

def find_objects(img, threshold=.3):
    """
    Return an array of object centers from an image.
    """
    thresholded_img = np.uint8(img > threshold)
    _, markers = cv2.connectedComponents(thresholded_img)
    object_centers = []
    for ii in range(1, np.max(markers)):
        masked_img = mask_img(img, markers == ii)
        object_index = np.argmax(masked_img)
        object_center = np.unravel_index(object_index, img.shape)
        object_centers.append(object_center)
    return np.array(object_centers)

class OutOfBounds(Exception):
    """
    Error that is raised when trying to access image data that does not exist.
    """
    pass #pylint: disable=unnecessary-pass

def crop(img, center, width, height):
    """
    Crop an image.
    """
    left = int(center[0] - np.floor(width/2.0))
    right = left + width
    bottom = int(center[1] - np.floor(height/2.0))
    top = bottom + height

    if left < 0:
        raise OutOfBounds("Left side of crop window is outside of image")
    if bottom < 0:
        raise OutOfBounds("Bottom of crop window is outside of image")
    if right > img.shape[0]:
        raise OutOfBounds("Right side of crop window is outside of image")
    if top > img.shape[1]:
        raise OutOfBounds("Top of crop window is outside of image")

    return img[left:right, bottom:top]

def crop_all(images, center, width, height):
    """"
    Crop multiple bands of fits file image data
    """
    cropped_images = {}
    for band, img in images.items():
        cropped_images[band] = crop(img, center, width, height)
    return cropped_images

def max_corl_offset(img1, img2):
    """
    Return the maximum value in the cross correlation between two images.
    """
    assert img1.shape == img2.shape, "Images must be the same shape"
    corl = correlate2d(img1, img2, mode="same")
    corl_max = np.argmax(corl)
    corl_max = np.unravel_index(corl_max, img1.shape)
    return corl_max - np.floor(np.array(img1.shape)/2)

def find_asteroids(images, objects, crop_width=51, crop_height=51):
    """
    Use a correlation technique to find asteroids in images.
    """
    corl_maxes_rg = []
    corl_maxes_ri = []
    logging.info("Running classifier on objects to find asteroids")
    asteroid_candidates = []
    for obj in objects:
        try:
            cropped_images = crop_all(images, obj, crop_width, crop_height)
        except OutOfBounds:
            continue

        corl_max_rg = np.array(max_corl_offset(cropped_images["r"], cropped_images["g"]))
        corl_max_ri = np.array(max_corl_offset(cropped_images["r"], cropped_images["i"]))

        corl_maxes_rg.append(corl_max_rg)
        corl_maxes_ri.append(corl_max_ri)
        if np.sum(np.abs(corl_max_rg)) + np.sum(np.abs(corl_max_ri)) > 5:
            print(corl_max_rg, corl_max_ri)
            asteroid_candidates.append(obj)

    return np.array(asteroid_candidates)

def jpg_resized(run, camcol, field, shape):
    img = jpg_from_rcf(run, camcol, field)
    img = np.flipud(img)
    img = cv2.resize(np.array(img), (shape[1], shape[0]))
    return img

def display_coordinates(img, coordinates):
    plt.figure()
    plt.imshow(img)
    plt.figure()
    for coord in coordinates:
        plt.figure()
        plt.imshow(crop(img, coord, 100,100))
    plt.show()

def save_coordinates(img, coordinates, directory, run, camcol, field):
    for coord in coordinates:
        filename = os.path.join(directory, "{}_{}_{}_{}_{}.jpg".format(run, camcol, field, coord[0], coord[1]))
        logging.info("Saving {}".format(filename))
        cropped = crop(img, coord, 100, 100)
        cv2.imwrite(filename, cropped)



def main():
    """
    Main function.
    """
    logging.basicConfig(level=logging.INFO)

    run = 756#756#752
    camcol = 1
#    field = 319#373#314#373

    classifications = pd.DataFrame(columns = ["run", "camcol", "field", "right_ascension", "declination",
                                              "img_x", "img_y", "is_asteroid"])

    for field in range(300, 400):
        try:
            logging.info("Downloading FITS files")

            fits_file = fits_from_rcf(run, camcol, field)
            
            images = align_images(fits_file) 
            logging.info("Finding objects in image")
            objects = find_objects(images["r"])
            logging.info("{} objects found".format(len(objects)))
            asteroids = find_asteroids(images, objects)
            for obj in objects:
                is_asteroid = obj in asteroids
                x, y = obj
                right_ascension, declination =  xy_to_celestial(fits_file, [[x, y]])[0]
                classifications = classifications.append({"run" : run, "camcol" : camcol, "field" : field,
                                        "right_ascension": right_ascension, "declination": declination,
                                        "img_x": x, "img_y": y,
                                        "is_asteroid": is_asteroid},
                                        ignore_index=True)
            classifications.to_csv("classifications.csv")                 


            jpg_img = jpg_resized(run, camcol, field, images["r"].shape)
            save_coordinates(jpg_img, asteroids, "asteroids", run, camcol, field)
        except:
            logging.error("Error in processing; continuing with next image")
#    display_coordinates(run, camcol, field, asteroids)

if __name__ == "__main__":
    main()
