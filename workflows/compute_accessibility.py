# %%
import json

import geopandas as gpd
import pandas as pd
from cityseer.metrics import layers
from cityseer.tools import io
from landuse_schema_osm import SCHEMA
from osmnx import _errors as ox_errs
from osmnx import features
from pyproj import Transformer
from shapely import geometry
from shapely.wkt import loads

# location key for naming files
location_key = "nicosia"

# %%
# read the dataframes and set the indices
# when GPD are converted to GPKG the indices are converted to a column called "index"
nodes_gdf_dual_in = gpd.read_file(f"../temp/{location_key}_network_raw_nodes_dual.gpkg")
nodes_gdf_dual_in = nodes_gdf_dual_in.set_index("index")
edges_gdf_dual_in = gpd.read_file(f"../temp/{location_key}_network_raw_edges_dual.gpkg")
edges_gdf_dual_in = edges_gdf_dual_in.set_index("index")

# %%
# since the GPD were saved and reloaded network structure needs to be recreated
dual_nx = io.nx_from_cityseer_geopandas(nodes_gdf_dual_in, edges_gdf_dual_in)
# generate the network structure
nodes_gdf_dual, edges_gdf_dual, network_structure_dual = io.network_structure_from_nx(
    dual_nx, crs=3035
)
# manually copy across primal edge geoms
# this is done so that results can be visualised as lines instead of points
nodes_gdf_dual = nodes_gdf_dual.merge(
    nodes_gdf_dual_in[["primal_edge_geom"]],
    left_index=True,
    right_index=True,
    how="left",
)
# these were stored as WKT geometry so load to shapely geoms
nodes_gdf_dual["line_geometry"] = nodes_gdf_dual["primal_edge_geom"].apply(loads)
# Set this new column as the main geometry column
nodes_gdf_dual.set_geometry("line_geometry", inplace=True)
# set the CRS
nodes_gdf_dual["line_geometry"].set_crs("EPSG:3035", inplace=True)
# GPKG can only handle a single official geom column
# copy old geom column to point_geom as WKT
nodes_gdf_dual["point_geom"] = nodes_gdf_dual["geom"].to_wkt()
# drop old geom column
nodes_gdf_dual = nodes_gdf_dual.drop(columns=["geom"])

# %%
# recreate the boundary from the extents file
extents_gpd = gpd.read_file(f"../temp/{location_key}_boundary.gpkg")
# the input GPD has a single row representing the boundary
# fetch the row's geometry as a shapely geom
extents_geom_wgs = extents_gpd.iloc[0].geometry
# if the polygon is in a geographic coordinate system, e.g. WGS84 / EPSG:4326
# then convert it to a locally suitable projected CRS before buffering
# Define the coordinate transformation:
# - in this case the input geom is from OSM via EPSG:4326
# - in this case the output geom can uses EPSG:3035 which is appropriate for the EU
transformer_from_wgs = Transformer.from_crs("EPSG:4326", "EPSG:3035", always_xy=True)
# Apply the transformation to each point in the Polygon
extents_geom = geometry.Polygon(
    [transformer_from_wgs.transform(x, y) for x, y in extents_geom_wgs.exterior.coords]
)

# simplify the geometry, otherwise the OSM API migth complain of overly long URIs
extents_geom = extents_geom.convex_hull.simplify(100)

# buffer by the largest distance to be used for the largest accessibility analysis
# This is not technically necessary for the Cyprus example because it is an island.
extents_geom_buff = extents_geom.buffer(2000)
# convert back to WGS for passing to osmnx
transformer_to_wgs = Transformer.from_crs("EPSG:3035", "EPSG:4326", always_xy=True)
extents_geom_buff_wgs = geometry.Polygon(
    [transformer_to_wgs.transform(x, y) for x, y in extents_geom_buff.exterior.coords]
)

# %%
# download landuses from OSM and save in a GDF
# a list for accumulating the GDF
dfs = []
# iterate the categeory keys from the imported OSM landuse schema
for cat_key, val in SCHEMA.items():
    print(f"Retrieving {cat_key}")
    # iterate the nested OSM keys
    for osm_key, osm_vals in val.items():
        # fetch OSM data for each key and value pairing
        try:
            data_gdf = features.features_from_polygon(
                extents_geom_buff_wgs, tags={osm_key: osm_vals}
            )
        except ox_errs.InsufficientResponseError as e:
            print(e)
            continue
        # filter by nodes
        data_gdf = data_gdf.loc["node"]
        # reset the index
        data_gdf = data_gdf.reset_index(level=0, drop=True)
        data_gdf.index = data_gdf.index.astype(str)
        # add the category and OSM keys to the GDF
        data_gdf["cat_key"] = cat_key
        data_gdf["osm_key"] = osm_key
        # add the values as JSON
        data_gdf["osm_vals"] = json.dumps(osm_vals)
        # reduce the GDF to only the wanted columns
        data_gdf = data_gdf[["cat_key", "osm_key", "osm_vals", "geometry"]]
        # append to GDF list
        dfs.append(data_gdf)
# concatenate the list of GDF into a single GDF
landuses_gdf = pd.concat(dfs)
# reset the index
landuses_gdf = landuses_gdf.reset_index()
landuses_gdf.index = landuses_gdf.index.astype(str)
# has to be projected 3035 CRS
landuses_gdf = landuses_gdf.to_crs(3035)

# save landuses to a file
landuses_gdf.to_file(f"../temp/{location_key}_osm_landuses.gpkg")

# %%
# compute accessibilities
distances = [100, 200, 500, 1000, 2000]
# filter the below lost based on the quality of OSM contributions
# else use with discretion
nodes_gdf_dual, landuses_gdf = layers.compute_accessibilities(
    landuses_gdf,
    landuse_column_label="cat_key",
    accessibility_keys=[
        "drinking",
        "beverage",
        "eating",
        "children",
        "education",
        "transport",
        "healthcare",
        "office",
        "grocery_store",
        "retail_store",
        "civic",
        "entertainment",
        "religious",
        "service",
        "sport",
        "tourism",
    ],
    nodes_gdf=nodes_gdf_dual,
    network_structure=network_structure_dual,
    distances=distances,
    spatial_tolerance=50,
)
# compute mixed uses
nodes_gdf_dual, landuses_gdf = layers.compute_mixed_uses(
    landuses_gdf,
    landuse_column_label="cat_key",
    nodes_gdf=nodes_gdf_dual,
    network_structure=network_structure_dual,
    distances=distances,
    spatial_tolerance=50,
)

# %%
# save to file
nodes_gdf_dual.to_file(f"../temp/{location_key}_landuse_access.gpkg")
