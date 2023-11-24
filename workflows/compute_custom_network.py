""" Runs centrality on a pre-cleaned network."""
# %%
import geopandas as gpd
from cityseer.metrics import networks
from cityseer.tools import graphs, io

# %%
# open custom file
edges_gdf_custom = gpd.read_file(f"../temp/nicosia_2019_1.gpkg")

# %%
# generate the primal nx
G_clean_nx = io.nx_from_generic_geopandas(edges_gdf_custom)
# generate the dual
G_clean_nx_dual = graphs.nx_to_dual(G_clean_nx)
# generate the dual network structure
nodes_gdf_dual, edges_gdf_dual, network_structure_dual = io.network_structure_from_nx(
    G_clean_nx_dual, crs=32636
)

# %%
# attach the primal edges to their corresponding dual nodes
# this is useful for downstream visualisation


# a function is defined which copies geoms from the originating networkx graph
# the geometries are being copied directly instead of via WKT since no intermediary saving to disk
def copy_primal_edges(row):
    return G_clean_nx[row["primal_edge_node_a"]][row["primal_edge_node_b"]][
        row["primal_edge_idx"]
    ]["geom"]


# apply the function against the GeoPandas DataFrame
nodes_gdf_dual["line_geometry"] = nodes_gdf_dual.apply(copy_primal_edges, axis=1)
# Set this new column as the main geometry column
nodes_gdf_dual.set_geometry("line_geometry", inplace=True)
# set the CRS
nodes_gdf_dual["line_geometry"].set_crs("EPSG:32636", inplace=True)
# GPKG can only handle a single official geom column
# copy old POINT geom column to point_geom as WKT format
nodes_gdf_dual["point_geom"] = nodes_gdf_dual["geom"].to_wkt()
# drop old POINT geom column
nodes_gdf_dual = nodes_gdf_dual.drop(columns=["geom"])

# %%
# run shortest path centrality
nodes_gdf_dual = networks.node_centrality_shortest(
    network_structure_dual,
    nodes_gdf_dual,
    distances=[500, 1000, 2000, 5000, 10000],
)

# run simplest path centrality
nodes_gdf_dual = networks.node_centrality_simplest(
    network_structure_dual,
    nodes_gdf_dual,
    distances=[500, 1000, 2000, 5000, 10000],
)

# save
nodes_gdf_dual.to_file(f"../temp/network_centrality_nicosia_custom.gpkg")
# %%
