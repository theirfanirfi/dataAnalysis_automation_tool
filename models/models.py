import numpy as np
"""
Modeling Section:
    definition of various filtration models and inclusion into script:
    - Standard 
    - Cake filtration
    - Intermediate clogging
    - Complete clogging
    - Combined Intermediate-Adsorption
"""

# Function definition of the filtration model
# First model is based on the throughput V
# Second model is based on the Flux J -> appendix _flux
statistics = ""
max_model_Value = 0
max_model_name = ""

def vmax_standard(time,flux_0,parameter_ks):
    global statistics
    global max_model_Value
    global max_model_name
    value = (1/(flux_0*time)+(parameter_ks/2))**(-1)
    if value > max_model_Value:
        max_model_Value = value
        max_model_name = "VMAX Standard"

    statistics += "\nVMA Standard: "+str(value)
    return value

def vmax_standard_flux(time, flux_0, parameter_ks):
    global statistics
    global max_model_Value
    global max_model_name
    value = -(1/(flux_0*time)+(parameter_ks/2))**(-2)*(1/(flux_0*time))**2
    if value > max_model_Value:
        max_model_Value = value
        max_model_name = "VMAX Standard FLUX"

    statistics += "\nVMAX Standard FLUX: " + str(value)
    return value

def cake_filtration(time,flux_0,parameter_kc):
    return (1/(parameter_kc*flux_0))*((1+2*parameter_kc*(flux_0)**2*time)**0.5-1)

def cake_filtration_flux(time, flux_0, parameter_kc):
    return (1/(1+2*parameter_kc*flux_0**2*time)**0.5)*flux_0

def intermediate_filtration(time,flux_0,parameter_ki):
    return (1/parameter_ki)*np.log10(1+parameter_ki*flux_0*time)

def intermediate_filtration_flux(volume,flux_0,parameter_ki):
    return np.exp(-parameter_ki*volume)*flux_0

def complete_clogging(time,flux_0,parameter_kb):
    return (flux_0/parameter_kb)*(1-np.exp(-parameter_kb*time))

def complete_clogging_flux(time,flux_0,parameter_kb):
    return (np.exp(-parameter_kb*time)*flux_0)

def combined_intermediate(time, flux_0,parameter_ki, parameter_ka):
    return (1/parameter_ki)*np.log10(parameter_ki*flux_0/(5*parameter_ka)*(1-(1-parameter_ka*time)**5)+1)

def combined_intermediate_flux(VolumeTime, flux_0,parameter_ki, parameter_ka):
    volume, time = VolumeTime
    return ((np.exp(-parameter_ki*volume))*((1-parameter_ka*time)**4))*flux_0
    
# Derivative functions of the filtration models
def vmax_standard_derivative(time, flux_0, parameter1):
    return 1/(flux_0*time**2*(parameter1/2 + 1/(flux_0*time))**2)

def cake_filtration_derivative(time, flux_0, parameter1):
    return 1.0*flux_0/(2*flux_0**2*parameter1*time + 1)**0.5

def intermediate_filtration_derivative(time, flux_0, parameter1):
    return flux_0/(flux_0*parameter1*time + 1)

def complete_clogging_derivative(time, flux_0, parameter1):
    return flux_0*np.exp(-parameter1*time)

def combined_derivative(time, flux_0, parameter1, parameter2):
    return flux_0*(-parameter2*time + 1)**4/(flux_0*parameter1*(1 - (-parameter2*time + 1)**5)/(5*parameter2) + 1)

def combined_intermediate_flux2(VolumeTime, flux_0,parameter_ki, parameter_ka):
    volume, time = VolumeTime
    x1 = ((np.exp(-parameter_ki*volume))*((1-parameter_ka*time)**4))*flux_0
    x2 = ((np.exp(-parameter_ki*time))*((1-parameter_ka*volume)**4))*flux_0
    x = (x1,x2)
    return x


# Set values of time range for fitting (in min)
fit_time_range = np.linspace(0,1000,100)
# Set values of load range for fitting (in mL)
fit_load_range = np.linspace(0,2000,100)


def vmax_standard_flux2(volume, parameter_ks):
    return (1-((volume*parameter_ks)/2))**2
    
def cake_filtration_flux2(time, flux_0, parameter_kc):
    return (1/(1+2*parameter_kc*flux_0**2*time)**0.5)

def intermediate_filtration_flux2(volume,parameter_ki):
    return np.exp(-parameter_ki*volume)

def complete_clogging_flux2(time,parameter_kb):
    return np.exp(-parameter_kb*time)

def combined_intermediate_flux2(VolumeTime,parameter_ki, parameter_ka):
    volume, time = VolumeTime
    return ((np.exp(-parameter_ki*volume))*((1-parameter_ka*time)**4))

# print(max_model_name, max_model_name)
# print(statistics)