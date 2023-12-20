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
    poly_epsg_code=3007,
    to_epsg_code=3007,
    simplify=True,
    # edit the below three parameters if wanted - increasing will be more aggressive
    # too much will start collapsing block topologies
    crawl_consolidate_dist=12,  # default is 12
    parallel_consolidate_dist=20,  # default is 15
    iron_edges=True,  # default is True - will try to straigthen edges where necessary but set to False if preferred
    # custom request
    custom_request="""
        /* https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL */
        /* https://overpass-turbo.eu */
        [out:json];
        (
        way["highway"]
        ["area"!="yes"]
        ["highway"!~"motorway|motorway_link|trunk|trunk_link|bus_guideway|busway|escape|raceway|proposed|planned|abandoned|platform|construction|emergency_bay|rest_area"]
        ["track"!~"grade3|grade4|grade5"]
        ["footway"!="sidewalk"]
        ["service"!~"parking_aisle|driveway|drive-through|slipway"]
        ["amenity"!~"charging_station|parking|fuel|motorcycle_parking|parking_entrance|parking_space"]
        ["indoor"!="yes"]
        ["level"!="-2"]
        ["level"!="-3"]
        ["level"!="-4"]
        ["level"!="-5"]
        (poly:"{geom_osm}");
        );
        out body;
        >;
        out qt;
        """,
)
# save to QGIS
edges_gdf_primal = io.geopandas_from_nx(G_clean, crs=3007)
edges_gdf_primal.to_file(f"../temp/gothenburg_osm_network_cleaned_v3.gpkg")

# %%
# reopen in case edited in QGIS
edges_gdf_qgis = gpd.read_file(f"../temp/gothenburg_osm_network_cleaned_v3.gpkg")
G_primal = io.nx_from_generic_geopandas(edges_gdf_qgis)
# cast to dual
G_dual = graphs.nx_to_dual(G_primal)
# mark nodes inside original unbuffered extents as "live"
for nd_key, nd_data in G_dual.nodes(data=True):
    if extents_geom.contains(geometry.Point(nd_data["x"], nd_data["y"])):
        G_dual.nodes[nd_key]["live"] = True
    else:
        G_dual.nodes[nd_key]["live"] = False
# prepare data structures
nodes_gdf, edges_gdf, network_structure = io.network_structure_from_nx(G_dual, crs=3007)

# %%
# compute centralities
metrics.networks.node_centrality_shortest(
    network_structure, nodes_gdf, distances=[500, 1000, 2000, 5000, 10000]
)
metrics.networks.node_centrality_simplest(
    network_structure, nodes_gdf, distances=[500, 1000, 2000, 5000, 10000]
)


# %%
# a function is defined which copies geoms from the originating networkx graph
# the geometries are being copied directly instead of via WKT since no intermediary saving to disk
def copy_primal_edges(row):
    return G_primal[row["primal_edge_node_a"]][row["primal_edge_node_b"]][
        row["primal_edge_idx"]
    ]["geom"]


# apply the function against the GeoPandas DataFrame
nodes_gdf["line_geometry"] = nodes_gdf.apply(copy_primal_edges, axis=1)
# Set this new column as the main geometry column
nodes_gdf.set_geometry("line_geometry", inplace=True)
# set the CRS
nodes_gdf["line_geometry"].set_crs("EPSG:3007", inplace=True)
# GPKG can only handle a single official geom column
# copy old POINT geom column to point_geom as WKT format
nodes_gdf["point_geom"] = nodes_gdf["geom"].to_wkt()
# drop old POINT geom column
nodes_gdf = nodes_gdf.drop(columns=["geom"])
nodes_gdf = nodes_gdf.set_crs(3007)

# %%
# save to GPKG
nodes_gdf.to_file(f"../temp/gothenburg_osm_dual_metrics.gpkg")
