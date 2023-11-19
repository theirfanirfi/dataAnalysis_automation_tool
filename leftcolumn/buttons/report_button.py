from tkinter import filedialog

from fpdf import FPDF
import pandas as pd
from utils import *

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
# from docx import Document
# from docx.shared import Inches

def reportButton(i=1, label="Generate Report", tk=None, left_column=None, data=None):
    # print(results_list)
    button_frame = tk.Frame(left_column, bg="purple", bd=1, relief=tk.SOLID)
    button_frame.grid(row=i, column=0, sticky='w', padx=5, pady=5)
    button = tk.Button(button_frame,
    text=label,
    padx=20, pady=20, wraplength=200,
    command=lambda tk=tk: generateReport(tk, data))  # Make buttons wrap text
    button.grid(row=0, column=0, sticky='w')



def generateReport(tk, data):
    if not data.generate_report:
        data.update_stat_items("\nReport generation is not enabled.")
        return

    multi_text = "\n Smoothing Factor: "+str(data.get_smoothing_factor())
    multi_text += "\n Membrane Area: "+str(data.get_membrane_area())+"\n"
    multi_text += str(data.get_results_lists())

    pdf = FPDF()
    pdf.add_page()

    # Set font
    pdf.set_font("Arial", size=12)

    # Add text to the PDF
    pdf.multi_cell(0, 10, multi_text)

    # Add images to the PDF
    for image in [data.get_project_title()+"/flux.png",
                       data.get_project_title()+"/flux_vs_load.png",
                       data.get_project_title()+"/J_vs_load.png",
                       data.get_project_title()+"/loading.png"]:
        pdf.ln(10)  # add a newline before each image
        pdf.image(image, x=pdf.get_x(), w=pdf.w-20)

    pdf.multi_cell(0, 10,"\nModel fits\n")
    pdf.multi_cell(0, 10,data.get_statistical_model_values())
    # Save the PDF to the specified file

    # Add images to the PDF
    for image in [data.get_project_title()+"/plot_label.png",
                       data.get_project_title()+"/flux_mode_JJ0_Load(Lm²).png",
                       data.get_project_title()+"/flux_mode_JJ0_Time(min).png",
                       data.get_project_title()+"/flux_mode_JJ0_Volume(mL).png",
                       data.get_project_title()+"/flux_mode_Load(Lm²).png",
                       data.get_project_title()+"/flux_mode_Time(min).png",
                       data.get_project_title()+"/flux_mode_Volume(mL).png",
                       data.get_project_title()+"/flux.png",
                       data.get_project_title()+"/flux_vs_load.png",
                       data.get_project_title()+"/J_vs_load.png",
                       data.get_project_title()+"/loading.png"]:
        pdf.ln(10)  # add a newline before each image
        pdf.image(image, x=pdf.get_x(), w=pdf.w-20)
    pdf.output(data.get_project_title()+"/"+data.get_project_title()+".pdf")
    print('done')


