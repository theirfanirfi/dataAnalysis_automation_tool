def membrane_area(tk, sub_container, data):
	def on_text_change(event):
		if event.keycode==855638143 and entry.get() == "":
			return
		print('input',entry.get())
		print('working ', event)
		print('smoothing_factor', data.get_smoothing_factor())
		data.set_membrane_area(float(entry.get())/10000)
		data.update_stat_items("Membrane area now is: " + str(int(entry.get())/10000))
	
	label_frame = tk.Frame(sub_container, 
    	bg="purple", 
    	bd=1, 
    	relief=tk.SOLID)

	label_frame.grid(row=2, 
    	column=0, 
    	sticky='w', 
    	padx=5, pady=5)

	tk.Label(label_frame, 
    	text="Membrane Area").grid(row=2, column=0, sticky='w')
	entry = tk.Entry(sub_container)
	entry.bind("<KeyRelease>", on_text_change)
	entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')
	entry.configure(bd=0)

