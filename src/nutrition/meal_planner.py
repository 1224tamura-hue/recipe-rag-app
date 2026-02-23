import random

MEAL_BUDGETS = {
    "朝食": 0.25,
    "昼食": 0.35,
    "夕食": 0.30,
    "間食": 0.10,
}


def suggest_meal_plan(
    recipes: list[dict],
    total_kcal: float,
    meal_types: list[str] | None = None,
) -> dict[str, dict | None]:
    if meal_types is None:
        meal_types = ["朝食", "昼食", "夕食", "間食"]

    plan: dict[str, dict | None] = {}

    for meal_type in meal_types:
        budget = total_kcal * MEAL_BUDGETS.get(meal_type, 0.25)
        candidates = [
            r for r in recipes
            if r.get("meal_type") == meal_type
            and r.get("calories_kcal", 0) <= budget * 1.2
        ]
        if not candidates:
            candidates = [
                r for r in recipes
                if r.get("calories_kcal", 0) <= budget * 1.2
            ]

        if candidates:
            best = min(candidates, key=lambda r: abs(r.get("calories_kcal", 0) - budget))
            plan[meal_type] = best
        else:
            plan[meal_type] = None

    return plan


def find_recipes_by_ingredients(
    recipes: list[dict],
    ingredients: list[str],
) -> list[tuple[int, dict]]:
    results = []
    for recipe in recipes:
        text = recipe.get("text", "") + " " + " ".join(recipe.get("tags", []))
        count = sum(1 for ing in ingredients if ing.strip() in text)
        if count > 0:
            results.append((count, recipe))
    results.sort(key=lambda x: x[0], reverse=True)
    return results


def generate_shopping_list(recipes: list[dict]) -> dict[str, list[str]]:
    categories = {
        "肉・魚": ["鶏", "豚", "牛", "鮭", "サバ", "たら", "あさり", "魚"],
        "大豆・卵・乳製品": ["豆腐", "卵", "納豆", "大豆", "チーズ", "ヨーグルト", "牛乳"],
        "野菜": ["もやし", "ほうれん草", "ブロッコリー", "キャベツ", "玉ねぎ", "大根",
                 "ズッキーニ", "パプリカ", "トマト", "きゅうり", "春菊", "きのこ",
                 "えのき", "しめじ", "舞茸", "わかめ"],
        "穀物・麺": ["玄米", "白米", "オートミール", "豆腐麺", "全粒粉", "キヌア"],
        "調味料・缶詰": ["ポン酢", "醤油", "みりん", "塩麹", "味噌", "ごま油",
                       "オリーブオイル", "酢", "サバ缶", "トマト缶"],
        "その他": [],
    }

    all_ingredients: list[str] = []
    for recipe in recipes:
        text = recipe.get("text", "")
        material_section = ""
        for line in text.split("\n"):
            if "【材料】" in line:
                material_section = line.replace("【材料】", "")
                break
        items = [i.strip() for i in material_section.replace("、", ",").split(",") if i.strip()]
        all_ingredients.extend(items)

    unique_ingredients = list(dict.fromkeys(all_ingredients))

    categorized: dict[str, list[str]] = {cat: [] for cat in categories}
    for ing in unique_ingredients:
        matched = False
        for cat, keywords in categories.items():
            if any(kw in ing for kw in keywords):
                categorized[cat].append(ing)
                matched = True
                break
        if not matched:
            categorized["その他"].append(ing)

    return {cat: items for cat, items in categorized.items() if items}
