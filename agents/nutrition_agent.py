import os
import json
import google.genai as genai

from tools.openfoodfacts_tool import get_food_info
from tools.armour_tool import check_safe_prompt
# from tools.llm_judge import validate_nutrition_output

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def nutrition_agent(metrics, cot_log):
    """
    Generates a personalized nutrition plan based on user health metrics.
    Uses Gemini reasoning + OpenFoodFacts nutrition database.
    """

    cot_log.append("Nutrition agent started.")

    prompt = f"""
    You are a professional nutritionist.

    User health metrics:
    {metrics}

    Based on the user's:
    - BMI
    - BMR
    - Age
    - Occupation
    - Activity level

    Create a PERSONALIZED daily nutrition plan.

    Requirements:
    - Recommend meals appropriate for the user's calorie needs.
    - Adjust portion sizes or meal types depending on BMI.
    - Consider occupation (sedentary vs active).
    - Focus on balanced macronutrients.

    Return ONLY JSON:

    {{
        "breakfast": "meal name",
        "lunch": "meal name",
        "dinner": "meal name"
    }}
    """

    # ------------------------------------------------
    # 1️⃣ Armour Safety Check
    # ------------------------------------------------

    try:

        safe = check_safe_prompt(prompt)

        if not safe:
            cot_log.append("Armour blocked unsafe prompt.")
            raise ValueError("Unsafe prompt")

        cot_log.append("Armour safety passed.")

    except Exception as e:

        cot_log.append(f"Armour safeguard failed: {e}")

        return {
            "breakfast": get_food_info("Oatmeal with banana"),
            "lunch": get_food_info("Grilled chicken salad"),
            "dinner": get_food_info("Salmon with vegetables"),
            "fallback": True
        }

    # ------------------------------------------------
    # 2️⃣ Generate Meal Plan using Gemini
    # ------------------------------------------------

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )

        raw_output = response.text.strip()

        cot_log.append("Gemini generated personalized meal plan.")

    except Exception as e:

        cot_log.append(f"Gemini generation failed: {e}")

        return {
            "breakfast": get_food_info("Oatmeal with banana"),
            "lunch": get_food_info("Grilled chicken salad"),
            "dinner": get_food_info("Salmon with vegetables"),
            "fallback": True
        }

    # ------------------------------------------------
    # 3️⃣ Parse JSON
    # ------------------------------------------------

    try:

        plan_json = json.loads(raw_output)

        cot_log.append("JSON parsing successful.")

    except Exception:

        cot_log.append("JSON parsing failed. Using fallback meals.")

        plan_json = {
            "breakfast": "Oatmeal with banana",
            "lunch": "Grilled chicken salad",
            "dinner": "Salmon with vegetables"
        }

    # ------------------------------------------------
    # 4️⃣ LLM Judge Validation
    # ------------------------------------------------

    # try:

    #     valid = validate_nutrition_output(plan_json)

    #     if not valid:
    #         raise ValueError("LLM Judge rejected plan")

    #     cot_log.append("LLM Judge approved nutrition plan.")

    # except Exception as e:

    #     cot_log.append(f"Validation failed: {e}")

    #     plan_json = {
    #         "breakfast": "Oatmeal with banana",
    #         "lunch": "Grilled chicken salad",
    #         "dinner": "Salmon with vegetables"
    #     }

    # ------------------------------------------------
    # 5️⃣ Fetch Nutrition Data from OpenFoodFacts
    # ------------------------------------------------

    nutrition_output = {}

    try:

        for meal, food in plan_json.items():

            cot_log.append(f"Fetching nutrition info for {food}")

            nutrition_output[meal] = get_food_info(food)

        cot_log.append("Nutrition data retrieved successfully.")

    except Exception as e:

        cot_log.append(f"OpenFoodFacts lookup failed: {e}")

        nutrition_output = {
            "breakfast": get_food_info("Oatmeal with banana"),
            "lunch": get_food_info("Grilled chicken salad"),
            "dinner": get_food_info("Salmon with vegetables")
        }

    return nutrition_output