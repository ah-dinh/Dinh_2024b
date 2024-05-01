import matplotlib.pyplot as plt
import numpy as np
from scipy.io import loadmat

import sys
sys.path.insert(0, "/data/SO2/SO24/ANDY/SOHI/Utils")
import Andy
import SOhi_Toolbox


## Amundsen Sea
latbounds = [-75.5, -69]
lonbounds = [-140, -65]
start_date = (2006, 8, 1, 0)
end_date = (2006, 8, 31, 23)


ice, XC, YC = Andy.loads.sohi_meta('icedraft', lon_bounds = lonbounds, lat_bounds = latbounds)
ice[ice!=0] = 1
bath, XC, YC = Andy.loads.sohi_meta('bathymetry', lon_bounds = lonbounds, lat_bounds = latbounds)

SOhi_Toolbox.SOhi2nc.export_to_nc(   file_name         = '2006_08.nc', 
                        start_date        = start_date, 
                        end_date          = end_date,
                        variables         = ['THETA', 'SALT', 'UVEL', 'VVEL', 'WVEL'], 
                        lon_bounds        = lonbounds, 
                        lat_bounds        = latbounds, 
                        lon_coord_type    = 180, 
                        compression_level = 1) 