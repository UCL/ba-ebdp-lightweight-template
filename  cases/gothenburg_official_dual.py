"""
runs centralities on official network
"""

# %%
import geopandas as gpd
from cityseer import metrics
from cityseer.tools import graphs, io
from shapely import geometry, ops

# reopen in case edited in QGIS
edges_gdf = gpd.read_file(f"../temp/GOT_NMS_Revised_231115/GOT_NMS_Network_231115.shp")
# Union all geometries in the GeoDataFrame
extents_geom_buff = ops.unary_union(edges_gdf["geometry"]).convex_hull
# a reverse buffer 10km for edge effects
extents_geom = extents_geom_buff.buffer(-10000)
# convert edges GDF to networkx
G_official = io.nx_from_generic_geopandas(edges_gdf)
# makes sure nodes are properly connected
G_official = graphs.nx_consolidate_nodes(G_official, 2)
# cast to dual
G_dual = graphs.nx_to_dual(G_official)
# mark nodes inside original unbuffered extents as "live"
for nd_key, nd_data in G_dual.nodes(data=True):
    if extents_geom.contains(geometry.Point(nd_data["x"], nd_data["y"])):
        G_dual.nodes[nd_key]["live"] = True
    else:
        G_dual.nodes[nd_key]["live"] = False
# prepare data structures
nodes_gdf, edges_gdf, network_structure = io.network_structure_from_nx(G_dual, crs=3007)
# compute centralities
metrics.networks.node_centrality_shortest(
    network_structure, nodes_gdf, distances=[500, 1000, 2000, 5000, 10000]
)
metrics.networks.node_centrality_simplest(
    network_structure, nodes_gdf, distances=[500, 1000, 2000, 5000, 10000]
)

# %%
nodes_gdf.to_file(f"../temp/gothenburg_official_dual_nodes.gpkg")
edges_gdf.to_file(f"../temp/gothenburg_official_dual_edges.gpkg")
