import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from features import get_aligned_images, jpg_resized, display_coordinates, is_asteroid

def get_moving_objects(filename = "~/Downloads/ADR4.dat"):
    df = pd.read_csv(filename, delim_whitespace=True)
    df.columns = ["moID", "Run", "Col", "Field", "Object", "rowc", "colc", "time", "ra", "dec"] + list(range(114))
    return df

def asteroids_in_rcf(df, run, camcol, field):
    df = df[df["Run"] == run]
    df = df[df["Col"] == camcol]
    df = df[df["Field"] == field]
     
    return df

moving_objects = get_moving_objects()
def asteroid_coords_in_rcf(run, camcol, field):
    df = moving_objects#get_moving_objects()
    asteroids = asteroids_in_rcf(df, run, camcol, field)
    asteroid_coordinates = np.array(list((zip(asteroids["rowc"], asteroids["colc"]))))
    asteroid_coordinates = np.round(asteroid_coordinates)
    asteroid_coordinates = asteroid_coordinates.astype(int)
    return asteroid_coordinates

if __name__ == "__main__":
    run, camcol, field = 1033, 1, 147#752, 1, 321
    images = get_aligned_images(run, camcol, field)
    asteroid_coordinates = asteroid_coords_in_rcf(run, camcol, field)
    for coord in asteroid_coordinates:
        print(is_asteroid(images, coord))
#    asteroids = find_asteroids(images, asteroid_coordinates)
#    print(asteroids)

    jpg_img = jpg_resized(run, camcol, field, images["r"].shape)
    display_coordinates(jpg_img, asteroid_coordinates)


