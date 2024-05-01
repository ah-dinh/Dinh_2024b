import sys
sys.path.insert(0,'/data/SO2/SO24/ANDY/SOHI/Notebooks/4_Parcels/Scripts/Advection/source')

from Repeated_Releases import run_obj
import argparse
from datetime import timedelta

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--name')
args = parser.parse_args()

if args.name == 'pineisland':
    lat_paths = '/data/SO2/SO24/ANDY/SOHI/Notebooks/4_Parcels/inputs/run7/pineisland/lats.npy'
    lon_paths = '/data/SO2/SO24/ANDY/SOHI/Notebooks/4_Parcels/inputs/run7/pineisland/lons.npy'
    dep_paths = '/data/SO2/SO24/ANDY/SOHI/Notebooks/4_Parcels/inputs/run7/pineisland/depths.npy'
    save_to = "/data/SO2/SO24/ANDY/SOHI/Notebooks/4_Parcels/outputs/R8_ASE_5min/pineisland.zarr"
elif args.name == 'thwaites':
    lat_paths = '/data/SO2/SO24/ANDY/SOHI/Notebooks/4_Parcels/inputs/run7/thwaites/lats.npy'
    lon_paths = '/data/SO2/SO24/ANDY/SOHI/Notebooks/4_Parcels/inputs/run7/thwaites/lons.npy'
    dep_paths = '/data/SO2/SO24/ANDY/SOHI/Notebooks/4_Parcels/inputs/run7/thwaites/depths.npy'
    save_to = "/data/SO2/SO24/ANDY/SOHI/Notebooks/4_Parcels/outputs/R8_ASE_5min/thwaites.zarr"
elif args.name == 'smith':
    lat_paths = '/data/SO2/SO24/ANDY/SOHI/Notebooks/4_Parcels/inputs/run7/smith/lats.npy'
    lon_paths = '/data/SO2/SO24/ANDY/SOHI/Notebooks/4_Parcels/inputs/run7/smith/lons.npy'
    dep_paths = '/data/SO2/SO24/ANDY/SOHI/Notebooks/4_Parcels/inputs/run7/smith/depths.npy'
    save_to = "/data/SO2/SO24/ANDY/SOHI/Notebooks/4_Parcels/outputs/R8_ASE_5min/smith.zarr"
elif args.name == 'kohler':
    lat_paths = '/data/SO2/SO24/ANDY/SOHI/Notebooks/4_Parcels/inputs/run7/kohler/lats.npy'
    lon_paths = '/data/SO2/SO24/ANDY/SOHI/Notebooks/4_Parcels/inputs/run7/kohler/lons.npy'
    dep_paths = '/data/SO2/SO24/ANDY/SOHI/Notebooks/4_Parcels/inputs/run7/kohler/depths.npy'
    save_to = "/data/SO2/SO24/ANDY/SOHI/Notebooks/4_Parcels/outputs/R8_ASE_5min/kohler.zarr"
    
    
data_path = "/data/SO2/SO24/ANDY/SOHI/Data/Models/SOHI/Annum/Amundsen.nc"

obj = run_obj(lat_paths=lat_paths, 
              lon_paths=lon_paths, 
              dep_paths=dep_paths, 
              save_to=save_to,
              data_path = data_path)

obj.runtime1 = timedelta(days=365)
obj.repeatdt = timedelta(days=1)   
obj.runtime2 = timedelta(days=365*3) ## without repeated release 
obj.dt = -timedelta(seconds=300)    ## 20 min
obj.outputdt = timedelta(hours=24)   ## Frequency of outputs
obj.maxage = 60*60*24*365*3  
obj.chunk = 137

if __name__ == "__main__":
    obj.run()