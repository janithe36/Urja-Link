# module_placement.py
import math
import geopandas as gpd
import numpy as np
from shapely.affinity import rotate
from shapely.ops import unary_union, transform
from shapely.geometry import MultiPolygon, Polygon, LineString

from definitions import (epsg_default, epsg_metric_germany, flat_roof_orientation_mode, flat_roof_space_util,
                         flat_roof_row_distance)
from spatial_operations import calculate_rotation_angle

# ... (most functions remain the same) ...

def module_placement(gdf_segments, azimuth_list, slope_list, gdf_superstructures, module_height, module_width):
    gdf_segments = gdf_segments.to_crs(epsg_metric_germany)
    gdf_superstructures = gdf_superstructures.to_crs(epsg_metric_germany)
    modules_possible_vertical_list, modules_possible_horizontal_list, alignment_list, azimuths = [], [], [], []
    for i, roof_segment in enumerate(gdf_segments.itertuples()):
        segment_shape = roof_segment.geometry
        if isinstance(segment_shape, MultiPolygon):
            segment_shape = segment_shape.geoms[0]
        
        intersecting_obstacles = []
        if not gdf_superstructures.empty:
            possible_matches = gdf_superstructures.sindex.intersection(segment_shape.bounds)
            for idx in possible_matches:
                obs = gdf_superstructures.geometry.iloc[idx]
                if obs.intersects(segment_shape):
                    intersecting_obstacles.append(obs.intersection(segment_shape))
        
        obstacles = unary_union(intersecting_obstacles) if intersecting_obstacles else MultiPolygon()

        if slope_list[i] == 0:
            alignment, modules_v, modules_h, azimuth = place_modules_flatroof(
                roof=segment_shape, obstacles=obstacles, module_height=module_height, module_width=module_width,
                slope=slope_list[i], mode=flat_roof_orientation_mode, space_util=flat_roof_space_util,
                row_distance=flat_roof_row_distance
            )
        else:
            alignment, modules_v, modules_h = place_modules(
                roof=segment_shape, obstacles=obstacles, module_height=module_height, module_width=module_width,
                slope=slope_list[i]
            )
            azimuth = azimuth_list[i]
        
        modules_possible_vertical_list.append(modules_v)
        modules_possible_horizontal_list.append(modules_h)
        alignment_list.append(alignment)
        azimuths.append(azimuth)

    gdf_modules_vertical = gpd.GeoDataFrame({"geometry": modules_possible_vertical_list}, crs=epsg_metric_germany).to_crs(epsg_default)
    gdf_modules_horizontal = gpd.GeoDataFrame({"geometry": modules_possible_horizontal_list}, crs=epsg_metric_germany).to_crs(epsg_default)
    return alignment_list, gdf_modules_vertical, gdf_modules_horizontal, azimuths

# ... (other functions remain the same) ...