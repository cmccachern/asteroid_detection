import logging
import pandas as pd
import numpy as np
import os
from features import get_aligned_images, is_asteroid
from sdss_moving_objects import asteroid_coords_in_rcf


def false_negative(classifier):
    #runs = [752, 756]
    runs = [1033, 1035, 1037, 1040, 1043, 1045, 1056, 1122, 1140, 1231, 1239, 1241]
    fields = range(100, 400)
    camcol = 1

    if os.path.isfile("performance.csv"):
        df = pd.read_csv("performance.csv")
    else:
        df = pd.DataFrame(columns = ["run", "camcol", "field", "x", "y", "is_asteroid"])

    for run in runs:
        for field in fields:
            asteroids_classified = len(df)
            correct_classifications = np.sum(df["is_asteroid"])
            percent_correct = 100*correct_classifications/asteroids_classified
            print("Correct Classifications: {}/{} - {}%".format(correct_classifications, asteroids_classified, percent_correct))
            if len(df[np.logical_and(df["run"] == run, df["field"] == field)]) != 0:
                print("Skipping")
                continue
            asteroid_coordinates = asteroid_coords_in_rcf(run, camcol, field)
            if len(asteroid_coordinates) == 0:
                print("No asteroids in image; skipping")
                continue
            logging.info("Running classifier on images in run = {}, camcol = {}, field = {}".format(run, camcol, field))
            images = get_aligned_images(run, camcol, field)
            for coord in asteroid_coordinates:
                df = df.append({"run": run, "camcol": camcol, "field": field, "x": coord[0], "y": coord[0],
                                "is_asteroid": classifier(images, coord)}, ignore_index=True)
                df.to_csv("performance.csv")

def remove_nearby_objects(objects, asteroids):
    distant_objects = []
    for obj in objects:
        if np.any(np.mag(asteroids - obj) < 100):
            continue
        else:
            distant_objects.append(obj)
    return distant_objects
 
def false_positive():
    #runs = [752, 756, 1033, 1035, 1037, 1040, 1043, 1045, 1056, 1122, 1140, 1231, 1239, 1241]
    runs = [1033, 1035, 1037, 1040, 1043, 1045, 1056, 1122, 1140, 1231, 1239, 1241]
    fields = range(300, 400)
    camcol = 1

    if os.path.isfile("performance_fp.csv"):
        df = pd.read_csv("performance_fp.csv")
    else:
        df = pd.DataFrame(columns = ["run", "camcol", "field", "x", "y", "is_asteroid"])

    for run in runs:
        for field in fields:
            classifications = len(df)
            #correct_classifications = np.sum(!df["is_asteroid"])
            
            asteroid_coordinates = asteroid_coords_in_rcf(run, camcol, field)
            objects = find_objects(get_aligned_images(run, camcol, field)["r"])
            objects = remove_nearby_objects(objects, asteroid_coordinates)

            for coord in objects:
                df = df.append({"run": run, "camcol": camcol, "field": field, "x": coord[0], "y": coord[0],
                                "is_asteroid": classifier(images, coord)}, ignore_index=True)
                df.to_csv("performance_fp.csv")
 
 




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
              
    false_negative(is_asteroid)
