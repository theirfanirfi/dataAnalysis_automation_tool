from tkinter import filedialog
import pandas as pd
from utils import *

def csvButton(i=1, label="Upload CSV Files", tk=None,
    left_column=None, data=None):
    data.set_results([1,2,3])
    # print(results_list)
    button_frame = tk.Frame(left_column, bg="purple", bd=1, relief=tk.SOLID)
    button_frame.grid(row=i, column=0, sticky='w', padx=5, pady=5)
    button = tk.Button(button_frame,
    text=label,
    padx=20, pady=20, wraplength=75,
    command=lambda tk=tk: selectCSVFile(tk, data))  # Make buttons wrap text
    button.grid(row=0, column=0, sticky='w')



def selectCSVFile(tk, data):
    # root = tk.Tk()
    # root.withdraw()  # Hide the main window
    file_paths = filedialog.askopenfilenames(
        title="Select CSV Files",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
    )

    if not file_paths:
        print("No files selected.")
        return None

    print(file_paths)
    read_files(file_paths, tk, data)
    data.update_stat_items(file_paths)

def read_files(filePaths, tk, data):
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

    print(results_list)
    data.set_results(results_list)
    data.set_filter_runs(filter_runs)