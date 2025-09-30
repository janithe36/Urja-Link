import time
time.sleep(2)  # Wait 2 seconds to ensure files are unlocked

import argparse
import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon
from electricity_generation import pv_electricity_generation
from masks_to_vector import get_vector_labels, segment_simplify_and_add_azimuth
from definitions import *

# Constants
ORIENTATION_CLASSES = ['N', 'E', 'S', 'W', 'flat']
SUPERSTRUCTURE_CLASSES = [
    'chimney', 'dormer', 'ladder', 'pv_module',
    'shadow', 'tree', 'unknown', 'window'
]
MODULE_HEIGHT = 1.7  # meters
MODULE_WIDTH = 1.0   # meters


def create_dummy_orientation_gdf():
    """Create a minimal test GeoDataFrame with one polygon"""
    poly = Polygon([(100, 100), (400, 100), (400, 400), (100, 400)])
    gdf = gpd.GeoDataFrame({'orientation': ['N']}, geometry=[poly], crs="EPSG:4326")
    print(" Orientation mask empty. Using dummy test polygon.")
    return gdf


def main(args):
    # Step A: Extract vector labels
    print("\n[Step A] Extracting vector labels...")
    gdf_orientation = get_vector_labels(args.orientation_path, ORIENTATION_CLASSES, args.image_path)
    gdf_superstructures = get_vector_labels(args.superstructure_path, SUPERSTRUCTURE_CLASSES, args.image_path)

    # Debug prints
    print("DEBUG: Orientation GDF ->", gdf_orientation.shape, gdf_orientation.columns)
    print(gdf_orientation.head())
    print("DEBUG: Superstructures GDF ->", gdf_superstructures.shape, gdf_superstructures.columns)
    print(gdf_superstructures.head())

    # Export raw GDFs for inspection
    os.makedirs("debug_outputs", exist_ok=True)
    gdf_orientation.to_csv("debug_outputs/orientation_raw.csv", index=False)
    gdf_superstructures.to_csv("debug_outputs/superstructures_raw.csv", index=False)

    # Check for empty inputs
    if gdf_orientation.empty:
        gdf_orientation = create_dummy_orientation_gdf()
    if gdf_superstructures.empty:
        print(f" Superstructures GDF is empty. File: {args.superstructure_path}")

    # Step B: Process the vectors (segment simplification & azimuth)
    print("\n[Step B] Simplifying segments and adding azimuth...")
    gdf_segments_azimuth, gdf_superstructures_merged = segment_simplify_and_add_azimuth(
        gdf_orientation, gdf_superstructures
    )

    # Debug prints
    print("DEBUG: Segments Azimuth GDF ->", gdf_segments_azimuth.shape, gdf_segments_azimuth.columns)
    print(gdf_segments_azimuth.head())
    print("DEBUG: Superstructures Merged ->", gdf_superstructures_merged.shape, gdf_superstructures_merged.columns)
    print(gdf_superstructures_merged.head())

    # Export processed GDFs
    gdf_segments_azimuth.to_csv("debug_outputs/segments_azimuth.csv", index=False)
    gdf_superstructures_merged.to_csv("debug_outputs/superstructures_merged.csv", index=False)

    # Ensure geometry columns are active
    if "geometry" in gdf_segments_azimuth.columns:
        gdf_segments_azimuth = gdf_segments_azimuth.set_geometry("geometry")
    else:
        raise ValueError(
            " gdf_segments_azimuth has no 'geometry' column. Got: " + str(gdf_segments_azimuth.columns)
        )

    if "geometry" in gdf_superstructures_merged.columns:
        gdf_superstructures_merged = gdf_superstructures_merged.set_geometry("geometry")
    else:
        print(" Warning: gdf_superstructures_merged has no 'geometry' column, continuing with empty dataframe.")

    # Guards against empty data
    if gdf_segments_azimuth.empty:
        raise ValueError(" No roof segments detected. Check orientation_path and input images.")
    if gdf_superstructures_merged.empty:
        print(" Warning: No superstructures detected, continuing with empty dataframe.")

    # Step C: Calculate PV electricity generation
    print("\n[Step C] Calculating PV potential...")
    df_pv_results = pv_electricity_generation(
        gdf_segments_azimuth,
        gdf_superstructures_merged,
        MODULE_HEIGHT,
        MODULE_WIDTH,
        args.dir_pvgis_cache
    )

    # Step D: Save results
    print(f"\n[Step D] Saving PV results to {args.save_path_csv}...")
    os.makedirs(os.path.dirname(args.save_path_csv), exist_ok=True)
    df_pv_results.to_csv(args.save_path_csv, index=False)
    print(" PV potential calculation completed successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate PV potential for a campus/building")
    parser.add_argument("--image_path", required=True, help="Path to the input image")
    parser.add_argument("--orientation_path", required=True, help="Path to orientation mask")
    parser.add_argument("--superstructure_path", required=True, help="Path to superstructure mask")
    parser.add_argument("--save_path_csv", required=True, help="Path to save PV results CSV")
    parser.add_argument(
        "--dir_pvgis_cache",
        default="cache",  # Default PVGIS cache folder
        help="Directory for PVGIS cache (default: cache)"
    )
    args = parser.parse_args()
    main(args)
