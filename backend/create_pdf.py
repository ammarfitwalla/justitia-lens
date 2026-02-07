"""Quick script to generate PDF report for protest case."""
from fpdf import FPDF

# Read the text file
with open("data/cases/20/reports/incident_report_25-7718.txt", "r") as f:
    content = f.read()

# Create PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Courier", size=9)

for line in content.split('\n'):
    pdf.cell(0, 4, txt=line, ln=True)

pdf.output("data/cases/20/reports/incident_report_25-7718.pdf")
print("PDF created successfully!")
