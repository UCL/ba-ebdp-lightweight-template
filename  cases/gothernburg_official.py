"""
runs centralities on official network
"""

# %%
import geopandas as gpd
from cityseer import metrics
from cityseer.tools import graphs, io
from shapely import geometry, ops, to_wkt

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

# %%
# mark nodes inside original unbuffered extents as "live"
for nd_key, nd_data in G_official.nodes(data=True):
    if extents_geom.contains(geometry.Point(nd_data["x"], nd_data["y"])):
        G_official.nodes[nd_key]["live"] = True
    else:
        G_official.nodes[nd_key]["live"] = False
# prepare data structures
nodes_gdf, edges_gdf, network_structure = io.network_structure_from_nx(
    G_official, crs=3007
)
# compute centralities
metrics.networks.node_centrality_shortest(
    network_structure, nodes_gdf, distances=[500, 1000, 2000, 5000, 10000]
)

nodes_gdf.to_file(f"../temp/gothenburg_official_nodes.gpkg")
edges_gdf.to_file(f"../temp/gothenburg_official_edges.gpkg")

# %%
# generate vis lines for nodes - view in QGIS as "edge_geom"
G_qgis = graphs.nx_generate_vis_lines(G_official)


def generate_vis_lines(node_row):
    return G_qgis.nodes[node_row.name]["line_geom"]


def geom_to_wkt(node_row):
    return to_wkt(node_row["geom"])


nodes_gdf["edge_geom"] = nodes_gdf.apply(generate_vis_lines, axis=1)
nodes_gdf["node_geom_wkt"] = nodes_gdf.apply(geom_to_wkt, axis=1)
nodes_gdf = nodes_gdf.drop(columns=["geom"])
nodes_gdf = nodes_gdf.set_geometry("edge_geom")
nodes_gdf = nodes_gdf.set_crs(3007)

nodes_gdf.to_file(f"../temp/gothenburg_official_nodes_as_edges.gpkg")

# %%
# DECOMPOSED OPTION
G_decomposed = graphs.nx_decompose(G_official, 20)
# mark nodes inside original unbuffered extents as "live"
for nd_key, nd_data in G_decomposed.nodes(data=True):
    if extents_geom.contains(geometry.Point(nd_data["x"], nd_data["y"])):
        G_decomposed.nodes[nd_key]["live"] = True
    else:
        G_decomposed.nodes[nd_key]["live"] = False
# prepare data structures
(
    nodes_gdf_decomp,
    edges_gdf_decomp,
    network_structure_decomp,
) = io.network_structure_from_nx(G_decomposed, crs=3007)
# compute centralities
metrics.networks.node_centrality_shortest(
    network_structure_decomp, nodes_gdf_decomp, distances=[500, 1000, 2000, 5000, 10000]
)

nodes_gdf_decomp.to_file(f"../temp/gothenburg_official_nodes_decomposed.gpkg")
