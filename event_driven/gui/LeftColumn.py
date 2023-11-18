class LeftColumn:
    def __init__(self, tk, app, data, rightColumn):
        
        self.rightColumn = rightColumn
        self.tk = tk
        self.app = app
        self.data = data
        self.leftColumn = self.defineLeftColumn()
        
        self.csv_button = self.init_csv_button()
        self.check_data_quality_button = None
        self.plot_button = None
        self.fit_models_button = None
        self.generate_report_button = None
        
    
    def defineLeftColumn(self):
        self.leftColumn = self.tk.Frame(self.app, bg="lightblue")
        self.leftColumn.grid(row=0, column=0, rowspan=3, sticky='ns')  # Align to the left
    
    def init_csv_button(self):
            button_frame = self.tk.Frame(self.leftColumn, bg="purple", bd=1, relief=self.tk.SOLID)
            button_frame.grid(row=0, column=0, sticky='w', padx=5, pady=5)
            button = self.tk.Button(button_frame,
            text="Select CSV",
            padx=20, pady=20, wraplength=75)
            # command=lambda tk=self.tk: selectCSVFile(self.tk, self.data))  # Make buttons wrap text
            button.grid(row=0, column=0, sticky='w')
            # button.pack()