import requests

def test_openfoodfacts(product_code: str):
    """Test usage of the OpenFoodFacts API for a given barcode."""

    url = f"https://world.openfoodfacts.org/api/v0/product/{product_code}.json"

    headers = {
        "User-Agent": "NutritionGeminiADK/1.0 +https://github.com/Cammy276/nutritionist-agentic-rag.git",
        # Replace the GitHub URL with your project if you have one
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("Request timed out — try increasing timeout or check your connection.")
        return
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        return
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return

    data = response.json()

    if data.get("status") != 1:
        print("Product not found:", data.get("status_verbose"))
        return

    product = data.get("product", {})

    # Extract some common fields
    product_name = product.get("product_name", "Unknown")
    brands = product.get("brands", "Unknown")
    energy = product.get("nutriments", {}).get("energy-kcal_100g", "N/A")
    proteins = product.get("nutriments", {}).get("proteins_100g", "N/A")
    carbs = product.get("nutriments", {}).get("carbohydrates_100g", "N/A")
    fats = product.get("nutriments", {}).get("fat_100g", "N/A")

    print(f"Product: {product_name}")
    print(f"Brands: {brands}")
    print(f"Energy (kcal/100g): {energy}")
    print(f"Proteins (g/100g): {proteins}")
    print(f"Carbs (g/100g): {carbs}")
    print(f"Fats (g/100g): {fats}")


# Example usage
if __name__ == "__main__":
    barcode = input("Enter product barcode (e.g., 737628064502): ")
    test_openfoodfacts(barcode)