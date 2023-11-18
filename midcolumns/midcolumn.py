
def midColumn(tk, main_frame, data):
    # Create the right main column (column 1)
    mid_column = tk.Frame(main_frame, bg="lightgray",
                            highlightbackground="purple",
                            highlightcolor="purple", highlightthickness=1)
    mid_column.grid(row=1, column=1, rowspan=5, sticky='wn')  # Align to the left

    # Create three containers with a height of 200px in the right column
    # for i in range(1):
    container = tk.Frame(mid_column, height=400, width=400, bg="white")
    container.grid(row=0, sticky='wn', padx=5, pady=5)
    container.configure(bd=1, relief=tk.SOLID, borderwidth=1, highlightbackground="purple")  # Set container border color to purple