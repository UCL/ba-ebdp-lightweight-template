# %%
import geopandas as gpd
import momepy
from osmnx import features

# location key for naming files
location_key = "nicosia"

# %%
# recreate the boundary from the extents file
extents_gpd = gpd.read_file(f"../temp/{location_key}_boundary.gpkg")
# the input GPD has a single row representing the boundary
# fetch the row's geometry as a shapely geom
extents_geom_wgs = extents_gpd.iloc[0].geometry

# %%
bldgs_gdf = features.features_from_polygon(extents_geom_wgs, tags={"building": True})
# extract ways
bldgs_gdf = bldgs_gdf[bldgs_gdf.index.get_level_values("element_type") == "way"]
# remove double index
bldgs_gdf = bldgs_gdf.reset_index(level="element_type", drop=True).rename_axis("fid")
# extract only wanted columns
bldgs_gdf = bldgs_gdf[
    [
        "height",
        "name",
        "geometry",
    ]
]
# filter geometries
bldgs_gdf = bldgs_gdf[bldgs_gdf["geometry"].type.isin(["Polygon", "MultiPolygon"])]
# project
bldgs_gdf = bldgs_gdf.to_crs(3035)
# %%
# calculate momepy stats
# these are some examples, see the momepy docs for more options
bldgs_gdf["area"] = momepy.Area(bldgs_gdf).series
bldgs_gdf["perimeter"] = momepy.Perimeter(bldgs_gdf).series
bldgs_gdf["circular_compact"] = momepy.CircularCompactness(bldgs_gdf).series
bldgs_gdf["square_compactness"] = momepy.SquareCompactness(bldgs_gdf).series
bldgs_gdf["shared_walls"] = momepy.SharedWalls(bldgs_gdf).series
bldgs_gdf["shared_walls_ratio"] = momepy.SharedWallsRatio(bldgs_gdf, "perimeter").series
# rename to geom
bldgs_gdf = bldgs_gdf.rename_geometry("geom")
# %%
# save to file
bldgs_gdf.to_file(f"../temp/{location_key}_buildings.gpkg")
