import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from features import fits_from_rcf, align_images, jpg_resized, display_coordinates, find_asteroids

def get_moving_objects(filename = "~/Downloads/ADR4.dat"):
    df = pd.read_csv(filename, delim_whitespace=True)
    df.columns = ["moID", "Run", "Col", "Field", "Object", "rowc", "colc", "time", "ra", "dec"] + list(range(114))
    return df

def asteroids_in_rcf(df, run, camcol, field):
    df = df[df["Run"] == run]
    df = df[df["Col"] == camcol]
    df = df[df["Field"] == field]
     
    return df


if __name__ == "__main__":
    run, camcol, field = 752, 1, 321
    df = get_moving_objects()
    asteroids = asteroids_in_rcf(df, 752,1,321)
    fits_file = fits_from_rcf(run, camcol, field)
    images = align_images(fits_file) 
    jpg_img = jpg_resized(run, camcol, field, images["r"].shape)
    #save_coordinates(jpg_img, asteroids, "asteroids", run, camcol, field)
    asteroid_coordinates = np.array(list((zip(asteroids["rowc"], asteroids["colc"]))))
    asteroid_coordinates = np.round(asteroid_coordinates)
    asteroid_coordinates = asteroid_coordinates.astype(int)
    print(asteroid_coordinates)


    asteroids = find_asteroids(images, asteroid_coordinates)
    print(asteroids)

    display_coordinates(jpg_img, asteroid_coordinates)


