from PIL import Image, ImageTk

# Define a list of image file names
image_files = ["flux.png", "flux_vs_load.png", "J_vs_load.png", "loading.png"]
current_image_index = 0
image_label = False

def display_plots(right_column, tk, data):
	container = tk.Frame(right_column, height=200,width=300, bg="white")
	container.grid(row=3, column=1, sticky='nsew', padx=5, pady=5)
	container.configure(bd=1, relief=tk.SOLID, borderwidth=1, highlightbackground="purple")  # Set container border color to purple

	def on_image_click(event):
		global current_image_index
		# current_image_index+1
		# if current_image_index-1 <0:
		# 	current_image_index = 0
		# elif current_image_index+1 >= len(image_files)-1:
		# 	current_image_index = 0
		# else:
		# 	current_image_index +=1
		current_image_index+=1
		print(current_image_index)
		update_image()

	# Function to update the displayed image
	def update_image():
	    global current_image_index
	    global image_label
	    print('update is called')

	    if current_image_index < 0:
	        current_image_index = len(image_files) - 1
	    elif current_image_index >= len(image_files):
	        current_image_index = 0

	    # image = Image.open(image_files[current_image_index])
	    # photo = ImageTk.PhotoImage(image)
	    # image_label.config(image=photo)
	    # image_label.image = photo

	    if image_label:
	    	image_label.destroy()
	    image = Image.open(image_files[current_image_index])
	    image = image.resize((300, 200))
	    photo = ImageTk.PhotoImage(image)
	    image_label = tk.Label(container, image=photo)
	    image_label.photo = photo
	    image_label.config(width=300, height=200)
	    image_label.bind("<Button-1>", on_image_click)
	    image_label.pack()

	update_image()
