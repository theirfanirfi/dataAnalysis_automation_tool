import tkinter as tk
from datastore.Data import Data
from gui.LeftColumn import LeftColumn
from gui.RightColumn import RightColumn
class App:
    def __init__(self, tk, app, data):
        self.data = data
        self.right = RightColumn(tk, app, data)
        self.left = LeftColumn(tk, app, data, self.right)
        
    
    
    def update(self):
        pass
    



def main():
    root = tk.Tk()
    root.title("Data Analysis Automation Tool")
    # Create the main frame
    main_frame = tk.Frame(root, bg="white")  # Set the background color to white
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Create the left main column (column 0) with a fixed width of 600 pixels
    main_frame.grid_columnconfigure(0, minsize=600)
    data = Data()
    app = App(tk, main_frame, data)
    
    root.mainloop()


if __name__ == "__main__":
    main()