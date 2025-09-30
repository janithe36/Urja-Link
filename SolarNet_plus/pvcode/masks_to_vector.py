import geopandas as gpd
from spatial_operations import raster_to_vector, simplify_polygon, find_longest_line

def get_vector_labels(mask_path, classes, image_path):
    print(f"Vectorizing labels from {mask_path}")
    return gpd.GeoDataFrame() 

def segment_simplify_and_add_azimuth(gdf_orientation, gdf_superstructures):
    print("Simplifying and adding azimuth")
    return gpd.GeoDataFrame(), gpd.GeoDataFrame()