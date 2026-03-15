import os
import sys
import streamlit as st
from fpdf import FPDF
from io import BytesIO

# Ensure parent folder is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.nutrition_agent import nutrition_agent
from agents.lifestyle_agent import lifestyle_agent
from agents.action_plan_agent import action_plan_agent

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="Personalized Health Planner", layout="wide")

# -------------------------------
# Full-width Centered Title
# -------------------------------
st.markdown(
    """
    <div style="text-align:center; width:100%; margin:auto;">
        <h1>Personalized Nutrition & Lifestyle Planner</h1>
        <p>Enter your personal details to generate a health plan</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")  # spacing

# -------------------------------
# Input and Logs Section
# -------------------------------
col_inputs, col_logs = st.columns([2, 1])  # left: inputs, right: logs

# -------------------------------
# Logs container with improved styling
# -------------------------------
with col_logs:
    log_container = st.empty()

# Initialize log list at the start so box is always visible
cot_log = []

def update_logs(log_list):
    """Display structured color-coded logs with border, white background, bold labels, and concise errors."""
    html = '<div style="border:1px solid #ccc; padding:10px; background-color:white; height:600px; overflow-y:auto;">'
    
    # Title for the log box
    html += '<h3 style="margin-top:0; margin-bottom:10px; text-align:center;">Activity Logs</h3>'
    
    color_map = {"INFO": "#1f77b4", "SUCCESS": "#2ca02c", "WARNING": "#ff9800", "ERROR": "#d62728"}
    for log in log_list:
        if isinstance(log, dict):
            level = log.get("level", "INFO")
            msg = log.get("msg", "")
        else:
            level = "INFO"
            msg = str(log)

        # If it's an error or exception, summarize it
        if level == "ERROR":
            if isinstance(msg, Exception):
                msg = str(msg)
            msg = str(msg).splitlines()[0]

        color = color_map.get(level, "#000000")
        html += f'<div style="color:{color}; margin-bottom:4px;"><b>[{level}]</b> {msg}</div>'
    html += "</div>"
    
    log_container.markdown(html, unsafe_allow_html=True)

# -------------------------------
# Initialize log list at the start
# -------------------------------
cot_log = []

# Add initial entry
cot_log.append({"level": "INFO", "msg": "User entered the page."})

# Display the log box immediately
update_logs(cot_log)
# -------------------------------
# Logging helpers
# -------------------------------
def log_info(msg):
    cot_log.append({"level": "INFO", "msg": msg})
    update_logs(cot_log)

def log_success(msg):
    cot_log.append({"level": "SUCCESS", "msg": msg})
    update_logs(cot_log)

def log_warning(msg):
    cot_log.append({"level": "WARNING", "msg": msg})
    update_logs(cot_log)

def log_error(msg):
    if isinstance(msg, Exception):
        msg = str(msg).splitlines()[0]
    cot_log.append({"level": "ERROR", "msg": msg})
    update_logs(cot_log)

# -------------------------------
# User Inputs
# -------------------------------
with col_inputs:
    age = st.number_input("Age (years)", min_value=0, max_value=120, value=30)
    weight_kg = st.number_input("Weight (kg)", min_value=1, max_value=500, value=70)
    height_cm = st.number_input("Height (cm)", min_value=30, max_value=250, value=170)
    occupation = st.text_input("Occupation", value="")
    activity_level = st.selectbox("Activity Level", ["low", "moderate", "high"])

    can_generate = bool(occupation.strip())
    if not can_generate:
        st.warning("Please enter your occupation to enable report generation.")

# -------------------------------
# Generate Health Plan Button
# -------------------------------
with col_inputs:
    if st.button("Generate Health Plan") and can_generate:

        # Logging helpers
        def log_info(msg):
            cot_log.append({"level": "INFO", "msg": msg})
            update_logs(cot_log)

        def log_success(msg):
            cot_log.append({"level": "SUCCESS", "msg": msg})
            update_logs(cot_log)

        def log_warning(msg):
            cot_log.append({"level": "WARNING", "msg": msg})
            update_logs(cot_log)

        def log_error(msg):
            cot_log.append({"level": "ERROR", "msg": msg})
            update_logs(cot_log)

        metrics = {
            "age": age,
            "weight_kg": weight_kg,
            "height_cm": height_cm,
            "occupation": occupation,
            "activity_level": activity_level
        }

        # Run agents
        try:
            log_info("Running Nutrition Agent...")
            nutrition_output = nutrition_agent(metrics, cot_log)
            log_success("Nutrition Agent completed.")

            log_info("Running Lifestyle Agent...")
            lifestyle_output = lifestyle_agent(metrics, cot_log)
            log_success("Lifestyle Agent completed.")

            log_info("Generating SMART Action Plan...")
            action_plan_output = action_plan_agent(nutrition_output, lifestyle_output, cot_log)
            log_success("SMART Action Plan generated.")

        except Exception as e:
            log_error(f"Error during agent execution: {e}")

        # -------------------------------
        # Generate PDF Report
        # -------------------------------
        def generate_pdf_report(metrics, nutrition_output, lifestyle_output, action_plan_output):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Personalized Nutrition & Lifestyle Report", 0, 1, "C")

            # User Metrics
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "User Metrics", 0, 1)
            pdf.set_font("Arial", "", 12)
            for k, v in metrics.items():
                pdf.multi_cell(0, 8, f"{k}: {v}")

            pdf.ln(5)
            # Nutrition Plan
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Nutrition Plan", 0, 1)
            pdf.set_font("Arial", "", 12)
            for meal, data in nutrition_output.items():
                if isinstance(data, dict):
                    name = data.get("name", "")
                    energy = data.get("energy_kcal", "")
                    proteins = data.get("proteins_g", "")
                    carbs = data.get("carbs_g", "")
                    fat = data.get("fat_g", "")
                    pdf.multi_cell(0, 8, f"{meal.capitalize()}: {name}")
                    pdf.multi_cell(0, 8, f"   Energy (kcal): {energy}")
                    pdf.multi_cell(0, 8, f"   Proteins (g): {proteins}")
                    pdf.multi_cell(0, 8, f"   Carbs (g): {carbs}")
                    pdf.multi_cell(0, 8, f"   Fat (g): {fat}")
                else:
                    pdf.multi_cell(0, 8, f"{meal.capitalize()}: {data}")

            pdf.ln(5)
            # Lifestyle Plan
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Lifestyle Plan", 0, 1)
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 8, f"Exercise: {', '.join(lifestyle_output.get('exercise', []))}")
            pdf.multi_cell(0, 8, f"Hydration (Liters): {lifestyle_output.get('hydration_liters','')}")

            pdf.ln(5)
            # SMART Action Plan
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "SMART Action Plan", 0, 1)
            pdf.set_font("Arial", "", 12)
            for idx, obj in enumerate(action_plan_output.get("SMART_Objectives", []), 1):
                # Normalize to dict
                if isinstance(obj, dict):
                    goal = obj.get("goal", "")
                    specific = obj.get("specific", "")
                    measurable = obj.get("measurable", "")
                    achievable = obj.get("achievable", "")
                    relevant = obj.get("relevant", "")
                    time_bound = obj.get("time_bound", "")
                else:
                    # if string, treat as goal
                    goal = str(obj)
                    specific = measurable = achievable = relevant = time_bound = ""
                pdf.multi_cell(0, 8, f"{idx}. Goal: {goal}")
                pdf.multi_cell(0, 8, f"   Specific: {specific}")
                pdf.multi_cell(0, 8, f"   Measurable: {measurable}")
                pdf.multi_cell(0, 8, f"   Achievable: {achievable}")
                pdf.multi_cell(0, 8, f"   Relevant: {relevant}")
                pdf.multi_cell(0, 8, f"   Time-bound: {time_bound}")
                pdf.ln(2)

            pdf_output = pdf.output(dest='S').encode('latin1')
            pdf_bytes = BytesIO(pdf_output)
            pdf_bytes.seek(0)
            return pdf_bytes

        pdf_bytes = generate_pdf_report(metrics, nutrition_output, lifestyle_output, action_plan_output)
        log_success("PDF Report Generated Successfully")

        # Download button only
        st.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name="health_report.pdf",
            mime="application/pdf"
        )
