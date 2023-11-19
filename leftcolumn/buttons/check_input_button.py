from tkinter import filedialog
import pandas as pd
import numpy as np
from utils import *

checked_data = []

def checkButton(i=2, label="Check Input Data", 
    tk=None, 
    left_column=None, data=None):
    print('results_list ',data.get_results_lists())
    button_frame = tk.Frame(left_column, bg="purple", bd=1, relief=tk.SOLID)
    button_frame.grid(row=i, column=0, sticky='w', padx=5, pady=5)
    button = tk.Button(button_frame,
    text=label,
    padx=20, pady=20, wraplength=200,
    command=lambda tk=tk: checkInputData(data))  # Make buttons wrap text
    button.grid(row=0, column=0, sticky='w')

def checkInputData(data):
    #Check data quality
    results_list = data.get_results_lists()
    smoothing_factor = data.get_smoothing_factor()
    membrane_area = data.get_membrane_area()
    text_stats = "Checking data quality\n"
    text_stats += "\nSmoothing factor: " + str(smoothing_factor)
    text_stats += "\nMembrane area: " + str(membrane_area)
    
    print(smoothing_factor, membrane_area)
    # return 

    # calculation of flux and inclusion into results_list
    # initialize count for next loop
    count_2 = 0
    for results in results_list:
        if len(results) < smoothing_factor*2:
            print('Please reduce smoothing factor. Data points not sufficient.')
            text_stats += "Please reduce smoothing factor. Data points not sufficient."
            
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

    # print(results_list)
    #drop out rows where flux is NaN
    for i, results in enumerate(results_list):
        # print('i',results[np.isnan(results['flux (LMH)'])==False])
        results = results[np.isnan(results['flux (LMH)']) == False]
        results['vol (L)'] = results['vol (mL)']/1000
        results_list[i] = results

    #insert loading in L/m²
    for i, results in enumerate(results_list):
        results['load (L/m²)'] = results['vol (mL)']/1000/membrane_area
        results_list[i] = results

    data.set_results(results_list)
    text_stats += "\n"
    text_stats += str(results_list)
    data.update_stat_items(text_stats)
