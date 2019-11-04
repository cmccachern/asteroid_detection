=================================
Move images according to position
=================================

The code to convert between world and pixel coordinates:

.. code-block:: python

    from astropy import wcs

    # Save Fits file header data necessary to calculate coordinates
    coord = wcs.WCS(FITS_FILE)

    # convert world coordinates to pixel coordinates
    x_temp, y_temp = coord.wcs_world2pix(ra, dec, 0)

    # convert pixel coordinates to world coordinates
    ra_temp, dec_temp = coord.pix2world(x, y, 0)

For more information `look here: https://docs.astropy.org/en/stable/wcs/`_.

In order to translate images and overlay them, one world coordinate (ra, dec)
is converted to pixel coordinates in each image. Two of the three images are then
shifted to match the coordinates of the remaining image.

All the images are then then stacked with

>>> np.stack((image1, image2, image3), axis=2)

The image is then cropped according to the size of the overlap. Unfortunately sometimes
one of the asteroids is in a position not visible in other images, causing it to be
cropped out of the whole image.

