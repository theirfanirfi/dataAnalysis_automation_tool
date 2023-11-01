
def rightColumn(tk, main_frame):
    # Create the right main column (column 1)
    right_column = tk.Frame(main_frame, bg="lightgray", highlightbackground="purple", highlightcolor="purple", highlightthickness=1)
    right_column.grid(row=0, column=1, rowspan=3, sticky='nsew')  # Align to the left

    # Create three containers with a height of 200px in the right column
    for i in range(3):
        container = tk.Frame(right_column, height=200, bg="white")
        container.grid(row=i, column=0, sticky='nsew', padx=5, pady=5)
        container.configure(bd=1, relief=tk.SOLID, borderwidth=1, highlightbackground="purple")  # Set container border color to purple

    # Create a StringVar to store and update the display
    display = tk.StringVar()