import os
from dotenv import load_dotenv
from tools.armour_tool import check_safe_prompt
from tools.health_tools import *
from agents.nutrition_agent import nutrition_agent
from agents.lifestyle_agent import lifestyle_agent
from agents.action_plan_agent import action_plan_agent
from app.report_generator import generate_pdf_report

load_dotenv()

def run_pipeline(user_input):
    cot_log = []

    # 1. Armour safeguard
    if not check_safe_prompt(user_input.get("query","")):
        return {"error":"Unsafe input blocked by Armour."}
    cot_log.append("Armour safeguard passed.")

    # 2. Validate inputs
    required_fields = ["weight_kg","height_m","waist_cm","hip_cm","age","sex","activity_level","occupation"]
    missing = [f for f in required_fields if f not in user_input or user_input[f] in [None,""]]
    if missing:
        cot_log.append(f"Missing fields: {missing}. Returning general plan.")
        return {"general_plan":"Balanced diet + light exercise + hydration","CoT_Log":cot_log}

    # 3. Local metric calculation
    weight = user_input["weight_kg"]
    height = user_input["height_m"]
    waist = user_input["waist_cm"]
    hip = user_input["hip_cm"]
    age = user_input["age"]
    sex = user_input["sex"]

    bmi = calculate_bmi(weight,height)
    category = bmi_category(bmi)
    whr = waist_to_hip_ratio(waist,hip)
    risks = health_risk(bmi,whr)
    bmr = calculate_bmr(weight,height*100,age,sex)
    cot_log.append("Metrics calculated.")

    metrics = {"weight_kg":weight,"height_m":height,"bmi":bmi,"category":category,
               "whr":whr,"risks":risks,"bmr":bmr,"age":age,"occupation":user_input["occupation"]}

    # 4. Nutrition agent
    nutrition_output = nutrition_agent(metrics,cot_log)
    # 5. Lifestyle agent
    lifestyle_output = lifestyle_agent(metrics,cot_log)
    # 6. Action plan agent
    action_plan = action_plan_agent(nutrition_output,lifestyle_output,cot_log)

    # 7. PDF
    action_plan["PDF_Report"] = generate_pdf_report(action_plan)
    action_plan["CoT_Log"] = cot_log

    return action_plan

# ---------------- Test case ----------------
if __name__ == "__main__":
    user_input = {
        "weight_kg":70,"height_m":1.75,"waist_cm":85,"hip_cm":95,
        "age":25,"sex":"male","activity_level":"moderate","occupation":"office",
        "query":"Assess my health and generate nutrition & lifestyle plan"
    }
    result = run_pipeline(user_input)
    print(result)