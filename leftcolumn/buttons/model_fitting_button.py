from tkinter import filedialog
import pandas as pd
from utils import *
from models.models import * 
from scipy.optimize import *
import matplotlib.pyplot as plt

import numpy as np
from fpdf import FPDF
from datetime import date
from datetime import datetime
from pandas.plotting import table
from scipy.integrate import quad
from sympy.solvers.diophantine.diophantine import diop_solve
from sympy import *
import os

checked_data = []

def model_fitting_button(i=4, label="Fit Models", 
    tk=None, 
    left_column=None, data=None):
    print('results_list ',data.get_results_lists())
    button_frame = tk.Frame(left_column, bg="purple", bd=1, relief=tk.SOLID)
    button_frame.grid(row=i, column=0, sticky='w', padx=5, pady=5)
    button = tk.Button(button_frame,
    text=label,
    padx=20, pady=20, wraplength=200,
    command=lambda tk=tk: fit_models(data))  # Make buttons wrap text
    button.grid(row=0, column=0, sticky='w')

def fit_models(data):
    data.update_stat_items("Models are being fitted......")
    results_list = data.get_results_lists()
    filter_runs = data.get_filter_runs()
    smoothing_factor = data.get_smoothing_factor()
    membrane_area = data.get_membrane_area()
    max_model_value = -1
    max_model_name = ""
    model_value_statistics = list()


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

    def find_max_model(value, name):
        global max_model_Value
        global max_model_name

        # if value > max_model_Value:
        #     max_model_Value = value
        #     max_model_name = name

        model_value_statistics.append({
            "model_name": name,
            "model_value": value,
        })
        return value

    def vmax_standard(time,flux_0,parameter_ks):
        return find_max_model((1/(flux_0*time)+(parameter_ks/2))**(-1),"vmax_standard")

    def vmax_standard_flux(time, flux_0, parameter_ks):
        return find_max_model(-(1/(flux_0*time)+(parameter_ks/2))**(-2)*(1/(flux_0*time))**2,"vmax_standard_flux")

    def cake_filtration(time,flux_0,parameter_kc):
        return find_max_model((1/(parameter_kc*flux_0))*((1+2*parameter_kc*(flux_0)**2*time)**0.5-1),"cake_filtration")

    def cake_filtration_flux(time, flux_0, parameter_kc):
        return find_max_model((1/(1+2*parameter_kc*flux_0**2*time)**0.5)*flux_0,"cake_filtration_flux")

    def intermediate_filtration(time,flux_0,parameter_ki):
        return find_max_model((1/parameter_ki)*np.log10(1+parameter_ki*flux_0*time),"intermediate_filtration")

    def intermediate_filtration_flux(volume,flux_0,parameter_ki):
        return find_max_model(np.exp(-parameter_ki*volume)*flux_0,"intermediate_filtration_flux")

    def complete_clogging(time,flux_0,parameter_kb):
        return find_max_model((flux_0/parameter_kb)*(1-np.exp(-parameter_kb*time)),"complete_clogging")

    def complete_clogging_flux(time,flux_0,parameter_kb):
        return find_max_model((np.exp(-parameter_kb*time)*flux_0),"complete_clogging_flux")

    def combined_intermediate(time, flux_0,parameter_ki, parameter_ka):
        return find_max_model((1/parameter_ki)*np.log10(parameter_ki*flux_0/(5*parameter_ka)*(1-(1-parameter_ka*time)**5)+1), "combined_intermediate")

    def combined_intermediate_flux(VolumeTime, flux_0,parameter_ki, parameter_ka):
        volume, time = VolumeTime
        return find_max_model(((np.exp(-parameter_ki*volume))*((1-parameter_ka*time)**4))*flux_0,"combined_intermediate_flux")
        
    # Derivative functions of the filtration models
    def vmax_standard_derivative(time, flux_0, parameter1):
        return find_max_model(1/(flux_0*time**2*(parameter1/2 + 1/(flux_0*time))**2),"vmax_standard_derivative")

    def cake_filtration_derivative(time, flux_0, parameter1):
        return find_max_model((1.0*flux_0/(2*flux_0**2*parameter1*time + 1)**0.5),"cake_filtration_derivative")

    def intermediate_filtration_derivative(time, flux_0, parameter1):
        return find_max_model(flux_0/(flux_0*parameter1*time + 1), "intermediate_filtration_derivative")

    def complete_clogging_derivative(time, flux_0, parameter1):
        return find_max_model(flux_0*np.exp(-parameter1*time), "complete_clogging_derivative")

    def combined_derivative(time, flux_0, parameter1, parameter2):
        return find_max_model(flux_0*(-parameter2*time + 1)**4/(flux_0*parameter1*(1 - (-parameter2*time + 1)**5)/(5*parameter2) + 1),"combined_derivative")

    def combined_intermediate_flux2(VolumeTime, flux_0,parameter_ki, parameter_ka):
        volume, time = VolumeTime
        x1 = ((np.exp(-parameter_ki*volume))*((1-parameter_ka*time)**4))*flux_0
        x2 = ((np.exp(-parameter_ki*time))*((1-parameter_ka*volume)**4))*flux_0
        x = (x1,x2)
        return find_max_model(x, "combined_intermediate_flux2")

    # Set values of time range for fitting (in min)
    fit_time_range = np.linspace(0,1000,100)
    # Set values of load range for fitting (in mL)
    fit_load_range = np.linspace(0,2000,100)
    
    plt_label = ""

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
        plt.savefig(os.path.join(data.get_project_title(), "plot_label"))
        # plt.show()
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
            # plt.xlabel('Load (L/m²)')
            plt_label = 'Load (L/m²)'
        elif models_list_flux[counter].__name__ == 'intermediate_filtration_flux':
            # plt.xlabel('Volume (mL)')
            plt_label = 'Volume (mL)'
        else:
            # plt.xlabel('Time (min)')
            plt_label = 'Time (min)'
        plt.ylabel('Flux (LMH)')
        plt.xlabel(plt_label)
        plt.title(models_list_flux[counter].__name__)
        plt.xlim(0) 
        plt.ylim(0)
        plt.legend()
        plt_label = "flux_mode_"+plt_label.replace(" ","").replace("/","")
        plt.savefig(os.path.join(data.get_project_title(), plt_label))
        # plt.show()
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
        plt_label = ""
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
            plt_label = 'Load (L/m²)'
            # plt.xlabel('Load (L/m²)')
        elif models_list_flux[counter].__name__ == 'intermediate_filtration_flux2':
            # plt.xlabel('Volume (mL)')
            plt_label = 'Volume (mL)'
        else:
            # plt.xlabel('Time (min)')
            plt_label = 'Time (min)'
        plt.ylabel('J/J0 (-)')
        plt.xlabel(plt_label)
        plt.title(models_list_flux[counter].__name__)
        plt.xlim(0) 
        plt.ylim(0)
        plt.legend()
        # plt.show()
        plt_label = "flux_mode_JJ0_"+plt_label.replace(" ","").replace("/","")
        plt.savefig(os.path.join(data.get_project_title(), plt_label))
        counter += 1

    # Selection of best model fit for loading
    r_squared_sum = r_squared.sum(axis=0)
    r_squared_sum = r_squared_sum.sort_values(ascending=False)
    best_model_fit = r_squared_sum.index[0]

    r_squared_flux_sum = r_squared_flux.sum(axis=0)
    r_squared_flux_sum = r_squared_flux_sum.sort_values(ascending=False)
    best_model_fit_flux = r_squared_flux_sum.index[0]
    best_text = "\nBest model fit for loading\n"
    best_text += "Rsquared Sum\n"
    best_text += str(r_squared_sum)
    best_text += "\nRsquared Sum Best model fit\n"
    best_text += "\n"+str(best_model_fit)

    best_text += "\nRsquared Sum Flux\n"
    best_text += '\n\n '+str(r_squared_flux_sum)
    best_text += "\nbest model fit flux\n"
    best_text += '\n\n '+str(best_model_fit_flux)
    # print('best_details ')
    # print('r_squared_sum',r_squared_sum)
    # print('best_model_fit', best_model_fit[0])
    # print('r_squared_flux_sum', r_squared_flux_sum)
    # print("best_model_fit_flux", best_model_fit_flux[0])

    data.enable_last_batch_of_images()
    print('enabled')
    data.update_stat_items("Models fitted.\nPlease click in the model view section.\nReport Generation Enabled.")
    data.set_statistical_model_values(model_value_statistics)
    data.update_stat_textarea_items(best_text, model_value_statistics)
    data.enable_report_generation()
    # print(model_value_statistics)
    # print("max: ",max_model_name, max_model_name)