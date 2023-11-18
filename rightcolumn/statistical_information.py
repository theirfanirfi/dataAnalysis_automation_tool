def display_stats_information(right_column, tk, data):
	container = tk.Frame(right_column, height=300,width=600, bg="white")
	container.grid(row=2, column=1, sticky='w')
	container.configure(bd=1, relief=tk.SOLID, borderwidth=1, highlightbackground="purple")  # Set container border color to purple
