# %%
import osmnx as ox

# Download the boundaries for the necessary location
# This will return a GeoPandas DataFrame
extents_gpd = ox.geocode_to_gdf(
    ["Cyprus", "British Sovereign Base Areas", "Northern Cyprus"]
)
# dissolve the boundaries into a single boundary
extents_gpd_merged = extents_gpd.dissolve()
# preferably simplify - units are degrees from WGS84 - optionally take the convex hull
extents_gpd_merged.geometry = extents_gpd_merged.geometry.convex_hull.simplify(0.1)
# then save to a file
# indexing into "geometry" will remove all columns except the geometry
extents_gpd_merged[["geometry"]].to_file("../temp/cyprus_boundary_merged.gpkg")
