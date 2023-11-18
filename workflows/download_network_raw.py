# %%
import geopandas as gpd
from cityseer.tools import graphs, io
from pyproj import Transformer
from shapely import geometry

# location key for naming files
location_key = "nicosia"

# read the extents file
extents_gpd = gpd.read_file(f"../temp/{location_key}_boundary.gpkg")
extents_gpd

# %%
# the input GPD has a single row representing the boundary
# fetch the row's geometry as a shapely geom
extents_geom_wgs = extents_gpd.iloc[0].geometry

# if the polygon is in a geographic coordinate system, e.g. WGS84 / EPSG:4326
# then convert it to a locally suitable projected CRS before buffering
# Define the coordinate transformation:
# - in this case the input geom is from OSM via EPSG:4326
# - in this case the output geom can uses EPSG:3035 which is appropriate for the EU
transformer = Transformer.from_crs("EPSG:4326", "EPSG:3035", always_xy=True)
# Apply the transformation to each point in the Polygon
extents_geom = geometry.Polygon(
    [transformer.transform(x, y) for x, y in extents_geom_wgs.exterior.coords]
)

# simplify the geometry, otherwise the OSM API migth complain of overly long URIs
extents_geom = extents_geom.convex_hull.simplify(100)

# buffer by the largest distance to be used for the largest centralities or accessibility analysis
# This is not technically necessary for the Cyprus example because it is an island.
extents_geom_buff = extents_geom.buffer(10000)

# %%
# this will download the OSM network with minimal simplification
# specify the input and output EPSG CRS appropriate to the case
# this is returned as a networkX graph
G_raw_nx = io.osm_graph_from_poly(
    extents_geom_buff, simplify=False, poly_epsg_code=3035, to_epsg_code=3035
)
# set nodes to live where they intersect the original boundary
# nodes outside of this are only used for preventing edge roll-off
for nd_key, nd_data in G_raw_nx.nodes(data=True):
    if extents_geom.contains(geometry.Point(nd_data["x"], nd_data["y"])):
        G_raw_nx.nodes[nd_key]["live"] = True
    else:
        G_raw_nx.nodes[nd_key]["live"] = False
G_raw_nx

# %%
# create the nodes and edges GeoDataFrames from the networkX graph
# the network structure can be ignored for now because it can be recreated later
(
    nodes_gdf_primal,
    edges_gdf_primal,
    _network_structure_primal,
) = io.network_structure_from_nx(G_raw_nx, crs=3035)

# %% save primal to GPKG
nodes_gdf_primal.to_file(f"../temp/{location_key}_network_raw_nodes_primal.gpkg")
edges_gdf_primal.to_file(f"../temp/{location_key}_network_raw_edges_primal.gpkg")

# %%
# dual representations can be preferable for visualisation
# in this case: cast the graph to dual, then attach the original primal edges for visualisation
G_raw_nx_dual = graphs.nx_to_dual(G_raw_nx)
(
    nodes_gdf_dual,
    edges_gdf_dual,
    _network_structure_dual,
) = io.network_structure_from_nx(G_raw_nx_dual, crs=3035)


# attach the primal edges to their corresponding dual nodes
# this is useful for downstream visualisation
# i.e. it is often more convenient to visualise the dual node data as the corresponding source (primal) edge
# GeoPandas can't be saved with multiple geom columns, so use WKT for now
# a function is defined which copies geoms from the originating networkx graph
def copy_primal_edges(row):
    return G_raw_nx[row["primal_edge_node_a"]][row["primal_edge_node_b"]][
        row["primal_edge_idx"]
    ]["geom"].wkt


# apply the function against the GeoPandas DataFrame
nodes_gdf_dual["primal_edge_geom"] = nodes_gdf_dual.apply(copy_primal_edges, axis=1)

# %% save dual to GPKG
nodes_gdf_dual.to_file(f"../temp/{location_key}_network_raw_nodes_dual.gpkg")
edges_gdf_dual.to_file(f"../temp/{location_key}_network_raw_edges_dual.gpkg")
