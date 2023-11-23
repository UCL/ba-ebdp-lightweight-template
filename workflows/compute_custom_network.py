# %%
import geopandas as gpd
from cityseer.tools import graphs, io
from pyproj import Transformer
from shapely import geometry
from cityseer.metrics import networks
from shapely.wkt import loads

# %%
# reopen after editing in QGIS
edges_gdf_custom = gpd.read_file(f"../temp/nicosia_2019_1.gpkg")
# %%
# convert to nx
G_clean_nx = io.nx_from_generic_geopandas(edges_gdf_custom)
(
    nodes_gdf_primal,
    edges_gdf_primal,
    _network_structure_primal,
) = io.network_structure_from_nx(G_clean_nx, crs=32636)
# %%
G_clean_nx_dual = graphs.nx_to_dual(G_clean_nx)


# %%
# generate the network structure
nodes_gdf_dual, edges_gdf_dual, network_structure_dual = io.network_structure_from_nx(
    G_clean_nx_dual, crs=32636
)

# %%
# run shortest path centrality
nodes_gdf_dual = networks.node_centrality_shortest(
    network_structure_dual,
    nodes_gdf_dual,
    distances=[500, 1000, 2000, 5000, 10000],
)
# run simplest path centrality
# use with caution on algorithmically cleaned networks
# unless the network has been visually inspected and corrected in QGIS
nodes_gdf_dual = networks.node_centrality_simplest(
    network_structure_dual,
    nodes_gdf_dual,
    distances=[500, 1000, 2000, 5000, 10000],
)

# save
nodes_gdf_dual.to_file(f"../temp/network_centrality_nicosia_custom.gpkg")
