import argparse
import os
import sys
import time
import zarr
from tqdm import tqdm
import netCDF4 as nc
import numpy as np
import dask as da
from dask.diagnostics import ProgressBar
import zarr
import gc
import os

if __name__ == "__main__":
    
    ### Script parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file')
    parser.add_argument('-n', '--workers')
    
    args = parser.parse_args()
    file_path = args.file
    
    ### Pre-allocate space & define chunking
    print('\nInitializing...')
    
    if os.path.isdir(file_path):
        store = zarr.open(file_path, mode = 'a')
    else:
        raise FileNotFoundError(f"{file_path} do not exist")
    
    n_point = store['lat'].shape[0]
    n_time = store['lat'].shape[1]
    ns = int(n_point / 366)
    
    chunks = [ns*i for i in range(366)]
    chunks = np.asarray(chunks)
    assert chunks[-1] == n_point - ns  
    
    print(f"n_points = {n_point} | n_time = {n_time}")
    
    print('\nCreating new store...')
    try: 
        test = store['K']
        print('Using existing I J K directory...')
    except:
        print('Creating new I J K directory...')
        store['I'] = zarr.zeros(shape=(n_point, n_time), chunks=(ns, n_time))
        store['J'] = zarr.zeros(shape=(n_point, n_time), chunks=(ns, n_time))
        store['K'] = zarr.zeros(shape=(n_point, n_time), chunks=(ns, n_time))
    
    print('\nLoading Coordinates...')
    ## Load coordinates
    cube = nc.Dataset("/data/SO2/SO24/ANDY/SOHI/Data/Models/SOHI/Annum/Amundsen.nc")
    XC = cube['lon'][:]
    YC = cube['lat'][:]
    RC = cube['depth'][:]
    cube.close()
    
    ## Calculate I, J, K index within the particle index i1 and i2
    def findIJK(i1, ns = ns, n_time = n_time, YC = YC, XC = XC, RC = RC, file_path = file_path):
        
        i2 = i1 + ns
        resX = np.zeros((ns, n_time))
        resY = np.zeros((ns, n_time))
        resZ = np.zeros((ns, n_time))
        
        data = zarr.open_group(file_path,'r')
        
        count = 0
        for p in range(i1,i2):
            lats = data['lat'][p,:]
            lons = data['lon'][p,:]
            deps = data['z'][p,:]
                       
            Y = np.tile(lats, (len(YC),1))
            Y = np.abs(Y - YC[:,None])
            Y = np.argmin(Y, axis=0)

            X = np.tile(lons, (len(XC),1))
            X = np.abs(X - XC[:,None])
            X = np.argmin(X, axis=0)

            Z = np.tile(deps, (len(RC),1))
            Z = np.abs(Z - RC[:,None])
            Z = np.argmin(Z, axis=0)     
            
            resX[count,:] = X[:]
            resY[count,:] = Y[:]
            resZ[count,:] = Z[:]
            
            count += 1
            
        data = zarr.open_group(file_path,'a')
        data['I'][i1:i2, :] = resY[:]
        data['J'][i1:i2, :] = resX[:]
        data['K'][i1:i2, :] = resZ[:]

    print('\nCreating delayed objects...')
    delayedObj = []
    for t in range(len(chunks)):
        ## Check if there is data written
        test = store['I'][chunks[t]:chunks[t]+ns,2]
        test = test == 0
        if test.any(): ## No data...
            print(f"CHUNK = {t} appended")
            delayedObj.append(da.delayed(findIJK)(chunks[t]))
        else:
            print(f"Skipping CHUNK = {t}")

    print('\nComputing...')
    with ProgressBar():
        da.compute(*delayedObj, num_workers=int(args.workers), memory_limit='2GB')
        
    print('Done!')