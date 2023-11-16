# %%
import osmnx as ox

# Download the boundaries for the necessary location
# This will return a GeoPandas DataFrame
cyprus_boundary = ox.geocode_to_gdf(
    ["Cyprus", "British Sovereign Base Areas", "Northern Cyprus"]
)
# dissolve the boundaries into a single boundary
cyprus_boundary_merged = cyprus_boundary.dissolve()
# then save to a file
cyprus_boundary_merged.to_file("../temp/cyprus_boundary_merged.gpkg")
