import os
import json
import google.genai as genai

from tools.armour_tool import check_safe_prompt
# from tools.llm_judge import validate_lifestyle_output

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def lifestyle_agent(metrics, cot_log):
    """
    Generates a personalized lifestyle plan using Gemini.
    Exercise recommendations depend on BMI, age, occupation, activity level.
    Hydration is calculated locally.
    """

    cot_log.append("Lifestyle agent started.")

    prompt = f"""
    You are a certified fitness coach.

    User health metrics:
    {metrics}

    Based on the user's:
    - BMI
    - Age
    - Occupation
    - Activity level

    Recommend a PERSONALIZED daily exercise routine.

    Requirements:
    - Adjust intensity based on BMI
    - Sedentary occupations should include mobility exercises
    - Older users should have lower impact exercises
    - Provide 3 exercise activities

    Return ONLY JSON:

    {{
        "exercise": [
            "exercise 1",
            "exercise 2",
            "exercise 3"
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
            "exercise": ["30 min walking", "15 min stretching"],
            "hydration_liters": round(metrics["weight_kg"] * 0.035, 2),
            "fallback": True
        }

    # --------------------------------
    # 2️⃣ Generate Exercise Plan
    # --------------------------------

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )

        raw_output = response.text.strip()

        cot_log.append("Gemini generated lifestyle plan.")

    except Exception as e:

        cot_log.append(f"Lifestyle generation failed: {e}")

        return {
            "exercise": ["30 min walking", "15 min stretching"],
            "hydration_liters": round(metrics["weight_kg"] * 0.035, 2),
            "fallback": True
        }

    # --------------------------------
    # 3️⃣ Parse JSON
    # --------------------------------

    try:

        plan_json = json.loads(raw_output)

        cot_log.append("Lifestyle JSON parsed successfully.")

    except Exception:

        cot_log.append("JSON parsing failed. Using fallback exercises.")

        plan_json = {
            "exercise": ["30 min walking", "15 min stretching"]
        }

    # --------------------------------
    # 4️⃣ LLM-as-Judge Validation
    # --------------------------------

    # try:

    #     valid = validate_lifestyle_output(plan_json)

    #     if not valid:
    #         raise ValueError("LLM Judge rejected lifestyle plan")

    #     cot_log.append("LLM Judge approved lifestyle plan.")

    # except Exception as e:

    #     cot_log.append(f"Validation failed: {e}")

    #     plan_json = {
    #         "exercise": ["30 min walking", "15 min stretching"]
    #     }

    # --------------------------------
    # 5️⃣ Hydration Calculation (Local)
    # --------------------------------

    hydration = round(metrics["weight_kg"] * 0.035, 2)

    cot_log.append(f"Hydration calculated locally: {hydration} liters.")

    return {
        "exercise": plan_json["exercise"],
        "hydration_liters": hydration
    }