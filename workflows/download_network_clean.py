"""
This workbook shows how to algorithmically clean a network
It requires some time to experiment with the underlying parameters
In many cases it may be preferable to use the raw network workflow instead

After algorithmic cleaning, inspect the network in QGIS
The automated cleaning parameters can then be modified and iterated
Finally, edit the network directly in QGIS

Once happy with the network, continue with STEP 2
"""

# %%
import geopandas as gpd
from cityseer.tools import graphs, io
from pyproj import Transformer
from shapely import geometry

# location key for naming files
location_key = "cyprus"

# read the extents file
extents_gpd = gpd.read_file(f"../temp/{location_key}_boundary.gpkg")
extents_gpd

# %%
# STEP 1 - fetch and clean the network

# the input GPD has a single row representing the boundary
# fetch the row's geometry as a shapely geom
extents_geom_wgs = extents_gpd.iloc[0].geometry

# if the polygon is in a geographic coordinate system, e.g. WGS84 / EPSG:4326
# then convert it to a locally suitable projected CRS before buffering
# Define the coordinate transformation:
# - in this case the input geom is from OSM via EPSG:4326
# - in this case the output geom can uses EPSG:6312 which is appropriate for Cyprus
transformer = Transformer.from_crs("EPSG:4326", "EPSG:6312", always_xy=True)
# Apply the transformation to each point in the Polygon
extents_geom = geometry.Polygon(
    [transformer.transform(x, y) for x, y in extents_geom_wgs.exterior.coords]
)

# simplify the geometry, otherwise the OSM API might complain of overly long URIs
extents_geom = extents_geom.convex_hull.simplify(100)

# buffer by the largest distance to be used for the largest centralities or accessibility analysis
# This is not technically necessary for the Cyprus example because it is an island.
extents_geom_buff = extents_geom.buffer(10000)

# %%
# this will download the OSM network with full simplification
# specify the input and output EPSG CRS appropriate to the case
# this is returned as a networkX graph
# set simplify to False so that the steps can be done manually per below
G_clean = io.osm_graph_from_poly(
    extents_geom_buff,
    simplify=True,
    poly_crs_code=6312,
    to_crs_code=6312,
)
# set nodes to live where they intersect the original boundary
# nodes outside of this are only used for preventing edge roll-off
for nd_key, nd_data in G_clean.nodes(data=True):
    if extents_geom.contains(geometry.Point(nd_data["x"], nd_data["y"])):
        G_clean.nodes[nd_key]["live"] = True
    else:
        G_clean.nodes[nd_key]["live"] = False
G_clean


# See the following link for information on cleaning options
# https://github.com/benchmark-urbanism/cityseer-examples/blob/main/notebooks/graph_cleaning.ipynb

# create the nodes and edges GeoDataFrames from the networkX graph
# the network structure can be ignored for now because it can be recreated later
edges_gdf_primal = io.geopandas_from_nx(G_clean, crs=6312)

# %%
# save primal to GPKG and do inspection or further cleaning from QGIS
edges_gdf_primal.to_file(f"../temp/{location_key}_network_clean_edges_primal.gpkg")

# %%
# dual representations can be preferable for visualisation
# in this case: cast the graph to dual, then attach the original primal edges for visualisation
G_clean_nx_dual = graphs.nx_to_dual(G_clean)
(
    nodes_gdf_dual,
    edges_gdf_dual,
    _network_structure_dual,
) = io.network_structure_from_nx(G_clean_nx_dual, crs=6312)

# %% save dual to GPKG
nodes_gdf_dual.to_file(f"../temp/{location_key}_network_clean_nodes_dual.gpkg")
edges_gdf_dual.to_file(f"../temp/{location_key}_network_clean_edges_dual.gpkg")
