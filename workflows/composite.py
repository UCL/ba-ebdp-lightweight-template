"""

"""

import pathlib

import geopandas as gpd
from cityseer.metrics import networks
from cityseer.tools import graphs, io
from shapely import geometry


def process_bounds(
    bounds_path: pathlib.Path | str, out_path: pathlib.Path | str, distances: list[int]
):
    """ """
    bounds_path = pathlib.Path(bounds_path)
    extents_gpd = gpd.read_file(bounds_path)
    if not extents_gpd.crs.is_projected:
        raise IOError("Input spatial boundary must be in a projected CRS.")
    working_crs = extents_gpd.crs.to_epsg()
    working_path = bounds_path.with_suffix("")
    if not isinstance(working_crs, int):
        raise ValueError(f"Expected int for EPSG code: {working_crs}")
    if not extents_gpd.geom_type[0] in ("Polygon", "MultiPolygon"):
        raise ValueError("Input data should be Polygon or MultiPolygon type.")
    bound_geom = extents_gpd.geometry.unary_union
    extents_geom = bound_geom.convex_hull.simplify(100)
    # TODO: max(distances)
    extents_geom_buff = extents_geom.buffer(max(distances))
    G_clean_nx = io.osm_graph_from_poly(
        extents_geom_buff,
        simplify=True,
        poly_crs_code=working_crs,
        to_crs_code=working_crs,
    )
    for nd_key, nd_data in G_clean_nx.nodes(data=True):
        if extents_geom.contains(geometry.Point(nd_data["x"], nd_data["y"])):
            G_clean_nx.nodes[nd_key]["live"] = True
        else:
            G_clean_nx.nodes[nd_key]["live"] = False
    G_clean_nx_dual = graphs.nx_to_dual(G_clean_nx)
    (
        nodes_gdf_dual,
        _edges_gdf_dual,
        network_structure_dual,
    ) = io.network_structure_from_nx(G_clean_nx_dual, crs=working_crs)

    # centrality
    nodes_gdf_dual = networks.node_centrality_shortest(
        network_structure_dual,
        nodes_gdf_dual,
        distances=distances,
    )
    nodes_gdf_dual = networks.node_centrality_simplest(
        network_structure_dual,
        nodes_gdf_dual,
        distances=distances,
    )
    nodes_gdf_dual.to_file(out_path)


if __name__ == "__main__":
    bounds_path = "./temp/AbuDhabi_boundary.gpkg"
    out_path = "./temp/AbuDhabi_auto_clean_centrality.gpkg"
    distances = [400, 800, 1200, 2000, 5000, 10000]
    process_bounds(bounds_path, out_path, distances)
