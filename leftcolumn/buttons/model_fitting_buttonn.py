from tkinter import filedialog
import pandas as pd
from utils import *
from models.models import * 
from scipy.optimize import *
import matplotlib.pyplot as plt

checked_data = []

def model_fitting_button(i=4, label="Fit Models", 
    tk=None, 
    left_column=None, data=None):
    print('results_list ',data.get_results_lists())
    button_frame = tk.Frame(left_column, bg="purple", bd=1, relief=tk.SOLID)
    button_frame.grid(row=i, column=0, sticky='w', padx=5, pady=5)
    button = tk.Button(button_frame,
    text=label,
    padx=20, pady=20, wraplength=75,
    command=lambda tk=tk: fit_models(data))  # Make buttons wrap text
    button.grid(row=0, column=0, sticky='w')

def fit_models(data):
    results_list = data.get_results_lists()
    filter_runs = data.get_filter_runs()
    smoothing_factor = data.get_smoothing_factor()
    membrane_area = data.get_membrane_area()
    data.enable_last_batch_of_images()
    print('enabled')


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
        # plt.show()
        plt.savefig('load_mode.png')
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
        # plt.show()
        plt.savefig('flux_mode.png')
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
            print(Vmax)
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
            complete_integral = quad(complete_clogging_flux, 0, 
                Vmax_flux[model.__name__][counter], 
                args= (flux_initial_flux[model.__name__][counter],
                    parameter_matrix_flux[model.__name__][counter]))
            integral.append(complete_integral)
            counter += 1
        if counter2 == 0:
            Integrals_Models = pd.DataFrame(integral, columns=[model.__name__,f'{model.__name__} error'])
        else:
            Integrals_Models_intermediate = pd.DataFrame(integral, columns=[model.__name__,f'{model.__name__} error'])
            Integrals_Models[model.__name__] = Integrals_Models_intermediate[model.__name__]
            Integrals_Models[f'{model.__name__} error'] = Integrals_Models_intermediate[f'{model.__name__} error']
        counter2 += 1


  

 