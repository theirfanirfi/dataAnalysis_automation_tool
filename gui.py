import tkinter as tk
from leftcolumn.leftcolumn import leftColumn
from midcolumns.midcolumn import midColumn
from rightcolumn.rightcolumn import rightColumn
from utils import Data

# Function to update the display
def update_display(value):
    current_text = display.get()
    display.set(current_text + value)

# Function to calculate and update the result
def calculate():
    try:
        result = eval(display.get())
        display.set(str(result))
    except Exception as e:
        display.set("Error")

# Create the main application window
app = tk.Tk()
app.title("Left-Aligned Split Frame Example")

# Create the main frame
main_frame = tk.Frame(app, bg="white")  # Set the background color to white
main_frame.pack(fill=tk.BOTH, expand=True)

# Create the left main column (column 0) with a fixed width of 600 pixels
main_frame.grid_columnconfigure(0, minsize=300)
# main_frame.grid_columnconfigure(1, minsize=400)
main_frame.grid_columnconfigure(2, minsize=600)

data = Data(main_frame)
# left column
leftColumn(tk, main_frame, data)
# midColumn(tk, main_frame, data)

#right column
rightColumn(tk, main_frame, data)


# Start the main loop
app.mainloop()
