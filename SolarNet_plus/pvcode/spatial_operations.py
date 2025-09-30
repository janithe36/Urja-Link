import rasterio
import cv2
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon, box
from utils import get_progress_string

def find_longest_line(polygon):
    ring_xy = polygon.exterior.coords.xy
    x_coords, y_coords = list(ring_xy[0]), list(ring_xy[1])
    longest_line_length = 0
    longest_line_coords = None
    for i in range(len(x_coords) - 1):
        length = np.sqrt((x_coords[i+1] - x_coords[i])**2 + (y_coords[i+1] - y_coords[i])**2)
        if length > longest_line_length:
            longest_line_length = length
            longest_line_coords = [(x_coords[i], y_coords[i]), (x_coords[i+1], y_coords[i+1])]
    return longest_line_coords

def raster_to_vector(mask, id, image_bbox, CLASSES, bg_is_0=False):
    label_list, geometry_list = [], []
    image_shape = mask.shape
    for i, class_id in enumerate(CLASSES):
        prediction = np.zeros(image_shape, dtype=np.uint8)
        if bg_is_0:
            prediction[mask == i + 1] = 1
        else:
            prediction[mask == i] = 1
        if np.sum(prediction) > 0:
            contours, _ = cv2.findContours(prediction, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                if len(cnt) >= 3:
                    try:
                        pol = Polygon(cnt.reshape(-1, 2))
                        geometry_list.append(pol)
                        label_list.append(CLASSES[i])
                    except ValueError:
                        continue
    # Placeholder for a function that needs to be defined or imported
    # transformed_geoms = [convert_geocoord_and_pixel(g, image_bbox_px, image_bbox) for g in geometry_list]
    return gpd.GeoDataFrame({'id': [id] * len(label_list), 'label': label_list, 'geometry': geometry_list})

def simplify_polygon(polygon, tolerance=1):
    return polygon.simplify(tolerance, preserve_topology=True)