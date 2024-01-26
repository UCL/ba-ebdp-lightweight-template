"""
Generates algorithmically cleaned primal network and runs centralities
"""

# %%
import geopandas as gpd
import osmnx as ox
from cityseer import metrics
from cityseer.tools import graphs, io
from pyproj import Transformer
from shapely import geometry, to_wkt

# fetch using relation id
gothenburg_extents_gdf = ox.geocode_to_gdf("R935611", by_osmid=True)
# take convex hull
gothenburg_extents_gdf.geometry = gothenburg_extents_gdf.geometry.convex_hull
# save for QGIS
gothenburg_extents_gdf.to_file(f"../temp/gothenburg_boundary.gpkg")

# %%
# read the extents file (in case edited from QGIS)
extents_gpd = gpd.read_file(f"../temp/gothenburg_boundary.gpkg")
# fetch geom
extents_geom_wgs = extents_gpd.iloc[0].geometry
# transform to 3007
transformer = Transformer.from_crs("EPSG:4326", "EPSG:3007", always_xy=True)
extents_geom = geometry.Polygon(
    [transformer.transform(x, y) for x, y in extents_geom_wgs.exterior.coords]
)
# take convex hull, then buffer by 20km, and simplify by 100m
extents_geom = extents_geom.convex_hull.buffer(20000).simplify(100)
# a separate 10km buffered version for edge effects
extents_geom_buff = extents_geom.buffer(10000)

# %%
# fetch and automatically clean
G_clean = io.osm_graph_from_poly(
    extents_geom_buff,
    poly_crs_code=3007,
    to_crs_code=3007,
    simplify=True,
    # edit the below three parameters if wanted - increasing will be more aggressive
    # too much will start collapsing block topologies
    crawl_consolidate_dist=12,  # default is 12
    parallel_consolidate_dist=15,  # default is 15
    iron_edges=True,  # default is True - will try to straigthen edges where necessary but set to False if preferred
)
# save to QGIS
edges_gdf_primal = io.geopandas_from_nx(G_clean, crs=3007)
edges_gdf_primal.to_file(f"../temp/gothenburg_osm_network_cleaned.gpkg")

# %%
# reopen in case edited in QGIS
edges_gdf_qgis = gpd.read_file(f"../temp/gothenburg_osm_network_cleaned.gpkg")
G_qgis = io.nx_from_generic_geopandas(edges_gdf_qgis)
# mark nodes inside original unbuffered extents as "live"
for nd_key, nd_data in G_clean.nodes(data=True):
    if extents_geom.contains(geometry.Point(nd_data["x"], nd_data["y"])):
        G_clean.nodes[nd_key]["live"] = True
    else:
        G_clean.nodes[nd_key]["live"] = False
# prepare data structures
nodes_gdf, edges_gdf, network_structure = io.network_structure_from_nx(G_qgis, crs=3007)

# %%
# compute centralities
metrics.networks.node_centrality_shortest(
    network_structure, nodes_gdf, distances=[500, 1000, 2000, 5000, 10000]
)
nodes_gdf.to_file(f"../temp/gothenburg_osm_nodes.gpkg")
edges_gdf.to_file(f"../temp/gothenburg_osm_edges.gpkg")

# %%
# generate vis lines for nodes - view in QGIS as "edge_geom"
G_qgis = graphs.nx_generate_vis_lines(G_qgis)


def generate_vis_lines(node_row):
    return G_qgis.nodes[node_row.name]["line_geom"]


def geom_to_wkt(node_row):
    return to_wkt(node_row["geom"])


nodes_gdf["edge_geom"] = nodes_gdf.apply(generate_vis_lines, axis=1)
nodes_gdf["node_geom_wkt"] = nodes_gdf.apply(geom_to_wkt, axis=1)
nodes_gdf = nodes_gdf.drop(columns=["geom"])
nodes_gdf = nodes_gdf.set_geometry("edge_geom")
nodes_gdf = nodes_gdf.set_crs(3007)

# %%
# save to GPKG
nodes_gdf.to_file(f"../temp/gothenburg_osm_nodes_as_edges.gpkg")
