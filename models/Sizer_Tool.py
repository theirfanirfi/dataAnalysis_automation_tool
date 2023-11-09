import tkinter as tk
from tkinter import filedialog
from tkinter import *
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.optimize import *
import numpy as np
from fpdf import FPDF
from datetime import date
from datetime import datetime
from pandas.plotting import table
from scipy.integrate import quad
from sympy.solvers.diophantine.diophantine import diop_solve
from sympy import *



# Open window for .csv file selection
# Multiple file selections at once
root = tk.Tk()
root.withdraw()
root.call('wm', 'attributes', '.', '-topmost', True)
files = filedialog.askopenfilename(multiple=True) 
# gui tk
var = root.tk.splitlist(files)
filePaths = []
for f in var:
    filePaths.append(f)


# dictionary for run information
filter_runs = {}
# list including all run data
results_list = []


# generate result list as Table_ for all runs and include into the results_list
count = 0
for path in filePaths:
    table_string = f'Table_{count}' 
    locals()[table_string]= pd.read_csv(path, sep= ",", header = 0 , index_col=False)
    filter_runs[count] = {}
    for name in locals()[table_string].columns:
        filter_runs[count][name] = locals()[table_string].iloc[0][name]
    locals()[table_string] = locals()[table_string].iloc[1:-1,0:4]
    locals()[table_string].columns = locals()[table_string].iloc[0]
    locals()[table_string].drop(index = locals()[table_string].index[0],axis =0, inplace = True)
    locals()[table_string] = locals()[table_string].astype(float)
    results_list.append(locals()[table_string])
    count += 1
    
#drop out erroneous rows where run was already stopped and flux = 0
counter = 0
for results in results_list:
    count = 0
    boolean_results = []
    while count+1 < len(results['vol (mL)']):
        boolean_results.append(results['vol (mL)'].iloc[count+1] - results['vol (mL)'].iloc[count] > 0.5)
        count += 1
    boolean_results.append(boolean_results[-1])
    results_list[counter] = results[boolean_results]
    counter += 1


def calculate():
    global smoothing_factor
    global membrane_area
    smoothing_factor = int(float(smoothing_factor_entry.get()))
    membrane_area = float(membrane_area_entry.get())/10000
    root.quit()

root = Tk()
root.title("Smoothing Factor & Membrane Area")

smoothing_factor_label = Label(root, text="Enter smoothing factor:")
smoothing_factor_label.pack()

smoothing_factor_entry = Entry(root)
smoothing_factor_entry.pack()

membrane_area_label = Label(root, text="Enter membrane area (in cm2):")
membrane_area_label.pack()

membrane_area_entry = Entry(root)
membrane_area_entry.pack()

calculate_button = Button(root, text="Submit", command=calculate)
calculate_button.pack()

root.mainloop()
root.destroy()

# Code continues here, after the GUI window closes
print("Values stored as 'smoothing_factor' and 'membrane_area':")
print("Smoothing factor:", smoothing_factor)
print("Membrane area:", membrane_area, "(m^2)")




# calculation of flux and inclusion into results_list
# initialize count for next loop
count_2 = 0
for results in results_list:
    if len(results) < smoothing_factor*2:
        print('Please reduce smoothing factor. Data points not sufficient.')
        
    vol = results['vol (mL)']
    time = results['time (min)']
    flux = (vol.shift(-smoothing_factor) - vol) / (time.shift(-smoothing_factor) - time)
    flux = flux.rolling(window=smoothing_factor).mean()
    flux = flux.fillna(method='bfill')
    flux = flux.fillna(method='ffill')
    
    results_list[count_2]['flux (LMH)'] = flux * 60 / 1000 / membrane_area
    results_list[count_2]['flux (LMM)'] = flux / 1000 / membrane_area
    results_list[count_2]['flux (LMS)'] = flux /  60 /1000 / membrane_area
    results_list[count_2]['flux J/J0 (-)'] = results_list[count_2]['flux (LMH)'] / results_list[count_2]['flux (LMH)'].iloc[0]
    count_2 += 1 


#drop out rows where flux is NaN
for i, results in enumerate(results_list):
    results = results[np.isnan(results['flux (LMH)']) == False]
    results['vol (L)'] = results['vol (mL)']/1000
    results_list[i] = results

#insert loading in L/m²
for i, results in enumerate(results_list):
    results['load (L/m²)'] = results['vol (mL)']/1000/membrane_area
    results_list[i] = results

def plot_results(x_col, y_col, x_label, y_label, save_file):
    fig = plt.figure()
    for i, results in enumerate(results_list):
        plot_label = f'{filter_runs[i]["Comments"]}'
        plt.plot(results[x_col], results[y_col], label=plot_label)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xlim(0)
    plt.ylim(0)
    plt.legend(prop={'size':6})
    plt.savefig(save_file, dpi=400)

plot_results('time (min)', 'load (L/m²)', 'Time (min)', 'Load (L/m²)', 'loading.png')
plot_results('time (min)', 'flux (LMH)', 'Time (min)', 'Flux (LMH)', 'flux.png')
plot_results('load (L/m²)', 'flux (LMH)', 'Load (L/m²)', 'Flux (LMH)', 'flux_vs_load.png')
plot_results('load (L/m²)', 'flux J/J0 (-)', 'Load (L/m²)', 'J/J0 (-)', 'J_vs_load.png')

#Check data quality
delta_flux = [0]*len(results_list)
for i, results in enumerate(results_list):
    delta_flux1 = (results['flux (LMH)'].iloc[0]-results['flux (LMH)'].iloc[-1])/results['flux (LMH)'].iloc[0]*100
    delta_flux[i] = delta_flux1
    if delta_flux[i] < 11:
        print(f'Flux decrease of run {i} lower than 10%')


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

def vmax_standard(time,flux_0,parameter_ks):
    return (1/(flux_0*time)+(parameter_ks/2))**(-1)

def vmax_standard_flux(time, flux_0, parameter_ks):
    return -(1/(flux_0*time)+(parameter_ks/2))**(-2)*(1/(flux_0*time))**2

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



# Model fitting for all models in loading mode
models_list =[vmax_standard, cake_filtration, intermediate_filtration, complete_clogging, combined_intermediate]
counter= 0
while counter < len(models_list):
    load_fit = []
    r2 = []
    flux_0 =[]
    load_fit_matrix=[]
    parameter1 = []
    parameter2 = []
    for results in results_list:
        if models_list[counter].__name__ == 'combined_intermediate':
            popt, cir = curve_fit(models_list[counter], results['time (min)'], results['load (L/m²)'], maxfev = 10000, p0=(results['flux (LMH)'].iloc[0],1,1))
            a, b, c = popt
            load_fit_series = models_list[counter](fit_time_range, a, b,c)
            load_fit_df = pd.DataFrame(load_fit_series, columns = ['fit vol(mL)'])
            load_fit.append(load_fit_df)
            corr_matrix = np.corrcoef(results['load (L/m²)'],models_list[counter](results['time (min)'], a, b,c))
            corr = corr_matrix[0,1]**2
            r2.append(corr)
            flux_0.append(a)
            parameter1.append(b)
            parameter2.append(c)

        else:
            if models_list[counter].__name__ == 'vmax_standard':
                popt, cir = curve_fit(models_list[counter], results['time (min)'], results['load (L/m²)'], maxfev = 10000, p0=(results['flux (LMM)'].iloc[0],0.1))
            else:
                popt, cir = curve_fit(models_list[counter], results['time (min)'], results['load (L/m²)'], maxfev = 10000, p0=(results['flux (LMM)'].iloc[0],1))
            a, b = popt
            load_fit_series = models_list[counter](fit_time_range, a, b)
            load_fit_df = pd.DataFrame(load_fit_series, columns = ['fit vol(mL)'])
            load_fit.append(load_fit_df)
            corr_matrix = np.corrcoef(results['load (L/m²)'],models_list[counter](results['time (min)'], a, b))
            corr = corr_matrix[0,1]**2
            r2.append(corr)
            flux_0.append(a)
            parameter1.append(b)      
    if counter == 0:
        load_fit_matrix.append(load_fit)
        flux_initial = pd.DataFrame(flux_0, columns =[models_list[counter].__name__])
        parameter_matrix = pd.DataFrame(parameter1, columns = [models_list[counter].__name__])
        r_squared = pd.DataFrame(r2, columns = [models_list[counter].__name__])  
    else:
        load_fit_matrix.append(load_fit)
        flux_initial[models_list[counter].__name__] = pd.DataFrame(flux_0)    
        parameter_matrix[models_list[counter].__name__] = pd.DataFrame(parameter1)    
        r_squared[models_list[counter].__name__ ] = pd.DataFrame(r2)  
    if models_list[counter].__name__ == 'combined_intermediate':
       parameter_matrix[f'{models_list[counter].__name__}2'] = pd.DataFrame(parameter2)
    fig = plt.figure()
    counter2 = 0
    for results in results_list:
        plot_label = f'{filter_runs[counter2]["Run No."]} {filter_runs[counter2]["Stand ID"]}'
        plt.plot(fit_time_range,load_fit[counter2],label = plot_label)
        counter2 += 1
    plt.xlabel('Time (min)')
    plt.ylabel('Load (L/m²)')
    plt.title(models_list[counter].__name__)
    plt.xlim(0) 
    plt.ylim(0)
    plt.legend()
    plt.show()
    counter += 1



# Model fitting for all models in flux mode
models_list_flux =[vmax_standard_flux, cake_filtration_flux, intermediate_filtration_flux, complete_clogging_flux, combined_intermediate_flux]
counter= 0
while counter < len(models_list_flux):
    flux_fit = []
    r2_flux = []
    flux_0 =[]
    parameter = []
    parameter1 = []
    parameter2 = []
    flux_fit_matrix= []
    for results in results_list:
        if models_list_flux[counter].__name__ == 'combined_intermediate_flux':
            popt, cir = curve_fit(models_list_flux[counter], (results['vol (mL)'],results['time (min)']), results['flux (LMH)'], 
                                  maxfev = 10000, p0=(results['flux (LMH)'].iloc[0],0.001,0.0001),bounds=([0,0.00001,0.000001],[100000,0.1,0.001]))
            a, b, c = popt
            flux_fit_series = models_list_flux[counter]((fit_load_range, fit_time_range), a, b,c)
            flux_fit_df = pd.DataFrame(flux_fit_series, columns = ['fit flux (LMH)'])
            flux_fit.append(flux_fit_df)
            corr_matrix = np.corrcoef(results['flux (LMH)'],models_list_flux[counter]((results['vol (mL)'],results['time (min)']), a, b,c))
            corr = corr_matrix[0,1]**2
            r2_flux.append(corr)
            flux_0.append(a)
            parameter1.append(b)
            parameter2.append(c)

        elif models_list_flux[counter].__name__ == 'vmax_standard_flux':
            popt, cir = curve_fit(models_list_flux[counter], results['load (L/m²)'], results['flux (LMH)'], maxfev = 100000, p0=(results['flux (LMH)'].iloc[0],0.001), bounds=([0, 0.0000001],[100000,0.01]),method='trf')
            a,b = popt
            flux_fit_series = models_list_flux[counter](fit_load_range, a,b)
            flux_fit_df = pd.DataFrame(flux_fit_series, columns = ['fit Flux (LMH)'])
            flux_fit.append(flux_fit_df)
            corr_matrix = np.corrcoef(results['flux (LMH)'],models_list_flux[counter](results['load (L/m²)'], a,b))
            corr = corr_matrix[0,1]**2
            r2_flux.append(corr)
            flux_0.append(a)
            parameter1.append(b) 
        elif  models_list_flux[counter].__name__ == 'intermediate_filtration_flux':
            popt, cir = curve_fit(models_list_flux[counter], results['vol (mL)'], results['flux (LMH)'], maxfev = 100000, p0=(results['flux (LMH)'].iloc[0],1))
            a, b = popt
            flux_fit_series = models_list_flux[counter](fit_load_range, a, b)
            flux_fit_df = pd.DataFrame(flux_fit_series, columns = ['fit Flux (LMH)'])
            flux_fit.append(flux_fit_df)
            corr_matrix = np.corrcoef(results['flux (LMH)'],models_list_flux[counter](results['vol (mL)'], a, b))
            corr = corr_matrix[0,1]**2
            r2_flux.append(corr)
            flux_0.append(a)
            parameter1.append(b)                   
        else:
            popt, cir = curve_fit(models_list_flux[counter], results['time (min)'], results['flux (LMH)'], maxfev = 10000, p0=(results['flux (LMM)'].iloc[0],1))
            a, b = popt
            flux_fit_series = models_list_flux[counter](fit_time_range, a, b)
            flux_fit_df = pd.DataFrame(flux_fit_series, columns = ['fit flux (LMH)'])
            flux_fit.append(flux_fit_df)
            corr_matrix = np.corrcoef(results['flux (LMH)'],models_list_flux[counter](results['time (min)'], a, b))
            corr = corr_matrix[0,1]**2
            r2_flux.append(corr)
            flux_0.append(a)
            parameter1.append(b)           
    counter2 = 0
    flux_fit_Data = pd.DataFrame()
    while counter2 < len(flux_fit):        
        flux_fit_Data[f'{counter2}'] = flux_fit[counter2] 
        counter2 += 1
    if counter == 0:
        flux_fit_matrix.append(flux_fit_Data)
        flux_initial_flux = pd.DataFrame(flux_0, columns =[models_list[counter].__name__])
        parameter_matrix_flux = pd.DataFrame(parameter1, columns = [models_list[counter].__name__])
        r_squared_flux = pd.DataFrame(r2_flux, columns = [models_list_flux[counter].__name__])  
    else:
        flux_fit_matrix.append(flux_fit_Data)
        flux_initial_flux[models_list[counter].__name__] = pd.DataFrame(flux_0)   
        parameter_matrix_flux[models_list[counter].__name__] = pd.DataFrame(parameter1)    
        r_squared_flux[models_list_flux[counter].__name__ ] = pd.DataFrame(r2_flux)  
    fig = plt.figure()
    counter2 = 0
    for results in results_list:
        plot_label = f'{filter_runs[counter2]["Run No."]} {filter_runs[counter2]["Stand ID"]}'
        if models_list_flux[counter].__name__ == 'vmax_standard_flux' or models_list_flux[counter].__name__ == 'intermediate_filtration_flux':
            plt.plot(fit_load_range,flux_fit[counter2],label = plot_label)
        else:
            plt.plot(fit_time_range,flux_fit[counter2],label = plot_label)
        counter2 += 1
    if models_list[counter].__name__ == 'combined_intermediate':
        parameter_matrix_flux[f'{models_list[counter].__name__}2'] = pd.DataFrame(parameter2)
    if models_list_flux[counter].__name__ == 'vmax_standard_flux':
        plt.xlabel('Load (L/m²)')
    elif models_list_flux[counter].__name__ == 'intermediate_filtration_flux':
        plt.xlabel('Volume (mL)')
    else:
        plt.xlabel('Time (min)')
    plt.ylabel('Flux (LMH)')
    plt.title(models_list_flux[counter].__name__)
    plt.xlim(0) 
    plt.ylim(0)
    plt.legend()
    plt.show()
    counter += 1

                                 
 
              

#Calculation of Vmax through the derivative functions of the loading functions
models_list_derivative = [vmax_standard_derivative, cake_filtration_derivative, intermediate_filtration_derivative, complete_clogging_derivative, combined_derivative]
counter = 0
while counter < len(models_list):
    counter2 = 0
    Vmax_single =[]
    while counter2 < len(parameter_matrix):
        if models_list[counter].__name__ == 'combined_intermediate':
            Vmax_interim = fsolve(models_list_derivative[counter],10, args=(flux_initial[models_list[counter].__name__][counter2],
                                                                            parameter_matrix[models_list[counter].__name__][counter2], parameter_matrix[f'{models_list[counter].__name__}2'][counter2]), maxfev= 100000)
            Vmax_interim = Vmax_interim[0]
            Vmax_single.append(Vmax_interim)
        else:
            Vmax_interim = fsolve(models_list_derivative[counter],10,args=(flux_initial[models_list[counter].__name__][counter2],parameter_matrix[models_list[counter].__name__][counter2]), maxfev= 100000)
            Vmax_interim = Vmax_interim[0]
            Vmax_single.append(Vmax_interim)
        counter2 += 1        
    if counter == 0:
        Vmax = pd.DataFrame(Vmax_single, columns=[models_list[counter].__name__])
    else:
        Vmax[models_list[counter].__name__] = pd.DataFrame(Vmax_single)
    counter += 1
    
    
#Calculation of time or volume at flux=0 through the flux functions
models_list_flux =[vmax_standard_flux, cake_filtration_flux, intermediate_filtration_flux, complete_clogging_flux, combined_intermediate_flux2]
counter = 0
while counter < len(models_list):
    counter2 = 0
    Vmax_single =[]
    while counter2 < len(parameter_matrix_flux):
        if models_list_flux[counter].__name__ == 'combined_intermediate_flux2':
            Vmax_interim = fsolve(models_list_flux[counter],(10,10), args=(flux_initial_flux[models_list[counter].__name__][counter2], parameter_matrix_flux[models_list[counter].__name__][counter2], parameter_matrix_flux[f'{models_list[counter].__name__}2'][counter2]), maxfev= 100000)
            Vmax_interim = Vmax_interim[0]
            Vmax_single.append(Vmax_interim)
        else:
            Vmax_interim = fsolve(models_list_flux[counter],10,args=(flux_initial_flux[models_list[counter].__name__][counter2],parameter_matrix_flux[models_list[counter].__name__][counter2]), maxfev= 100000)
            Vmax_interim = Vmax_interim[0]
            Vmax_single.append(Vmax_interim)
        counter2 += 1        
    if counter == 0:
        Vmax_flux = pd.DataFrame(Vmax_single, columns=[models_list[counter].__name__])
    else:
        Vmax_flux[models_list[counter].__name__] = pd.DataFrame(Vmax_single)
    counter += 1

  

# Integration of volume over time for throughput calculation
models_list_integral = [cake_filtration, complete_clogging, combined_intermediate]
counter2 = 0
for model in models_list_integral:
    counter = 0
    integral =[]
    while counter < len(Vmax_flux):
        complete_integral = quad(complete_clogging_flux, 0, Vmax_flux[model.__name__][counter], args= (flux_initial_flux[model.__name__][counter],parameter_matrix_flux[model.__name__][counter]))
        integral.append(complete_integral)
        counter += 1
    if counter2 == 0:
        Integrals_Models = pd.DataFrame(integral, columns=[model.__name__,f'{model.__name__} error'])
    else:
        Integrals_Models_intermediate = pd.DataFrame(integral, columns=[model.__name__,f'{model.__name__} error'])
        Integrals_Models[model.__name__] = Integrals_Models_intermediate[model.__name__]
        Integrals_Models[f'{model.__name__} error'] = Integrals_Models_intermediate[f'{model.__name__} error']
    counter2 += 1
  

 
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


# Model fitting for all models in flux mode for J/J0
models_list_flux =[vmax_standard_flux2, cake_filtration_flux2, intermediate_filtration_flux2, complete_clogging_flux2, combined_intermediate_flux2]
counter= 0
while counter < len(models_list_flux):
    flux_fit = []
    r2_flux_J = []
    parameter_J = []
    parameter1 = []
    parameter2 = []
    flux_fit_matrix_J=[]
    for results in results_list:
        if models_list_flux[counter].__name__ == 'combined_intermediate_flux2':
            popt, cir = curve_fit(models_list_flux[counter], (results['vol (mL)'],results['time (min)']), results['flux J/J0 (-)'], 
                                  maxfev = 10000000, p0=(0.01,0.0001),bounds=([0.001,0.0000001],[1,0.001]))
            b, c = popt
            flux_fit_series = models_list_flux[counter]((fit_load_range, fit_time_range), b,c)
            flux_fit_df = pd.DataFrame(flux_fit_series, columns = [f'fit flux J/J0 (-)'])
            flux_fit_df['Load (L/m²)'] = fit_load_range
            flux_fit.append(flux_fit_df)
            corr_matrix = np.corrcoef(results['flux J/J0 (-)'],models_list_flux[counter]((results['vol (mL)'],results['time (min)']), b,c))
            corr = corr_matrix[0,1]**2
            r2_flux.append(corr)
            parameter1.append(b)
            parameter2.append(c)
        elif models_list_flux[counter].__name__ == 'vmax_standard_flux2':
            popt, cir = curve_fit(models_list_flux[counter], results['load (L/m²)'], results['flux J/J0 (-)'], maxfev=100000, p0=(0.00001), bounds=(0.000001,0.01))
            b = popt
            flux_fit_series = models_list_flux[counter](fit_load_range, b)
            flux_fit_df = pd.DataFrame(flux_fit_series, columns = [f'fit flux J/J0 (-)'])
            flux_fit_df['Load (L/m²)'] = fit_load_range
            flux_fit.append(flux_fit_df)
            corr_matrix = np.corrcoef(results['flux J/J0 (-)'],models_list_flux[counter](results['load (L/m²)'], b))
            corr = corr_matrix[0,1]**2
            r2_flux.append(corr)
            parameter1.append(b) 
        elif  models_list_flux[counter].__name__ == 'intermediate_filtration_flux2':
            popt, cir = curve_fit(models_list_flux[counter], results['vol (mL)'], results['flux J/J0 (-)'], maxfev = 100000, p0=(1))
            b = popt
            flux_fit_series = models_list_flux[counter](fit_load_range, b)
            flux_fit_df = pd.DataFrame(flux_fit_series, columns = [f'fit flux J/J0 (-)'])
            flux_fit_df['Load (L/m²)'] = fit_load_range
            flux_fit.append(flux_fit_df)
            corr_matrix = np.corrcoef(results['flux J/J0 (-)'],models_list_flux[counter](results['vol (mL)'], b))
            corr = corr_matrix[0,1]**2
            r2_flux.append(corr)
            parameter1.append(b)                   
        elif models_list_flux[counter].__name__ == 'cake_filtration_flux2':
            popt, cir = curve_fit(models_list_flux[counter], results['time (min)'], results['flux J/J0 (-)'], maxfev = 10000, p0=(results['flux (LMM)'].iloc[0],0.001))
            a, b = popt
            flux_fit_series = models_list_flux[counter](fit_time_range, a, b)
            flux_fit_df = pd.DataFrame(flux_fit_series, columns = [f'fit flux J/J0 (-)'])
            flux_fit_df['Time (min)'] = fit_time_range
            flux_fit.append(flux_fit_df)
            corr_matrix = np.corrcoef(results['flux J/J0 (-)'],models_list_flux[counter](results['time (min)'], a, b))
            corr = corr_matrix[0,1]**2
            r2_flux.append(corr)
            flux_0.append(a)
            parameter1.append(b)       
        elif models_list_flux[counter].__name__ == 'complete_clogging_flux2':
            popt, cir = curve_fit(models_list_flux[counter], results['time (min)'], results['flux J/J0 (-)'], maxfev = 10000, p0=(1))
            b = popt
            flux_fit_series = models_list_flux[counter](fit_time_range, b)
            flux_fit_df = pd.DataFrame(flux_fit_series, columns = [f'fit flux J/J0 (-)'])
            flux_fit_df['Time (min)'] = fit_time_range
            flux_fit.append(flux_fit_df)
            corr_matrix = np.corrcoef(results['flux J/J0 (-)'],models_list_flux[counter](results['time (min)'], b))
            corr = corr_matrix[0,1]**2
            r2_flux.append(corr)
            parameter1.append(b)

    if counter == 0:
       # flux_fit_matrix_J.append(flux_fit)
        parameter_matrix_flux_J = pd.DataFrame(parameter1, columns = [models_list[counter].__name__])
        r_squared_flux_J = pd.DataFrame(r2_flux, columns = [models_list_flux[counter].__name__])  
    else:
       # flux_fit_matrix_J.append(flux_fit)
        parameter_matrix_flux_J[models_list[counter].__name__] = pd.DataFrame(parameter1)    
        r_squared_flux_J[models_list_flux[counter].__name__ ] = pd.DataFrame(r2_flux)  
    fig = plt.figure()
    counter2 = 0
    for results in results_list:
        plot_label = f'{filter_runs[counter2]["Run No."]} {filter_runs[counter2]["Stand ID"]}'
        if models_list_flux[counter].__name__ == 'vmax_standard_flux2' or models_list_flux[counter].__name__ == 'intermediate_filtration_flux2':
            plt.plot(fit_load_range,flux_fit[counter2],label = plot_label)
        else:
            plt.plot(fit_time_range,flux_fit[counter2],label = plot_label)
        counter2 += 1
    if models_list[counter].__name__ == 'combined_intermediate':
        parameter_matrix_flux_J[f'{models_list[counter].__name__}2'] = pd.DataFrame(parameter2)
    if models_list_flux[counter].__name__ == 'vmax_standard_flux2':
        plt.xlabel('Load (L/m²)')
    elif models_list_flux[counter].__name__ == 'intermediate_filtration_flux2':
        plt.xlabel('Volume (mL)')
    else:
        plt.xlabel('Time (min)')
    plt.ylabel('J/J0 (-)')
    plt.title(models_list_flux[counter].__name__)
    plt.xlim(0) 
    plt.ylim(0)
    plt.legend()
    plt.show()
    counter += 1
    
    
            
"""   



#Selection of best model fit for loading
r_squared_sum = r_squared.sum(axis=0)
r_squared_sum = r_squared_sum.sort_values(ascending=False)
best_model_fit = r_squared_sum.index[0]

r_squared_flux_sum = r_squared_flux.sum(axis=0)
r_squared_flux_sum = r_squared_flux_sum.sort_values(ascending=False)
best_model_fit_flux = r_squared_flux_sum.index[0]





#Calculation of filter area

#process time in h
process_time = np.linspace(0,12,num=100)
#batch volume in L
batch_volume = np.linspace(0,2000,num=100)
A_min = [0]*len(delta_flux)
counter = 0
average_flux = [0]*len(delta_flux)

for flux in delta_flux:
    average_flux[counter] = results_list[counter]['flux (LMH)'].mean()
    if flux < 10:
            A_min[counter] = batch_volume/(average_flux[counter]*process_time)
    counter += 1
"""