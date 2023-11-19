from leftcolumn.buttons.csv_button import csvButton
from leftcolumn.buttons.check_input_button import checkButton
from leftcolumn.buttons.plot_button import plot_button
from leftcolumn.buttons.model_fitting_button import model_fitting_button
from leftcolumn.inputs.smoothing_factor import smoothingFactor
from leftcolumn.inputs.membrane_area import membrane_area
from leftcolumn.buttons.report_button import reportButton

filter_runs = {}
results_list = [1]

def leftColumn(tk, main_frame, data):
    left_column = tk.Frame(main_frame, bg="lightblue")
    left_column.grid(row=0, column=0, rowspan=3, sticky='wn')  # Align to the left

    #buttons

    csvButton(i=1, label="CSV", tk=tk, left_column=left_column, data=data)
    checkButton(i=2, label="Check Input Data", tk=tk, left_column=left_column, data=data)
    plot_button(i=3, label="Plot Data", tk=tk, left_column=left_column, data=data)
    model_fitting_button(i=4, label="Fit Models", tk=tk, left_column=left_column, data=data)
    reportButton(i=5, label="Generate Report", tk=tk, left_column=left_column, data=data)

    # Create the sub-container in the left column
    sub_container = tk.Frame(left_column, bg="lightgreen")
    sub_container.grid(row=6, column=0, columnspan=2, sticky='w')

    # Create the first sub-column in the sub-container
    smoothingFactor(tk, sub_container, data)
    membrane_area(tk, sub_container, data)

    # Create the second sub-column in the sub-container
    text_labels = ['Label 1:', 'Label 2:', 'Label 3:']
    for i, label in enumerate(text_labels):
        label_frame = tk.Frame(sub_container, bg="purple", bd=1, relief=tk.SOLID)
        label_frame.grid(row=i, column=2, padx=5, pady=5, sticky='w')
        tk.Label(label_frame, text=label).grid(row=5, column=1,  sticky='w')

    data.setLeftColumn(left_column)
