
import dippykit as dip
import neowise_api as neo
from fits_file import Fits
import json
import numpy as np
from astropy import wcs
r = [0, 0, 255]
screen = np.zeros((3, 3, 3))
red = np.full((3, 3), 255)
green = np.zeros((3, 3))
blue = np.zeros((3, 3))

cake = np.stack((green, red, blue), axis=2)
screen[1][1] = r

print(screen)
# for i in range(len(image)):
#     for b in range(len(image[i])):
#         image[i, b] = pixel

dip.imshow(cake)
dip.show()
