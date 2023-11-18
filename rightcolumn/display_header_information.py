def display_header_information(right_column, tk, data):
	container = tk.Frame(right_column, height=300,width=600, bg="white")
	container.grid(row=1, column=1, sticky='wn')
	container.configure(bd=1, relief=tk.SOLID, borderwidth=1, highlightbackground="purple")  # Set container border color to purple
	text_area = tk.Text(container, height=10, width=84)
	text_area.grid(sticky='w')
	text_area.pack()
	data.set_stats_item(text_area)
