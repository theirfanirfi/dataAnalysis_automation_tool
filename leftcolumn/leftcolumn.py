from leftcolumn.buttons.csv_button import csvButton
def leftColumn(tk, main_frame):
    left_column = tk.Frame(main_frame, bg="lightblue")
    left_column.grid(row=0, column=0, rowspan=3, sticky='ns')  # Align to the left

    #buttons

    csvButton(i=1, label="CSV", tk=tk, left_column=left_column)

    # Create the sub-container in the left column
    sub_container = tk.Frame(left_column, bg="lightgreen")
    sub_container.grid(row=5, column=0, sticky='ew')

    # Create the first sub-column in the sub-container
    input_labels = ['Input 1:', 'Input 2:', 'Input 3:']
    for i, label in enumerate(input_labels):
        label_frame = tk.Frame(sub_container, bg="purple", bd=1, relief=tk.SOLID)
        label_frame.grid(row=i, column=0, sticky='w', padx=5, pady=5)
        tk.Label(label_frame, text=label).grid(row=0, column=0, sticky='w')
        entry = tk.Entry(sub_container)
        entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')
        entry.configure(bd=0)  # Remove the entry's border to avoid duplication

    # Create the second sub-column in the sub-container
    text_labels = ['Label 1:', 'Label 2:', 'Label 3:']
    for i, label in enumerate(text_labels):
        label_frame = tk.Frame(sub_container, bg="purple", bd=1, relief=tk.SOLID)
        label_frame.grid(row=i, column=2, padx=5, pady=5, sticky='w')
        tk.Label(label_frame, text=label).grid(row=0, column=0, sticky='w')
