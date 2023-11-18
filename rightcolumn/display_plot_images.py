from PIL import Image, ImageTk

# Define a list of image file names
image_files = ["flux.png", "flux_vs_load.png", "J_vs_load.png", "loading.png"]
current_image_index = 0
image_label = False


def display_plots(right_column, tk, data):
	global current_image_index
	current_image_index = data.get_current_image_index()
	def on_image_click(event):
		global current_image_index
		if data.first_batch_of_images or data.second_batch_of_images:
			current_image_index += 1
			data.set_current_image_index(current_image_index)
			update_image()
			print('image ', data.get_current_image_index())

	container = tk.Frame(right_column, height=300, width=600, bg="white")
	container.grid(row=3, column=1, sticky='nsew')
	container.configure(bd=1, relief=tk.SOLID, borderwidth=1,
						highlightbackground="purple")  # Set container border color to purple
	container.bind("<Button-1>", on_image_click)
	data.setImagesContainer(container)



    # Function to update the displayed image


	def update_image():
		global current_image_index
		global image_label
		print('update is called ',len(data.get_images()))
		if current_image_index < 0:
			current_image_index = len(data.get_images()) - 1
		elif current_image_index >= len(data.get_images()):
			current_image_index = 0

		data.set_current_image_index(current_image_index)

		# image = Image.open(image_files[current_image_index])
		# photo = ImageTk.PhotoImage(image)
		# image_label.config(image=photo)
		# image_label.image = photo

		if image_label:
			image_label.destroy()
		image = Image.open(data.get_project_title()+"/"+data.get_images()[data.get_current_image_index()])
		image = image.resize((600, 300))
		photo = ImageTk.PhotoImage(image)
		image_label = tk.Label(container, image=photo)
		image_label.photo = photo
		image_label.config(width=600, height=300)
		image_label.bind("<Button-1>", on_image_click)
		image_label.pack()



# def update_image(container, tk, data):
# 	current_image_index = data.get_current_image_index()
# 	def on_image_click(event):
# 		global current_image_index
# 		print(current_image_index)
# 		if data.first_batch_of_images or data.second_batch_of_images:
# 			current_image_index += 1
# 			update_image(container, tk, data)
#
# 	global current_image_index
# 	global image_label
# 	print('update is called')
# 	if current_image_index < 0:
# 		current_image_index = len(data.get_images()) - 1
# 	elif current_image_index >= len(data.get_images()):
# 		current_image_index = 0
#
# 	# image = Image.open(image_files[current_image_index])
# 	# photo = ImageTk.PhotoImage(image)
# 	# image_label.config(image=photo)
# 	# image_label.image = photo
#
# 	if image_label:
# 		image_label.destroy()
# 	image = Image.open(data.get_project_title()+"/"+data.get_images()[current_image_index])
# 	image = image.resize((300, 200))
# 	photo = ImageTk.PhotoImage(image)
# 	image_label = tk.Label(container, image=photo)
# 	image_label.photo = photo
# 	image_label.config(width=300, height=200)
# 	image_label.bind("<Button-1>", on_image_click)
# 	image_label.pack()