import netCDF4 as nc
import time
import numpy as np

files = ['2005_09.nc',
        '2005_10.nc',
        '2005_11.nc',
        '2005_12.nc',
        '2006_01.nc',
        '2006_02.nc',
        '2006_03.nc',
        '2006_04.nc',
        '2006_05.nc',
        '2006_06.nc',
        '2006_07.nc',
        '2006_08.nc']

fn = 'Amundsen.nc'

cube = nc.Dataset(files[-1])
YG = cube['YG'][:]
XG = cube['XG'][:]
YC = cube['lat'][:]
XC = cube['lon'][:]
RC = cube['depth'][:]
RF = cube['RF'][:]
cube.close()


dates = []
for f in files:
    cube = nc.Dataset(f)
    t = cube['date'][:]
    for i in t:
        dates.append(i)
dates = np.asarray(dates)

np.save('recovery.npy', np.asarray([0 for i in range(len(dates))]))


### Create cube
cube = nc.Dataset(fn, mode='w', format='NETCDF4', clobber=False)                   
cube.createDimension('lat', len(YC))    
cube.createDimension('lon', len(XC))   
cube.createDimension('depth', len(RC))
cube.createDimension('date', None)
    
vdate = cube.createVariable('date', np.float32, ('date',))
vdate.units="Iteration"     
vdate.long_name="Iteration since 2005-01-01 00:00:00 @ 60s timestep" 
vdate[:] = dates[:]
    
vXC = cube.createVariable('lon', np.float32, ('lon',))
vXC.units="Degrees"     
vXC.long_name="Longitude at cell center" 
vXC[:] = XC[:]
    
vXG = cube.createVariable('XG', np.float32, ('lon',))
vXG.units="Degrees"     
vXG.long_name="Longitude at cell edge" 
vXG[:] = XG[:]
    
vYC = cube.createVariable('lat', np.float32, ('lat',))
vYC.units="Degrees"     
vYC.long_name="Latitude at cell center" 
vYC[:] = YC[:]
    
vYG = cube.createVariable('YG', np.float32, ('lat',))
vYG.units="Degrees"     
vYG.long_name="Latitude at cell center" 
vYG[:] = YG[:]
    
vRC = cube.createVariable('depth', np.float32, ('depth',))
vRC.units="Meters"     
vRC.long_name="Depth at cell center" 
vRC[:] = RC[:]
    
vRF = cube.createVariable('RF', np.float32, ('depth',))
vRF.units="Meters"     
vRF.long_name="Depth at cell edge" 
vRF[:] = RF[:]

THETA = cube.createVariable('THETA', np.float32, ('date','depth','lat','lon'),
                                                  zlib=True, complevel = 1)
SALT = cube.createVariable('SALT', np.float32, ('date','depth','lat','lon'),
                                                  zlib=True, complevel = 1)
UVEL = cube.createVariable('UVEL', np.float32, ('date','depth','lat','lon'),
                                                  zlib=True, complevel = 1)
VVEL = cube.createVariable('VVEL', np.float32, ('date','depth','lat','lon'),
                                                  zlib=True, complevel = 1)
WVEL = cube.createVariable('WVEL', np.float32, ('date','depth','lat','lon'),
                                                  zlib=True, complevel = 1)
cube.close()

## Write cube
count = 0
avgt = []

new_cube = nc.Dataset('Amundsen.nc', 'a')
for f in files:
    print(f"Processing cube = {f}")
    cube = nc.Dataset(f)
    n = cube['THETA'].shape[0]
    
    for i in range(n):   
        recov = np.load('recovery.npy')
        if recov[count] == 1:
            count += 1
            continue
            
        else:
            print(f"{i+1} out of {n}")
            t_tot = time.time()
        
            t1 = time.time()
            d = np.asarray(cube['THETA'][i,:,:,:]) 
            print(f'THETA read in {int(time.time() - t1)} seconds')
            t1 = time.time()
            THETA[count, :, :, :] = d
            print(f'THETA written in {int(time.time() - t1)} seconds')
        
            t1 = time.time()
            d = np.asarray(cube['SALT'][i,:,:,:]) 
            print(f'SALT read in {int(time.time() - t1)} seconds')
            t1 = time.time()
            SALT[count, :, :, :] = d
            print(f'SALT written in {int(time.time() - t1)} seconds')
        
            t1 = time.time()
            d = np.asarray(cube['UVEL'][i,:,:,:]) 
            print(f'UVEL read in {int(time.time() - t1)} seconds')
            t1 = time.time()
            UVEL[count, :, :, :] = d
            print(f'UVEL written in {int(time.time() - t1)} seconds')
        
            t1 = time.time()
            d = np.asarray(cube['VVEL'][i,:,:,:]) 
            print(f'VVEL read in {int(time.time() - t1)} seconds')
            t1 = time.time()
            VVEL[count, :, :, :] = d
            print(f'VVEL written in {int(time.time() - t1)} seconds')
        
            t1 = time.time()
            d = np.asarray(cube['WVEL'][i,:,:,:]) 
            print(f'WVEL read in {int(time.time() - t1)} seconds')
            t1 = time.time()
            WVEL[count, :, :, :] = d
            print(f'WVEL written in {int(time.time() - t1)} seconds')
            
            recov[count] = 1
            count = count + 1
            np.save('recovery.npy', recov)
        
            dt = int(time.time() - t_tot)
            avgt.append(dt)
            print(f'Count = {count} | iter completed in {dt} seconds (average = {np.mean(avgt)})')
