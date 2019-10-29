"""
class for containing fits image and properties
"""

import copy
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
        self._image = copy.deepcopy(image.data)
        self._file = image
        self._name = params[0]
        self._params = params[1]['params']
        self._date = params[1]['asteroids'][0]['date']
        self._asteroids = params[1]['asteroids']

    def coordinates(self, world=False):
        """
        average NaN pixels to reduce noise,

        Returns
        -------
        [x], [y] : numpy array of type float
            (x, y) coordinates for asteroid in image
        """
        x_pos, y_pos = [], []
        coord = wcs.WCS(self._file)
        for astr in self._asteroids:
            if not world:
                x_temp, y_temp = coord.wcs_world2pix(float(astr['ra']),
                                                     float(astr['dec']), 0)
            else:
                x_temp, y_temp = float(astr['ra']), float(astr['dec'])

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

    def filter_image(self, original_image=None):
        """
        average NaN pixels to reduce noise,

        Returns
        -------
        data : numpy array
            Filtered image
        """
        if original_image:
            self._image = self._file.data
        temp_image = self._image
        done = False
        while not done:
            done = True
            for y_index, row in enumerate(temp_image):
                for x_index in range(len(row)):
                    if np.isnan(temp_image[x_index, y_index]):
                        new_pixel = self.__avg(temp_image, x_index, y_index)
                        if np.isnan(new_pixel):
                            done = False
                        else:
                            self._image[x_index, y_index] = new_pixel

    def scale_image(self, min_factor=None, max_factor=None, original_image=None):
        if original_image:
            temp_image = self._file.data
            print('wtf')
        else:
            temp_image = self._image
        temp_image[temp_image < np.median(temp_image)] = np.median(temp_image)
        temp_image = np.log(temp_image - np.min(temp_image) + 1)
        if not max_factor:
            max_factor = 1
        if not min_factor:
            min_factor = 0.3
        self._image = np.clip(temp_image, min_factor * np.max(temp_image),
                              max_factor * np.max(temp_image))

    def normalize(self, original_image=None):
        if original_image:
            temp_image = self._file.data
        else:
            temp_image = self._image
        temp_image = temp_image - np.min(temp_image)
        denominator = np.max(temp_image) - np.min(temp_image)
        self._image = temp_image / denominator

    def image(self):
        return self._image

    def circle_asteroid(self, original_image=None):
        if original_image:
            temp_image = self._file.data
        else:
            temp_image = self._image
        x_pos, y_pos = self.coordinates()
        thickness = 1
        for i in range(len(temp_image)):
            for a in range(len(temp_image[i])):
                if 60 - thickness < np.sqrt(np.square(y_pos[0]-i) + np.square(x_pos[0]-a)) < thickness + 60:
                    temp_image[i, a] = np.max(temp_image)

    # def scale(self, original_image=None):
    #     if original_image:
    #         temp_image = self._file.data
    #     else:
    #         temp_image = self._image
    #     temp_image = temp_image - np.min(temp_image)
    #     denominator = np.max(temp_image) - np.min(temp_image)
    #     self._image = temp_image / denominator