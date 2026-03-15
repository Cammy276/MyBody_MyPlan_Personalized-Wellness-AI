import os
import json
import google.genai as genai

from tools.armour_tool import check_safe_prompt
# from tools.llm_judge import validate_action_plan

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def action_plan_agent(nutrition_output, lifestyle_output, cot_log):
    """
    Combines outputs from nutrition_agent and lifestyle_agent
    to generate a consolidated SMART action plan.
    """

    cot_log.append("Action Plan agent started.")

    prompt = f"""
    You are a professional health coach.

    Nutrition plan:
    {nutrition_output}

    Lifestyle plan:
    {lifestyle_output}

    Based on the provided plans, generate SMART health objectives.

    SMART means:
    - Specific
    - Measurable
    - Achievable
    - Relevant
    - Time-bound

    Requirements:
    - Produce 3 SMART goals
    - Each goal must clearly include measurable targets
    - Each goal should include a timeframe (e.g., daily, weekly)

    Return ONLY JSON:

    {{
        "SMART_Objectives": [
            {{
                "goal": "description",
                "specific": "...",
                "measurable": "...",
                "achievable": "...",
                "relevant": "...",
                "time_bound": "..."
            }},
            {{
                "goal": "...",
                "specific": "...",
                "measurable": "...",
                "achievable": "...",
                "relevant": "...",
                "time_bound": "..."
            }}
        ]
    }}
    """

    # --------------------------------
    # 1️⃣ Armour Safety Check
    # --------------------------------

    try:

        safe = check_safe_prompt(prompt)

        if not safe:
            cot_log.append("Armour blocked unsafe prompt.")
            raise ValueError("Unsafe prompt")

        cot_log.append("Armour safety passed.")

    except Exception as e:

        cot_log.append(f"Armour safeguard failed: {e}")

        return {
            "Meals": nutrition_output,
            "Exercise": lifestyle_output["exercise"],
            "Hydration_Liters": lifestyle_output["hydration_liters"],
            "SMART_Objectives": [
                "Eat balanced meals daily for the next 30 days",
                "Exercise 30 minutes daily for the next 4 weeks",
                "Drink recommended water intake daily"
            ],
            "fallback": True
        }

    # --------------------------------
    # 2️⃣ Generate SMART Goals
    # --------------------------------

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )

        raw_output = response.text.strip()

        cot_log.append("Gemini generated SMART action plan.")

    except Exception as e:

        cot_log.append(f"SMART plan generation failed: {e}")

        return {
            "Meals": nutrition_output,
            "Exercise": lifestyle_output["exercise"],
            "Hydration_Liters": lifestyle_output["hydration_liters"],
            "SMART_Objectives": [
                "Eat balanced meals daily for the next 30 days",
                "Exercise 30 minutes daily for the next 4 weeks",
                "Drink recommended water intake daily"
            ],
            "fallback": True
        }

    # --------------------------------
    # 3️⃣ Parse JSON
    # --------------------------------

    try:

        plan_json = json.loads(raw_output)

        cot_log.append("SMART plan JSON parsed successfully.")

    except Exception:

        cot_log.append("SMART plan parsing failed, using fallback.")

        plan_json = {
            "SMART_Objectives": [
                {
                    "goal": "Improve daily nutrition",
                    "specific": "Eat 3 balanced meals daily",
                    "measurable": "Track meals each day",
                    "achievable": "Use simple healthy meals",
                    "relevant": "Supports better energy and health",
                    "time_bound": "Daily for 30 days"
                },
                {
                    "goal": "Increase physical activity",
                    "specific": "Perform 30 minutes of exercise",
                    "measurable": "Track exercise duration",
                    "achievable": "Use moderate intensity exercises",
                    "relevant": "Improves cardiovascular health",
                    "time_bound": "5 days per week for 4 weeks"
                },
                {
                    "goal": "Maintain hydration",
                    "specific": f"Drink {lifestyle_output['hydration_liters']} liters of water",
                    "measurable": "Track water intake daily",
                    "achievable": "Carry a water bottle",
                    "relevant": "Supports metabolism and recovery",
                    "time_bound": "Daily"
                }
            ]
        }

    # --------------------------------
    # 4️⃣ LLM Judge Validation
    # --------------------------------

    # try:

    #     valid = validate_action_plan(plan_json)

    #     if not valid:
    #         raise ValueError("LLM Judge rejected action plan")

    #     cot_log.append("LLM Judge approved action plan.")

    # except Exception as e:

    #     cot_log.append(f"Validation failed: {e}")

    # --------------------------------
    # 5️⃣ Final Consolidated Output
    # --------------------------------

    return {
        "Meals": nutrition_output,
        "Exercise": lifestyle_output["exercise"],
        "Hydration_Liters": lifestyle_output["hydration_liters"],
        "SMART_Objectives": plan_json["SMART_Objectives"]
    }