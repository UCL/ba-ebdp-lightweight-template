""" Runs centrality on a pre-cleaned network."""

# %%
import os

import geopandas as gpd
from cityseer.metrics import networks
from cityseer.tools import graphs, io

os.getcwd()

# %%
# open custom file
edges_gdf_custom = gpd.read_file(f"../temp/pedieos_1.gpkg")

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
# run shortest path centrality
nodes_gdf_dual = networks.node_centrality_shortest(
    network_structure_dual,
    nodes_gdf_dual,
    distances=[500, 1000, 1500],
)

# run simplest path centrality
nodes_gdf_dual = networks.node_centrality_simplest(
    network_structure_dual,
    nodes_gdf_dual,
    distances=[500, 1000, 1500],
)

# save
nodes_gdf_dual.to_file(f"../temp/network_centrality_pedieos.gpkg")
