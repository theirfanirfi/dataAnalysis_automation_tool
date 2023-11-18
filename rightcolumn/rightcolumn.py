from rightcolumn.display_header_information import display_header_information
from rightcolumn.statistical_information import display_stats_information
from rightcolumn.display_plot_images import display_plots

def rightColumn(tk, main_frame, data):
    # Create the right main column (column 1)
    right_column = tk.Frame(main_frame,
                            bg="lightgray",
                            highlightbackground="purple",
                            highlightcolor="purple",
                            highlightthickness=1)
    right_column.grid(row=0, column=2, rowspan=3, columnspan=2, sticky='wn')  # Align to the left

    # Create three containers with a height of 200px in the right column

    display_header_information(right_column, tk, data)
    display_stats_information(right_column, tk, data)
    display_plots(right_column, tk, data)
    # Create a StringVar to store and update the display
    #display = tk.StringVar()

    data.setRightColumn(right_column)