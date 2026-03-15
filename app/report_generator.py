from fpdf import FPDF

def generate_pdf_report(metrics, filename="nutrition_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial","B",16)
    pdf.cell(0,10,"Personalized Nutrition & Lifestyle Report",0,1,"C")
    pdf.set_font("Arial","",12)
    for k,v in metrics.items():
        pdf.multi_cell(0,8,f"{k}: {v}")
    pdf.output(filename)
    return filename