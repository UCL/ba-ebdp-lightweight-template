"""
"""

# %%
import geopandas as gpd
from cityseer.tools import graphs, io
from pyproj import Transformer
from shapely import geometry

# location key for naming files
location_key = "cyprus"

# read the extents file
extents_gpd = gpd.read_file(f"../temp/{location_key}_boundary.gpkg")
extents_gpd

# %%
# STEP 1 - fetch and clean the network

# the input GPD has a single row representing the boundary
# fetch the row's geometry as a shapely geom
extents_geom_wgs = extents_gpd.iloc[0].geometry

# if the polygon is in a geographic coordinate system, e.g. WGS84 / EPSG:4326
# then convert it to a locally suitable projected CRS before buffering
# Define the coordinate transformation:
# - in this case the input geom is from OSM via EPSG:4326
# - in this case the output geom can uses EPSG:6312 which is appropriate for Cyprus
transformer = Transformer.from_crs("EPSG:4326", "EPSG:6312", always_xy=True)
# Apply the transformation to each point in the Polygon
extents_geom = geometry.Polygon(
    [transformer.transform(x, y) for x, y in extents_geom_wgs.exterior.coords]
)

# simplify the geometry, otherwise the OSM API might complain of overly long URIs
extents_geom = extents_geom.convex_hull.simplify(100)

# buffer by the largest distance to be used for the largest centralities or accessibility analysis
# This is not technically necessary for the Cyprus example because it is an island.
extents_geom_buff = extents_geom.buffer(10000)

# %%
# this will download the OSM network
# specify the input and output EPSG CRS appropriate to the case
# this is returned as a networkX graph
# set simplify to False so that the steps can be done manually per below
G = io.osm_graph_from_poly(
    extents_geom_buff,
    simplify=False,
    poly_crs_code=6312,
    to_crs_code=6312,
)
edges_gdf_raw = io.geopandas_from_nx(G, crs=6312)
edges_gdf_raw.to_file(f"../temp/{location_key}_network_raw.gpkg")

# %%
graph_crs = graphs.nx_remove_dangling_nodes(G)
for hwy_keys, matched_only, split_dist, consol_dist, cent_by_itx in [
    (["motorway"], True, 80, 40, False),
    (["trunk"], True, 60, 30, False),
    (["primary"], True, 40, 20, False),
    (["secondary"], True, 30, 15, False),
    (["tertiary"], True, 30, 15, False),
    (["residential"], True, 20, 12, True),
    (["motorway"], False, 60, 30, False),
    (["trunk", "primary"], False, 30, 20, False),
    (["secondary", "tertiary"], False, 15, 12, False),
    (["residential", "service"], False, 12, 10, True),
]:
    contains_buffer_dist = max(split_dist, 25)
    graph_crs = graphs.nx_split_opposing_geoms(
        graph_crs,
        buffer_dist=split_dist,
        prioritise_by_hwy_tag=True,
        osm_hwy_target_tags=hwy_keys,
        osm_matched_tags_only=matched_only,
        contains_buffer_dist=contains_buffer_dist,
    )
    graph_crs = graphs.nx_consolidate_nodes(
        graph_crs,
        buffer_dist=consol_dist,
        crawl=True,
        centroid_by_itx=cent_by_itx,
        prioritise_by_hwy_tag=True,
        contains_buffer_dist=contains_buffer_dist,
        osm_hwy_target_tags=hwy_keys,
        osm_matched_tags_only=matched_only,
    )
    graph_crs = graphs.nx_remove_filler_nodes(graph_crs)
graph_crs = graphs.nx_iron_edges(graph_crs)

# save primal to GPKG and do inspection or further cleaning from QGIS
edges_gdf_primal = io.geopandas_from_nx(graph_crs, crs=6312)
edges_gdf_primal.to_file(f"../temp/{location_key}_network_auto_clean.gpkg")
