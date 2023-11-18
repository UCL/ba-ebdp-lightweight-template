# %%
import geopandas as gpd
from cityseer.metrics import networks
from cityseer.tools import graphs, io
from shapely.wkt import loads

# location key for naming files
location_key = "nicosia"

# %%
# read the dataframes and set the indices
# when GPD are converted to GPKG the indices are converted to a column called "index"
nodes_gdf_dual_in = gpd.read_file(
    f"../temp/{location_key}_network_clean_nodes_dual.gpkg"
)
nodes_gdf_dual_in = nodes_gdf_dual_in.set_index("index")
edges_gdf_dual_in = gpd.read_file(
    f"../temp/{location_key}_network_clean_edges_dual.gpkg"
)
edges_gdf_dual_in = edges_gdf_dual_in.set_index("index")

# %%
# since the GPD were saved and reloaded network structure needs to be recreated
dual_nx = io.nx_from_cityseer_geopandas(nodes_gdf_dual_in, edges_gdf_dual_in)
# generate the network structure
nodes_gdf_dual, edges_gdf_dual, network_structure_dual = io.network_structure_from_nx(
    dual_nx, crs=3035
)
# %%
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
nodes_gdf_dual.to_file(f"../temp/{location_key}_network_centrality_clean.gpkg")
