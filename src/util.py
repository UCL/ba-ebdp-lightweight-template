import geopandas as gpd
import numpy as np


def generate_points_along_perimeter(gdf: gpd.GeoDataFrame, spacing: int = 20):
    """Generates points along a polygon perimeter"""
    new_points = []
    new_attributes = []
    # iter GDF
    for _, row in gdf.iterrows():
        # extract polygon
        polygon = row.geometry
        # calculate number of points based on spacing
        length = polygon.length
        num_points = int(np.ceil(length / spacing))
        # for each spacing, generate a point
        for i in range(num_points):
            distance_along_perimeter = i * spacing
            # catch overshoots
            if distance_along_perimeter < length:
                # prepare the point and attribute data for output GDF
                point = polygon.interpolate(distance_along_perimeter)
                new_points.append(point)
                new_attributes.append(row.drop("geometry"))
    # prepare and return a new GDF
    new_gdf = gpd.GeoDataFrame(new_attributes, geometry=new_points)
    return new_gdf
