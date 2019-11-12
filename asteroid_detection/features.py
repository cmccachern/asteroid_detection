"""
Functions for manipulating fits images to find asteroids.
"""

#pylint: disable=no-member
#pylint: disable=unsubscriptable-object


import numpy as np
from scipy.signal import correlate2d
import cv2
from astropy.io import fits
from astropy import wcs
import matplotlib.pyplot as plt
import logging

from sdss import fits_from_rcf, jpg_from_rcf

def plot_histogram(img):
    """
    Plot the RGB histogram of an image.
    """
    rgb_hist = rgb_histogram(img)
    plt.figure()
    for color, hist in rgb_hist.items():
        plt.plot(hist, color=color)
        plt.xlim([0, 256])

def rgb_histogram(img, channels=["r", "g", "b"]):
    """
    Find the rgb histogram
    """
    hist = {}
    for ii, color in enumerate(channels):
        hist[color] = cv2.calcHist([img], [ii], None, [256], [0, 256])
    return hist

def data_from_fits(fits_file):
    """
    Return the image data from a fits file.
    """
    hdul = fits.open(fits_file)
    data = hdul[0].data
    return data

def asteroid(img):
    """
    Hardcoded location for known asteroid in test image.
    """
    return img[170:205, 200:230]

def other_object(img):
    """
    Hardcoded location for non-asteroid object in test image.
    """
    return img[500:570, 1000:1070]

def galaxy(img):
    """
    Hardcoded location for galaxy in test image.
    """
    return img[420:490, 710:770]

def plot_object(fits_file, object_getter=asteroid):
    """
    Show the image of an object in a fits file.

    This function uses an object getter function to get the cropped data from a larger 2D array.
    """
    data = data_from_fits(fits_file)
    data = object_getter(data)
    plt.figure()
    plt.title(fits_file)
    plt.imshow(np.log10(data))

def plot_rgb(r_fits, g_fits, b_fits, object_getter=asteroid):
    """
    Plot an rgb image with area cropped by an object getter.
    """
    data = [None, None, None]
    for ii, fits_file in enumerate([r_fits, g_fits, b_fits]):
        data[ii] = data_from_fits(fits_file)
        data[ii] = object_getter(data[ii])
        plt.figure()
        plt.imshow(data[ii])

    data = np.dstack(data)
    plt.figure()
    plt.imshow(data)

def stack_images(data):
    img = np.dstack([data["r"], data["g"], data["i"]])
    plt.figure()
    plt.imshow(img)

def show_corls():
    """
    Test function that shows correlations between multiple fit files.
    """
    datar = data_from_fits("752_1_373_r.fits")
    datar = other_object(datar)
    datag = data_from_fits("752_1_373_g.fits")
    datag = other_object(datag)
    corl = correlate2d(datar, datag, mode="same")
    plt.figure()
    plt.imshow(corl)

    datar = data_from_fits("752_1_373_r.fits")
    datar = galaxy(datar)
    datag = data_from_fits("752_1_373_g.fits")
    datag = galaxy(datag)
    corl = correlate2d(datar, datag, mode="same")
    plt.figure()
    plt.imshow(corl)


    datar = data_from_fits("752_1_373_r.fits")
    datar = asteroid(datar)
    datag = data_from_fits("752_1_373_g.fits")
    datag = asteroid(datag)
    corl = correlate2d(datar, datag, mode="same")
    plt.figure()
    plt.imshow(corl)

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
    return np.unravel_index(corl_max, img1.shape)

def find_asteroids(images, crop_width=50, crop_height=50):
    """
    Use a correlation technique to find asteroids in images.
    """
    corl_maxes_rg = []
    corl_maxes_ri = []
    logging.info("Finding objects in image")
    objects = find_objects(images["r"])
    logging.info("{} objects found".format(len(objects)))
    logging.info("Running classifier on objects to find asteroids")
    asteroid_candidates = []
    for obj in objects:
        try:
            cropped_images = crop_all(images, obj, crop_width, crop_height)
        except OutOfBounds:
            continue

        corl_max_rg = np.array(max_corl_offset(cropped_images["r"], cropped_images["g"])) - np.array([25, 25])
        corl_max_ri = np.array(max_corl_offset(cropped_images["r"], cropped_images["i"])) - np.array([25, 25])
        #plt.imshow(cropped_images["r"])
        #plt.show()

        corl_maxes_rg.append(corl_max_rg)
        corl_maxes_ri.append(corl_max_ri)
        if np.sum(np.abs(corl_max_rg)) > 2 and \
           np.sum(np.abs(corl_max_ri)) > 2 and \
           np.sum(np.abs(corl_max_rg - corl_max_ri)) > 1:
            print(corl_max_rg, corl_max_ri)
            asteroid_candidates.append(obj)

    corl_maxes_rg = np.array(corl_maxes_rg)
    corl_maxes_ri = np.array(corl_maxes_ri)
    plt.figure()
    plt.scatter(corl_maxes_rg[:, 0], corl_maxes_rg[:,1])
    plt.figure()
    plt.scatter(corl_maxes_ri[:, 0], corl_maxes_ri[:,1])
    #plt.show()

    return np.array(asteroid_candidates)



def main():
    """
    Main function.
    """
    logging.basicConfig(level=logging.INFO)

    run = 752#756#752
    camcol = 1
    field = 373#314#373

    logging.info("Downloading FITS files")



    fits_file = fits_from_rcf(run, camcol, field)

    
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

    stack_images(images) 
    asteroids = find_asteroids(images)
        #plt.imshow(cropped_images["r"])
        #plt.show()
    print(asteroids)

    img = jpg_from_rcf(run, camcol, field)#plt.imread("image.jpg")
    plt.figure()
    plt.imshow(np.flipud(img))

    #plt.figure()
    #plt.imshow(np.log10(fits_file["r"][0].data))
    #plt.scatter(asteroids.T[1], asteroids.T[0], color="r")
    plt.show()

if __name__ == "__main__":
    main()
