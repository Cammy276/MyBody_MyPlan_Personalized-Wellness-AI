import requests

def get_food_info(food_name: str):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={food_name}&search_simple=1&action=process&json=1"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        products = data.get("products", [])
        if products:
            product = products[0]
            return {
                "name": product.get("product_name", "Unknown"),
                "energy_kcal": product.get("nutriments", {}).get("energy-kcal_100g", "N/A"),
                "proteins_g": product.get("nutriments", {}).get("proteins_100g", "N/A"),
                "carbs_g": product.get("nutriments", {}).get("carbohydrates_100g", "N/A"),
                "fat_g": product.get("nutriments", {}).get("fat_100g", "N/A")
            }
        return {"error": "Food not found"}
    except Exception as e:
        return {"error": str(e)}