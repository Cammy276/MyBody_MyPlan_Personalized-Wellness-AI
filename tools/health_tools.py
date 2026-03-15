def calculate_bmi(weight_kg, height_m):
    return round(weight_kg / (height_m ** 2), 1)

def bmi_category(bmi):
    if bmi < 18.5: return "Underweight"
    elif bmi < 25: return "Normal weight"
    elif bmi < 30: return "Overweight"
    return "Obese"

def waist_to_hip_ratio(waist_cm, hip_cm):
    return round(waist_cm / hip_cm, 2)

def health_risk(bmi, whr):
    risk = []
    if bmi >= 25: risk.append("Overweight/Obesity risk")
    if whr > 0.9: risk.append("Central obesity risk")
    return risk or ["Low risk"]

def calculate_bmr(weight_kg, height_cm, age, sex):
    if sex.lower() == "male":
        return round(10*weight_kg + 6.25*height_cm - 5*age + 5)
    return round(10*weight_kg + 6.25*height_cm - 5*age - 161)