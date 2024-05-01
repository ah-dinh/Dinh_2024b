import math
    
def function_sample(particle, fieldset, time):  
    particle.temperature = fieldset.T[time, particle.depth, particle.lat, particle.lon]
    particle.salinity = fieldset.S[time, particle.depth, particle.lat, particle.lon]
    
def function_age(particle, fieldset, time):
    particle.age += math.fabs(particle.dt)
    if particle.age >= fieldset.maxage:
        particle.delete()
        
def function_oob(particle, fieldset, time):
    particle.delete()
    
# def BrownianMotion2D(particle, fieldset, time):

#     kh_meridional = fieldset.Kh_meridional[time, particle.depth, particle.lat, particle.lon]
#     kh_zonal = fieldset.Kh_zonal[time, particle.depth, particle.lat, particle.lon]
#     dx = fieldset.meshSize[time, particle.depth, particle.lat, particle.lon]
#     dx0 = 1000

#     particle.lat += random.uniform(-1., 1.) * math.sqrt(2*math.fabs(particle.dt) * kh_meridional * math.pow(dx/dx0, 1.33))
#     particle.lon += random.uniform(-1., 1.) * math.sqrt(2*math.fabs(particle.dt) * kh_zonal      * math.pow(dx/dx0, 1.33))
  