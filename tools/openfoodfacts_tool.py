import requests
from time import sleep

def get_food_info(food_name: str, max_retries: int = 3):
    """
    Fetch nutrition info from OpenFoodFacts for a given food name.
    Retries up to max_retries on timeout or connection error.
    """
    url = f"https://world.openfoodfacts.org/cgi/search.pl"
    headers = {
        "User-Agent": "NutritionGeminiADK/1.0 +https://github.com/Cammy276/nutritionist-agentic-rag.git"
    }
    params = {
        "search_terms": food_name,
        "search_simple": 1,
        "action": "process",
        "json": 1
    }

    for attempt in range(1, max_retries + 1):
        try:
            r = requests.get(url, headers=headers, params=params, timeout=30)
            r.raise_for_status()
            data = r.json()
            products = data.get("products", [])
            if products:
                product = products[0]
                nutriments = product.get("nutriments", {})
                return {
                    "name": product.get("product_name", "Unknown"),
                    "energy_kcal": nutriments.get("energy-kcal_100g", "N/A"),
                    "proteins_g": nutriments.get("proteins_100g", "N/A"),
                    "carbs_g": nutriments.get("carbohydrates_100g", "N/A"),
                    "fat_g": nutriments.get("fat_100g", "N/A")
                }
            return {"error": "Food not found"}
        except requests.exceptions.Timeout:
            if attempt < max_retries:
                sleep(1)  # wait a bit before retry
                continue
            return {"error": "Request timed out after multiple attempts"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    return {"error": "Failed to fetch food info"}