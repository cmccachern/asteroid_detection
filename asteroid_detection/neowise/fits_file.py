"""
class for containing fits image and properties
"""

from astropy import wcs
import numpy as np


class Fits:
    """
    Fits file and associated data

    Parameters
    ------
    image : Numpy array
        fits file downloaded from neowise
    params : dict
        optional. data pertaining to the image including known asteroids

    """
    def __init__(self, image, params=None):
        self.image = image.data
        self.file = image
        self.name = params[0]
        self.params = params[1]['params']
        self.date = params[1]['asteroids'][0]['date']
        self.asteroids = params[1]['asteroids']

    def coordinates(self):
        """
        average NaN pixels to reduce noise,

        Returns
        -------
        [x], [y] : numpy array of type float
            (x, y) coordinates for asteroid in image
        """
        x_pos, y_pos = [], []
        coord = wcs.WCS(self.file)
        for astr in self.asteroids:
            x_temp, y_temp = coord.wcs_world2pix(float(astr['ra']),
                                                 float(astr['dec']), 0)
            x_pos.append(x_temp)
            y_pos.append(y_temp)
        return x_pos, y_pos

    @staticmethod
    def __avg(data, row, col):
        """
        average NaN pixels to reduce noise,

        Parameters
        ------
        data : Numpy array
            Image that is to be filtered
        row : int
            x position of pixel to be filtered
        col : int
            y position of pixel to be filtered

        Returns
        -------
        average : int or Nan
            Filtered pixel
        """
        total = 0
        count = 0
        for x_index in range(-1, 1):
            for y_index in range(-1, 1):
                if not np.isnan(data[row + x_index, col + y_index]):
                    total = total + data[row + x_index, col + y_index]
                    count = count + 1
        if count and not np.isnan(total):
            average = total / count
        else:
            average = total
        return average

    def filter_image(self):
        """
        average NaN pixels to reduce noise,

        Returns
        -------
        data : numpy array
            Filtered image
        """
        done = False
        while not done:
            done = True
            for y_index, row in enumerate(self.image):
                for x_index in range(len(row)):
                    if np.isnan(self.image[x_index, y_index]):
                        new_pixel = self.__avg(self.image, x_index, y_index)
                        if np.isnan(new_pixel):
                            done = False
                        else:
                            self.image[x_index, y_index] = new_pixel
