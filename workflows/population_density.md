# Population density workflow : Interpolation and Aggregative

## INTERPOLATION

- Download the 1km2 EU population grid from [eurostat](https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/population-distribution-demography/geostat#geostat11).
- Open in QGIS
- Open the area of interest boundary
- Export the boundary to a new file in 3035 projection (same as population grid)
- Buffer using Vector - Geoprocessing - Buffer tool and use a ~1000m buffer (or as preferred). This will generate a temporary scratch layer. Save to a geojson file and check that the CRS is 3035.
- Go to Raster - Extraction - Clip Raster by Mask Layer and clip the population raster by the newly created geojson buffer layer.
- Go to Raster – projections - Warp and select the clipped raster as input layer. Set the input and output CRS to 3035, resample with bilinear and set the output file resolution (in georeferenced units) to 100m. This will generate an upsampled raster. Save if wanted.
- Open a point data set (e.g. network nodes)
- Open the Processing Toolbox panel then search for the Sample Raster Values tool. Use the points dataset for the input layer and the upsampled raster layer for the raster. Save to a new file.
- Visualise or use for future analysis (look for a new column name in the dataset).

## AGGREGATIVE

This alternative method  is using Copernicus EU blocks

*Note that this is an aggregative (summing) of population from blocks adjacent to street nodes.* 

- Open the blocks layer in QGIS
- Open the points layer (e.g. network nodes)
- Check that these are the same CRS
- Buffer the nodes layer using Vector - Geoprocessing Tools - Buffer then buffer with a distance around 20m.
- Open the new layers properties and go to source, then click the button to create a spatial index.
- Join the new buffered nodes layer to the blocks layer using Vector - Data Management  
- Join Attributes by location. Use the buffered layers for “Join to features in” and select the blocks layer for “By comparing to”. Select the population column for “Fields to add” and use the “intersect” join predicate. Check that the join type is one-to-many. Select an output file name such as “Joined”.
- Go to Layer - Create Layer - New Virtual Layer and use a query such as: SELECT t.fid, t.geometry, sum(t.Pop2018) as pop_agg FROM Joined as t GROUP BY t.fid
- The new virtual layer’s pop_agg column should now contain the summed population from the surrounding blocks within 20m as a field called “pop_agg”. Visually check that the totals are as anticipated.
- Transform back the buffered nodes to nodes with Vector - geometry tools - centroids.
- Save and visualise as wanted.

