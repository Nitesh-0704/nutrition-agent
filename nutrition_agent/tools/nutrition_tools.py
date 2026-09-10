from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class NutrientQueryInput(BaseModel):
    """Input for looking up nutrient information."""
    food_item: str = Field(..., description="The food item or ingredient to look up (e.g. 'banana', 'grilled chicken breast')")
    serving_size_grams: Optional[float] = Field(
        default=100.0,
        description="Serving size in grams (default 100g)"
    )


class NutrientInfo(BaseModel):
    """Detailed nutrient breakdown for a food item."""
    food_item: str = Field(description="Name of the food item")
    serving_size_grams: float = Field(description="Serving size in grams")
    calories: float = Field(description="Calories (kcal)")
    protein_g: float = Field(description="Protein in grams")
    carbohydrates_g: float = Field(description="Carbohydrates in grams")
    dietary_fiber_g: float = Field(description="Dietary fibre in grams")
    sugars_g: float = Field(description="Sugars in grams")
    fat_g: float = Field(description="Total fat in grams")
    saturated_fat_g: float = Field(description="Saturated fat in grams")
    sodium_mg: float = Field(description="Sodium in milligrams")
    potassium_mg: float = Field(description="Potassium in milligrams")
    calcium_mg: float = Field(description="Calcium in milligrams")
    iron_mg: float = Field(description="Iron in milligrams")
    vitamin_c_mg: float = Field(description="Vitamin C in milligrams")
    vitamin_a_iu: float = Field(description="Vitamin A in IU")
    health_benefits: List[str] = Field(description="Key health benefits of this food")
    cautions: List[str] = Field(description="Dietary cautions or allergen notes")


class DietPlanInput(BaseModel):
    """Input for generating a personalised diet plan."""
    goal: str = Field(
        ...,
        description="Primary health goal: 'weight_loss', 'muscle_gain', 'maintenance', 'heart_health', 'diabetes_management', or 'general_wellness'"
    )
    age: int = Field(..., description="Age of the person in years")
    gender: str = Field(..., description="Gender: 'male', 'female', or 'other'")
    weight_kg: float = Field(..., description="Current weight in kilograms")
    height_cm: float = Field(..., description="Height in centimetres")
    activity_level: str = Field(
        ...,
        description="Activity level: 'sedentary', 'lightly_active', 'moderately_active', 'very_active', or 'extra_active'"
    )
    dietary_restrictions: Optional[List[str]] = Field(
        default=[],
        description="Dietary restrictions or allergies (e.g. ['gluten_free', 'lactose_intolerant', 'vegetarian', 'vegan', 'nut_allergy'])"
    )
    duration_weeks: Optional[int] = Field(default=4, description="Duration of the diet plan in weeks (default 4)")


class MealPlan(BaseModel):
    """A single day's meal plan."""
    breakfast: str = Field(description="Breakfast meal description")
    mid_morning_snack: str = Field(description="Mid-morning snack")
    lunch: str = Field(description="Lunch meal description")
    afternoon_snack: str = Field(description="Afternoon snack")
    dinner: str = Field(description="Dinner meal description")
    estimated_calories: int = Field(description="Estimated total daily calories")


class DietPlan(BaseModel):
    """Complete personalised diet plan."""
    goal: str = Field(description="Health goal")
    daily_calorie_target: int = Field(description="Recommended daily calorie intake")
    bmi: float = Field(description="Calculated Body Mass Index")
    bmi_category: str = Field(description="BMI category (Underweight / Normal / Overweight / Obese)")
    key_nutrients_to_focus: List[str] = Field(description="Nutrients to prioritise based on goal")
    foods_to_include: List[str] = Field(description="Foods to include regularly")
    foods_to_avoid: List[str] = Field(description="Foods to limit or avoid")
    sample_weekly_plan: Dict[str, Any] = Field(description="7-day sample meal plan")
    hydration_advice: str = Field(description="Daily water intake recommendation")
    supplementation_tips: List[str] = Field(description="Optional supplement suggestions")
    general_tips: List[str] = Field(description="Lifestyle and dietary tips")
    duration_weeks: int = Field(description="Recommended plan duration in weeks")


# ---------------------------------------------------------------------------
# Nutrient database (representative values per 100 g)
# ---------------------------------------------------------------------------

NUTRIENT_DB: Dict[str, Dict[str, Any]] = {
    "banana": {
        "calories": 89, "protein_g": 1.1, "carbohydrates_g": 22.8, "dietary_fiber_g": 2.6,
        "sugars_g": 12.2, "fat_g": 0.3, "saturated_fat_g": 0.1, "sodium_mg": 1,
        "potassium_mg": 358, "calcium_mg": 5, "iron_mg": 0.3, "vitamin_c_mg": 8.7, "vitamin_a_iu": 64,
        "health_benefits": ["Excellent potassium source", "Supports heart health", "Boosts energy quickly", "Rich in Vitamin B6"],
        "cautions": ["High in natural sugars – moderate for diabetics", "Avoid if on potassium-restricted diet"],
    },
    "chicken breast": {
        "calories": 165, "protein_g": 31.0, "carbohydrates_g": 0.0, "dietary_fiber_g": 0.0,
        "sugars_g": 0.0, "fat_g": 3.6, "saturated_fat_g": 1.0, "sodium_mg": 74,
        "potassium_mg": 256, "calcium_mg": 15, "iron_mg": 1.0, "vitamin_c_mg": 0.0, "vitamin_a_iu": 21,
        "health_benefits": ["High-quality lean protein", "Supports muscle growth", "Low in fat", "Rich in B vitamins"],
        "cautions": ["Avoid deep frying", "Ensure fully cooked (internal temp 75°C)"],
    },
    "spinach": {
        "calories": 23, "protein_g": 2.9, "carbohydrates_g": 3.6, "dietary_fiber_g": 2.2,
        "sugars_g": 0.4, "fat_g": 0.4, "saturated_fat_g": 0.1, "sodium_mg": 79,
        "potassium_mg": 558, "calcium_mg": 99, "iron_mg": 2.7, "vitamin_c_mg": 28.1, "vitamin_a_iu": 9377,
        "health_benefits": ["Very high in iron", "Excellent Vitamin K and A source", "Supports bone health", "Anti-inflammatory"],
        "cautions": ["High in oxalates – limit for kidney stone risk", "May interact with blood thinners (Vitamin K)"],
    },
    "brown rice": {
        "calories": 216, "protein_g": 4.5, "carbohydrates_g": 44.8, "dietary_fiber_g": 3.5,
        "sugars_g": 0.7, "fat_g": 1.8, "saturated_fat_g": 0.4, "sodium_mg": 10,
        "potassium_mg": 154, "calcium_mg": 23, "iron_mg": 1.0, "vitamin_c_mg": 0.0, "vitamin_a_iu": 0,
        "health_benefits": ["Whole grain – sustained energy", "Supports digestion", "Lowers cholesterol", "Gluten-free"],
        "cautions": ["Higher calorie than vegetables – portion control recommended"],
    },
    "egg": {
        "calories": 155, "protein_g": 13.0, "carbohydrates_g": 1.1, "dietary_fiber_g": 0.0,
        "sugars_g": 1.1, "fat_g": 11.0, "saturated_fat_g": 3.3, "sodium_mg": 124,
        "potassium_mg": 138, "calcium_mg": 56, "iron_mg": 1.8, "vitamin_c_mg": 0.0, "vitamin_a_iu": 540,
        "health_benefits": ["Complete protein with all essential amino acids", "Rich in choline for brain health", "Contains Vitamin D and B12"],
        "cautions": ["Contains cholesterol – limit to 1-2/day for heart conditions", "Egg allergy is common"],
    },
    "apple": {
        "calories": 52, "protein_g": 0.3, "carbohydrates_g": 13.8, "dietary_fiber_g": 2.4,
        "sugars_g": 10.4, "fat_g": 0.2, "saturated_fat_g": 0.0, "sodium_mg": 1,
        "potassium_mg": 107, "calcium_mg": 6, "iron_mg": 0.1, "vitamin_c_mg": 4.6, "vitamin_a_iu": 54,
        "health_benefits": ["Rich in antioxidants (quercetin)", "Supports gut health", "May reduce heart disease risk", "Low glycaemic index"],
        "cautions": ["Seeds contain trace cyanide – do not consume", "Moderate for diabetics due to fruit sugar"],
    },
    "salmon": {
        "calories": 208, "protein_g": 20.4, "carbohydrates_g": 0.0, "dietary_fiber_g": 0.0,
        "sugars_g": 0.0, "fat_g": 13.4, "saturated_fat_g": 3.1, "sodium_mg": 59,
        "potassium_mg": 363, "calcium_mg": 12, "iron_mg": 0.8, "vitamin_c_mg": 3.9, "vitamin_a_iu": 149,
        "health_benefits": ["Excellent omega-3 fatty acids source", "Supports heart & brain health", "High in Vitamin D", "Anti-inflammatory"],
        "cautions": ["High mercury content in farmed varieties – limit during pregnancy", "Fish allergy"],
    },
}


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool(permission=ToolPermission.READ_ONLY)
def get_nutrient_info(query: NutrientQueryInput) -> NutrientInfo:
    """
    Retrieve detailed nutritional information for a given food item.

    Looks up macronutrients (protein, carbs, fat), micronutrients (vitamins,
    minerals), health benefits, and dietary cautions for the requested food.
    If the exact item is not found in the database it returns best-estimate
    generic values.

    Args:
        query (NutrientQueryInput): Food item name and optional serving size in grams.

    Returns:
        NutrientInfo: Full nutrient breakdown including macros, micros,
                      health benefits, and cautions.
    """
    key = query.food_item.lower().strip()
    scale = query.serving_size_grams / 100.0

    # Try exact match then partial match
    data = NUTRIENT_DB.get(key)
    if data is None:
        for db_key, db_val in NUTRIENT_DB.items():
            if db_key in key or key in db_key:
                data = db_val
                break

    if data is None:
        # Generic fallback
        data = {
            "calories": 100, "protein_g": 5, "carbohydrates_g": 15, "dietary_fiber_g": 2,
            "sugars_g": 3, "fat_g": 3, "saturated_fat_g": 0.5, "sodium_mg": 50,
            "potassium_mg": 200, "calcium_mg": 30, "iron_mg": 0.5, "vitamin_c_mg": 5, "vitamin_a_iu": 100,
            "health_benefits": ["Provides essential nutrients", "Part of a balanced diet"],
            "cautions": ["Check for personal allergies or intolerances"],
        }

    return NutrientInfo(
        food_item=query.food_item,
        serving_size_grams=query.serving_size_grams,
        calories=round(data["calories"] * scale, 1),
        protein_g=round(data["protein_g"] * scale, 1),
        carbohydrates_g=round(data["carbohydrates_g"] * scale, 1),
        dietary_fiber_g=round(data["dietary_fiber_g"] * scale, 1),
        sugars_g=round(data["sugars_g"] * scale, 1),
        fat_g=round(data["fat_g"] * scale, 1),
        saturated_fat_g=round(data["saturated_fat_g"] * scale, 1),
        sodium_mg=round(data["sodium_mg"] * scale, 1),
        potassium_mg=round(data["potassium_mg"] * scale, 1),
        calcium_mg=round(data["calcium_mg"] * scale, 1),
        iron_mg=round(data["iron_mg"] * scale, 2),
        vitamin_c_mg=round(data["vitamin_c_mg"] * scale, 1),
        vitamin_a_iu=round(data["vitamin_a_iu"] * scale, 0),
        health_benefits=data["health_benefits"],
        cautions=data["cautions"],
    )


@tool(permission=ToolPermission.READ_ONLY)
def generate_diet_plan(plan_input: DietPlanInput) -> DietPlan:
    """
    Generate a personalised diet plan based on health goals, body metrics,
    and dietary preferences.

    Calculates BMI, estimates daily calorie needs using the Mifflin-St Jeor
    equation, and constructs a 7-day sample meal plan with targeted nutrition
    advice.

    Args:
        plan_input (DietPlanInput): User's goal, age, gender, weight, height,
                                    activity level, dietary restrictions, and
                                    desired plan duration.

    Returns:
        DietPlan: Complete personalised diet plan with calorie targets,
                  food recommendations, sample 7-day meal plan, hydration
                  advice, supplement tips, and general lifestyle guidance.
    """
    # --- BMI ---
    height_m = plan_input.height_cm / 100.0
    bmi = round(plan_input.weight_kg / (height_m ** 2), 1)
    if bmi < 18.5:
        bmi_cat = "Underweight"
    elif bmi < 25:
        bmi_cat = "Normal weight"
    elif bmi < 30:
        bmi_cat = "Overweight"
    else:
        bmi_cat = "Obese"

    # --- BMR (Mifflin-St Jeor) ---
    if plan_input.gender.lower() == "male":
        bmr = 10 * plan_input.weight_kg + 6.25 * plan_input.height_cm - 5 * plan_input.age + 5
    else:
        bmr = 10 * plan_input.weight_kg + 6.25 * plan_input.height_cm - 5 * plan_input.age - 161

    activity_map = {
        "sedentary": 1.2, "lightly_active": 1.375, "moderately_active": 1.55,
        "very_active": 1.725, "extra_active": 1.9,
    }
    tdee = bmr * activity_map.get(plan_input.activity_level, 1.375)

    goal = plan_input.goal.lower()
    if goal == "weight_loss":
        calorie_target = int(tdee - 500)
        key_nutrients = ["Protein (1.6-2g/kg body weight)", "Dietary Fibre (25-35g/day)", "Vitamin B12", "Iron", "Calcium"]
        include = ["Lean proteins (chicken, turkey, tofu)", "Non-starchy vegetables", "Legumes", "Whole grains", "Berries", "Green tea"]
        avoid = ["Sugary beverages", "Ultra-processed foods", "Refined carbohydrates", "Trans fats", "Alcohol", "High-calorie snacks"]
        supplements = ["Whey or plant protein", "Multivitamin", "Omega-3"]
    elif goal == "muscle_gain":
        calorie_target = int(tdee + 300)
        key_nutrients = ["Protein (2-2.5g/kg body weight)", "Complex Carbohydrates", "Creatine", "Zinc", "Magnesium"]
        include = ["Chicken breast", "Eggs", "Greek yoghurt", "Salmon", "Quinoa", "Sweet potato", "Oats", "Milk"]
        avoid = ["Alcohol", "Low-calorie diets", "Trans fats", "Excessive sugar"]
        supplements = ["Creatine monohydrate", "Whey protein", "BCAA", "Vitamin D3"]
    elif goal == "heart_health":
        calorie_target = int(tdee)
        key_nutrients = ["Omega-3 fatty acids", "Fibre", "Potassium", "Magnesium", "Antioxidants (Vitamin C, E)"]
        include = ["Fatty fish (salmon, mackerel)", "Olive oil", "Nuts", "Berries", "Leafy greens", "Oats", "Avocado"]
        avoid = ["Saturated fats", "Trans fats", "Excess sodium (>2g/day)", "Processed meats", "Sugary drinks"]
        supplements = ["Omega-3 fish oil", "CoQ10", "Magnesium"]
    elif goal == "diabetes_management":
        calorie_target = int(tdee)
        key_nutrients = ["Low-GI Carbohydrates", "Dietary Fibre (>30g/day)", "Chromium", "Magnesium", "Protein"]
        include = ["Non-starchy vegetables", "Legumes", "Whole grains", "Lean meats", "Nuts & seeds", "Greek yoghurt"]
        avoid = ["Sugary beverages", "White rice & bread", "Fried foods", "Sweets & desserts", "Alcohol on empty stomach"]
        supplements = ["Berberine", "Chromium picolinate", "Magnesium", "Alpha-lipoic acid"]
    else:
        calorie_target = int(tdee)
        key_nutrients = ["Protein", "Complex Carbohydrates", "Healthy Fats", "Vitamins A, C, D, E", "Calcium", "Iron"]
        include = ["Colourful vegetables", "Fruits", "Whole grains", "Lean proteins", "Dairy or alternatives", "Nuts & seeds"]
        avoid = ["Ultra-processed foods", "Excessive added sugar", "Trans fats", "High-sodium packaged foods"]
        supplements = ["Multivitamin", "Omega-3", "Vitamin D3"]

    # Adjust for vegetarian/vegan
    restrictions = [r.lower() for r in (plan_input.dietary_restrictions or [])]
    if "vegan" in restrictions or "vegetarian" in restrictions:
        include = [f for f in include if "chicken" not in f.lower() and "salmon" not in f.lower()
                   and "meat" not in f.lower() and "fish" not in f.lower()]
        include += ["Lentils", "Chickpeas", "Tempeh", "Tofu", "Nutritional yeast"]
        if "vegan" in restrictions:
            include = [f for f in include if "egg" not in f.lower() and "yoghurt" not in f.lower()
                       and "dairy" not in f.lower() and "milk" not in f.lower()]
            include += ["Fortified plant milk", "Chia seeds", "Hemp seeds"]
            supplements.append("Vitamin B12 (essential for vegans)")

    sample_plan = {
        "Monday": {"breakfast": "Oats with berries and chia seeds", "lunch": "Grilled chicken salad (or tofu for vegan)", "dinner": "Stir-fried vegetables with brown rice"},
        "Tuesday": {"breakfast": "Greek yoghurt with banana and walnuts", "lunch": "Lentil soup with whole grain bread", "dinner": "Baked salmon with sweet potato and spinach"},
        "Wednesday": {"breakfast": "Scrambled eggs with spinach and whole grain toast", "lunch": "Quinoa bowl with roasted vegetables", "dinner": "Turkey or chickpea curry with brown rice"},
        "Thursday": {"breakfast": "Smoothie: spinach, banana, protein powder, almond milk", "lunch": "Whole grain wrap with avocado and lean protein", "dinner": "Grilled fish or paneer with asparagus and quinoa"},
        "Friday": {"breakfast": "Overnight oats with nuts and seeds", "lunch": "Bean and vegetable chilli", "dinner": "Stir-fried tofu or chicken with edamame and noodles"},
        "Saturday": {"breakfast": "Avocado toast on whole grain bread with poached eggs", "lunch": "Large leafy green salad with salmon or chickpeas", "dinner": "Home-made vegetable soup with whole grain rolls"},
        "Sunday": {"breakfast": "Whole grain pancakes with fresh fruit", "lunch": "Buddha bowl: grains, roasted veg, beans, tahini dressing", "dinner": "Slow-cooked lean stew or vegetable dhal"},
    }

    return DietPlan(
        goal=plan_input.goal,
        daily_calorie_target=calorie_target,
        bmi=bmi,
        bmi_category=bmi_cat,
        key_nutrients_to_focus=key_nutrients,
        foods_to_include=include,
        foods_to_avoid=avoid,
        sample_weekly_plan=sample_plan,
        hydration_advice=f"Drink at least {round(plan_input.weight_kg * 0.033, 1)} litres of water daily. Add an extra 500ml for every 30 minutes of exercise.",
        supplementation_tips=supplements,
        general_tips=[
            "Eat 3 balanced meals and 2 healthy snacks per day",
            "Chew slowly and eat mindfully to improve digestion and satiety",
            "Prepare meals in advance to avoid unhealthy convenience choices",
            "Read nutrition labels – focus on ingredients, not just calories",
            "Sleep 7-9 hours per night for optimal metabolic function",
            "Combine diet with at least 150 minutes of moderate exercise per week",
        ],
        duration_weeks=plan_input.duration_weeks or 4,
    )
