# %%
import osmnx as ox

# %%
# CASE 1 - download for Cyprus
# Download the boundaries for Cyprus
# This will return a GeoPandas DataFrame
cyprus_extents_gdf = ox.geocode_to_gdf(
    ["Cyprus", "British Sovereign Base Areas", "Northern Cyprus"]
)
# dissolve the boundaries into a single boundary
cyprus_dissolved_gdf = cyprus_extents_gdf.dissolve()
# preferably simplify - units are degrees from WGS84 - optionally take the convex hull
cyprus_dissolved_gdf.geometry = cyprus_dissolved_gdf.geometry.simplify(0.0001)
# then save to a file
# indexing into "geometry" will remove all columns except the geometry
cyprus_dissolved_gdf[["geometry"]].to_file(f"../temp/cyprus_boundary.gpkg")

# %%
# CASE 2 - download for Nicosia
# in this case the query directly requests the polygon from the OSM id relation
nicosia_extents_gdf = ox.geocode_to_gdf("R2628520", by_osmid=True, which_result=2)
# preferably simplify - units are degrees from WGS84 - optionally take the convex hull
nicosia_extents_gdf.geometry = nicosia_extents_gdf.geometry.simplify(0.0001)
# then save to a file
# indexing into "geometry" will remove all columns except the geometry
nicosia_extents_gdf.to_file(f"../temp/nicosia_boundary.gpkg")
