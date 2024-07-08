""" Runs centrality on a pre-cleaned network."""

# %%
import geopandas as gpd
from cityseer.metrics import networks
from cityseer.tools import graphs, io

# %%
# open custom file
edges_gdf_input = gpd.read_file(f"../temp/AbuDhabi.gpkg")
edges_gdf_custom = edges_gdf_input.explode(ignore_index=True)
edges_gdf_custom.reset_index(drop=True, inplace=True)
edges_gdf_custom

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
distances = [400, 800, 1200, 2000, 5000, 10000]
# run shortest path centrality
nodes_gdf_dual = networks.node_centrality_shortest(
    network_structure_dual,
    nodes_gdf_dual,
    distances=distances,
)

# run simplest path centrality
nodes_gdf_dual = networks.node_centrality_simplest(
    network_structure_dual,
    nodes_gdf_dual,
    distances=distances,
)

# save
nodes_gdf_dual.to_file(f"../temp/AbuDhabi_w_cent.gpkg")
