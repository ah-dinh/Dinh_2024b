from parcels import ErrorCode, FieldSet,ParticleSet, JITParticle, Variable, AdvectionRK4_3D
from datetime import datetime, timedelta
from operator import attrgetter
import numpy as np
import netCDF4 as nc
import os
import math
import zarr

from kernels import function_sample, function_age, function_oob


class run_obj:
    
    def __init__(self, lat_paths, lon_paths, dep_paths, save_to, data_path):
        self.plats = np.load(lat_paths)
        self.plons = np.load(lon_paths)
        self.pdeps = np.load(dep_paths)
        self.save_to = save_to
        
        self.nparticles = len(self.plats)
        
        if os.path.isdir(self.save_to):
            self.mkpset = False
        else:
            self.mkpset = True
        
        assert len(self.plats) == len(self.plons)
        assert len(self.plons) == len(self.pdeps)
        
        print(f"{len(self.plats)} particles loaded!")
       
        
        ### Parameters
        self.cube_path = data_path #data
        
        
        self.runtime1 = None  ## with repeated release
        self.repeatdt = None   ## release frequency
        self.runtime2 = None  ## without repeated release
        
        self.dt = None    ## Advection timestep
        
        self.outputdt = None  ## Frequency of outputs
        
        self.maxage = None    ## Max age for particles (in seconds)
        
        self.chunk = 140
        
    def run(self):
        
        ## Define dimensions 
        filenames = {'U': self.cube_path, 
                     'V': self.cube_path, 
                     'W': self.cube_path, 
                     'T': self.cube_path, 
                     'S': self.cube_path}
        
        variables = {'U': 'UVEL', 
                     'V': 'VVEL', 
                     'W': 'WVEL', 
                     'T':'THETA', 
                     'S':'SALT'}
        
        dimensions = {'lon': 'XG', 
                      'lat': 'YG', 
                      'depth': 'RF'}
        
        ## Set time for each iteration
        cube = nc.Dataset(self.cube_path)
        cubetime = [datetime(2005, 1, 1, 0) + timedelta(seconds = i*60.0) for i in cube['date'][:]]
        cubetime = np.expand_dims(np.asarray([np.datetime64(i) for i in cubetime]), axis=0)
        
        ## Create field set
        fieldset = FieldSet.from_mitgcm(filenames, 
                                        variables, 
                                        dimensions, 
                                        timestamps = cubetime, 
                                        time_periodic = timedelta(days=365),
                                        allow_time_extrapolation = False) 

        ## Set interpolation method
        fieldset.T.interp_method = 'nearest'
        fieldset.S.interp_method = 'nearest'
        fieldset.add_constant('maxage', self.maxage)
      
        class p_params(JITParticle):                   
                temperature = Variable('temperature', initial=attrgetter('T'), dtype=np.float32)
                salinity = Variable('salinity', initial=attrgetter('S'), dtype=np.float32)
                age = Variable('age', initial=0., dtype=np.float32)
        
       
        
        if self.mkpset:

            pset = ParticleSet.from_list(fieldset = fieldset,   
                                pclass = p_params, 
                                lon = self.plons, 
                                lat = self.plats,
                                depth = self.pdeps,
                                repeatdt = self.repeatdt)
            
        else:

            pset = ParticleSet.from_particlefile(fieldset = fieldset,  
                                                     pclass = p_params,  
                                                     filename = self.save_to, 
                                                     restart=True, 
                                                     repeatdt=self.repeatdt)
    
        output_file = pset.ParticleFile(name = self.save_to, outputdt = self.outputdt, 
                                        chunks = (self.nparticles, self.chunk))
            
        print('Running with particle release...')
        pset.execute(AdvectionRK4_3D + pset.Kernel(function_sample) + pset.Kernel(function_age),                 
                             runtime = self.runtime1,    
                             dt = self.dt,
                             output_file = output_file,
                             recovery = {ErrorCode.ErrorOutOfBounds: function_oob})

        print("Particle Release Completed! Continuing run...")
        ## Stop Particle Release
        pset.repeatdt = None 

        ## Run for another y days
        pset.execute(AdvectionRK4_3D + pset.Kernel(function_sample) + pset.Kernel(function_age),                
                             runtime= self.runtime2,    
                             dt = self.dt,
                             output_file = output_file,
                             recovery = {ErrorCode.ErrorOutOfBounds: function_oob})
        print("\nCompleted")
        


            
class run_obj_no_sampling:
    
    def __init__(self, lat_paths, lon_paths, dep_paths, save_to, data_path):
        self.plats = np.load(lat_paths)
        self.plons = np.load(lon_paths)
        self.pdeps = np.load(dep_paths)
        self.save_to = save_to
        
        self.nparticles = len(self.plats)
        
        if os.path.isdir(self.save_to):
            self.mkpset = False
        else:
            self.mkpset = True
        
        assert len(self.plats) == len(self.plons)
        assert len(self.plons) == len(self.pdeps)
        
        print(f"{len(self.plats)} particles loaded!")
       
        
        ### Parameters
        self.cube_path = data_path #data
        
        
        self.runtime1 = None  ## with repeated release
        self.repeatdt = None   ## release frequency
        self.runtime2 = None  ## without repeated release
        
        self.dt = None    ## Advection timestep
        
        self.outputdt = None  ## Frequency of outputs
        
        self.maxage = None          ## Max age for particles (in seconds)
        
        self.chunk = 100
        
    def run(self):
        
        ## Define dimensions 
        filenames = {'U': self.cube_path, 
                     'V': self.cube_path, 
                     'W': self.cube_path}
        
        variables = {'U': 'UVEL', 
                     'V': 'VVEL', 
                     'W': 'WVEL'}
        
        dimensions = {'lon': 'XG', 
                      'lat': 'YG', 
                      'depth': 'RF'}
        
        ## Set time for each iteration
        cube = nc.Dataset(self.cube_path)
        cubetime = [datetime(2005, 1, 1, 0) + timedelta(seconds = i*60.0) for i in cube['date'][:]]
        cubetime = np.expand_dims(np.asarray([np.datetime64(i) for i in cubetime]), axis=0)
        
        ## Create field set
        fieldset = FieldSet.from_mitgcm(filenames, 
                                        variables, 
                                        dimensions, 
                                        timestamps = cubetime, 
                                        time_periodic = timedelta(days=365),
                                        allow_time_extrapolation = False) 

        ## Set interpolation method
        fieldset.interp_method = 'cgrid_tracer'
        fieldset.add_constant('maxage', self.maxage)
      
        class p_params(JITParticle):                   
                age = Variable('age', initial=0., dtype=np.float32)
        
        if self.mkpset:

            pset = ParticleSet.from_list(fieldset = fieldset,   
                                pclass = p_params, 
                                lon = self.plons, 
                                lat = self.plats,
                                depth = self.pdeps,
                                repeatdt = self.repeatdt)
            
        else:

            pset = ParticleSet.from_particlefile(fieldset = fieldset,  
                                                     pclass = p_params,  
                                                     filename = self.save_to, 
                                                     restart=True, 
                                                     restarttime=None, 
                                                     repeatdt=self.repeatdt)
    
        output_file = pset.ParticleFile(name = self.save_to, outputdt = self.outputdt,
                                       chunks = (self.nparticles, self.chunk))
            
        print('Running with particle release...')
        pset.execute(AdvectionRK4_3D + pset.Kernel(function_age),                 
                             runtime = self.runtime1,    
                             dt = self.dt,
                             output_file = output_file,
                             recovery = {ErrorCode.ErrorOutOfBounds: function_oob})

        print("Particle Release Completed! Continuing run...")
        ## Stop Particle Release
        pset.repeatdt = None 

        ## Run for another y days
        pset.execute(AdvectionRK4_3D + pset.Kernel(function_age),                
                             runtime= self.runtime2,    
                             dt = self.dt,
                             output_file = output_file,
                             recovery = {ErrorCode.ErrorOutOfBounds: function_oob})
        print("\nCompleted")
            
            
            
    