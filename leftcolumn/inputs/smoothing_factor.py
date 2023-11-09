def smoothingFactor(tk, sub_container, data):
	def on_text_change(event):
		if event.keycode==855638143 and entry.get() == "":
			return
		print('input',entry.get())
		print('working ', event)
		data.set_smoothing_factor(int(entry.get()))
	
	label_frame = tk.Frame(sub_container, 
    	bg="purple", 
    	bd=1, 
    	relief=tk.SOLID)

	label_frame.grid(row=1, 
    	column=0, 
    	sticky='w', 
    	padx=5, pady=5)

	tk.Label(label_frame, 
    	text="Smoothing Factor").grid(row=0, column=0, sticky='w')
	entry = tk.Entry(sub_container)
	entry.bind("<KeyRelease>", on_text_change)
	entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')
	entry.configure(bd=0)

