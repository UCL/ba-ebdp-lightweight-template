# %%
import osmnx as ox

# Specify the location and download boundaries
cyprus_boundary = ox.geocode_to_gdf(
    ["Cyprus", "British Sovereign Base Areas", "Northern Cyprus"]
)
# the boundaries are now contained in a GeoPandas dataframe
# dissolve the boundaries into a single boundary
cyprus_boundary_merged = cyprus_boundary.dissolve()
# then save to a file
cyprus_boundary_merged.to_file("../temp/cyprus_boundary_merged.gpkg")
