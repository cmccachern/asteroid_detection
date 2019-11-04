import neowise as neo
import numpy as np
import dippykit as dip

# example code, will show a random fits image
image_details = neo.find_params()
name = image_details[0]
print(image_details[1])
fits = neo.download_fits(name)
fits.data = neo.filter_image(fits.data)
fits.data = np.clip(fits.data, np.median(fits.data), np.max(fits.data))
fits.data = np.log(fits.data - np.median(fits.data) + 1)
fits.data = np.clip(fits.data, 0.3*np.max(fits.data), np.max(fits.data))
dip.imshow(fits.data, cmap='gist_heat')
dip.colorbar()
dip.show()


