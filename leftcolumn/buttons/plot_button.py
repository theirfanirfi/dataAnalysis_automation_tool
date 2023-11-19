from tkinter import filedialog
import pandas as pd
from utils import *
import matplotlib.pyplot as plt
import os

checked_data = []

def plot_button(i=3, label="Plot Data", 
    tk=None, 
    left_column=None, data=None):
    button_frame = tk.Frame(left_column, bg="purple", bd=1, relief=tk.SOLID)
    button_frame.grid(row=i, column=0, sticky='w', padx=5, pady=5)
    button = tk.Button(button_frame,
    text=label,
    padx=20, pady=20, wraplength=200,
    command=lambda tk=tk: plot_data(data))  # Make buttons wrap text
    button.grid(row=0, column=0, sticky='w')

def plot_data(data):
    #Check data quality
    results_list = data.get_results_lists()
    filter_runs = data.get_filter_runs()
    smoothing_factor = data.get_smoothing_factor()
    membrane_area = data.get_membrane_area()
    
    if not create_project_directory(data):
        return
    data.update_stat_items("Data is being plotted.........")
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
            plt.savefig(os.path.join(data.get_project_title(), save_file), dpi=400)

    plot_results('time (min)', 'load (L/m²)', 'Time (min)', 'Load (L/m²)', 'loading.png')
    plot_results('time (min)', 'flux (LMH)', 'Time (min)', 'Flux (LMH)', 'flux.png')
    plot_results('load (L/m²)', 'flux (LMH)', 'Load (L/m²)', 'Flux (LMH)', 'flux_vs_load.png')
    plot_results('load (L/m²)', 'flux J/J0 (-)', 'Load (L/m²)', 'J/J0 (-)', 'J_vs_load.png')

    data.enable_first_batch_of_images()
    data.update_stat_items("Data Plotted.")

def create_project_directory(data):
    try:
        os.system('mkdir '+data.get_project_title())
        data.write_the_project_directory()
        return True
    except Exception as e:
        return False