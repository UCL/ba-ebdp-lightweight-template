# %%
import geopandas as gpd
from cityseer.metrics import networks
from cityseer.tools import graphs, io
from shapely.wkt import loads

# %%
# read the dataframes and set the indices
# when GPD are converted to GPKG the indices are converted to a column called "index"
nodes_gdf_dual_in = gpd.read_file("../temp/cyprus_network_nodes_dual.gpkg")
nodes_gdf_dual_in = nodes_gdf_dual_in.set_index("index")
edges_gdf_dual_in = gpd.read_file("../temp/cyprus_network_edges_dual.gpkg")
edges_gdf_dual_in = edges_gdf_dual_in.set_index("index")

# %%
# since the GPD were saved and reloaded network structure needs to be recreated
dual_nx = io.nx_from_cityseer_geopandas(nodes_gdf_dual_in, edges_gdf_dual_in)
# apply edge weightings - this weights-down nodes based on duplicitous / parallel segments
# this is used instead of algorithmic cleaning
dual_nx_wt = graphs.nx_weight_by_dissolved_edges(dual_nx)
# generate the network structure
nodes_gdf_dual, edges_gdf_dual, network_structure_dual = io.network_structure_from_nx(
    dual_nx_wt, crs=3035
)
# manually copy across primal edge geoms
nodes_gdf_dual = nodes_gdf_dual.merge(
    nodes_gdf_dual_in[["primal_edge_geom"]],
    left_index=True,
    right_index=True,
    how="left",
)

# %%
# run shortest path centrality
nodes_gdf_dual = networks.node_centrality_shortest(
    network_structure_dual,
    nodes_gdf_dual,
    distances=[500, 1000, 2000, 5000, 10000],
    jitter_scale=20,
)
# run simplest path centrality
nodes_gdf_dual = networks.node_centrality_simplest(
    network_structure_dual,
    nodes_gdf_dual,
    distances=[500, 1000, 2000, 5000, 10000],
    jitter_scale=5,
)

# %%
# set primal line geoms as main geom before saving
# these were stored as WKT geometry via nodes_gdf_dual_in
# Set this new column as the main geometry column
nodes_gdf_dual["line_geometry"] = nodes_gdf_dual["primal_edge_geom"].apply(loads)
nodes_gdf_dual = nodes_gdf_dual.set_geometry("line_geometry")
nodes_gdf_dual["point_geom"] = nodes_gdf_dual["geom"].to_wkt()
nodes_gdf_dual = nodes_gdf_dual.drop(columns=["geom"])

# %% save
nodes_gdf_dual.to_file("../temp/cyprus_network_centrality.gpkg")
