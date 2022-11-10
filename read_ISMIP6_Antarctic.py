"""
@author: jennifer.arthur@npolar.no

Script for reading in netCDF ISMIP6 Antarctic Projections model outputs and writing out variables (e.g. grounded ice area fraction) at specific timesteps as a GIS shapefile.
ISMPI6 Antarctic projections experiment variable names: 
    grounded_ice_sheet_area_fraction			sftgrf
    floating_ice_shelf_area_fraction			sftflf
    land_ice_area_fraction					    sftgif
"""

import xarray as xr
import netCDF4 as nc
from shapely.geometry import shape
import rasterio.features 
import numpy as np
import pandas as pd
import geopandas as gpd

#Open netcdf dataset
ds = xr.open_dataset('Enter netCDF filepath')
#print(ds.variables.keys()) #get all variable names
#ds.data_vars #print all data variables

#Defining parameters and dimensions
sftgrf = ds.variables['sftgrf'][:] #access netcdf variable data, array of 1 element (sftgrf = grounded ice area fraction)
lat = ds.variables['y'][:]
#lat = ds.variables['lat_bnds'][:]
lon = ds.variables['x'][:]
#lon = ds.variables['lon_bnds'][:]
time = ds.variables['time'][:] 

#lon, lat = np.meshgrid(lon, lat) #create lat and lon coordinate arrays

#-------------------------------------------------------------------------------
##Writing netCDF variables to shapefile

#Create empty lists
mypoly=[]
vals=[]

# Set up coordinates for affine transformation. 
#x_min = ds.sftgrf[-1,0,0].x.values #translate in x direction
#y_min = ds.sftgrf[-1,0,0].y.values #translate in y direction
#x_step = abs(ds.sftgrf[-1,0,0].x.values - ds.sftgrf[-1,0,1].x.values) 
#y_step = abs(ds.sftgrf[-1,0,0].y.values - ds.sftgrf[-1,1,0].y.values)
#x_min = ds.sftgrf[-1,0,0].lon.values #translate in x direction
#y_min = ds.sftgrf[-1,0,0].lat.values #translate in y direction
#x_step = abs(ds.sftgrf[-1,0,0].lon.values - ds.sftgrf[-1,0,1].lon.values) 
#y_step = abs(ds.sftgrf[-1,0,0].lat.values - ds.sftgrf[-1,1,0].lat.values)
#print(x_min,y_min, x_step,y_step)



# Extract sftgrf (grounded ice area fraction) variable for specificed time step and write to shapefile
# Step 1: convert first instance of sftgrf to numpy array (change appropriately: [0,:,:] = first time value, [-1,:,:] = final time value)
# Step 2: Output a set of polygons based on numpy array values using rasterio. Returns a pair of (polygon, value) for each feature 
# Step 3: Append polygons and sftgrf values to mypoly and vals lists.
# Step 4: Affine coordinate transformation so that shapefile has correct crs assigned
for vec,value in rasterio.features.shapes(ds.sftgrf[-1,:,:].to_numpy().astype("float32"), transform=rasterio.Affine(8000.0, 0.0, -3040000.0, 0.0, 8000.0, -3040000.0)):
    mypoly.append(shape(vec))
    vals.append(value)
    
data = {'vals':vals,'geometry':mypoly}
ds_dataframe = pd.DataFrame(data) # convert dataframe into a 2d numpy array
ds_geodataframe = gpd.GeoDataFrame(ds_dataframe,crs="EPSG:3031") #create geodataframe
ds_geodataframe.to_file('Output file location') #write to shapefile


