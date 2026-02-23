from dataclasses import dataclass
from typing import Literal

SexType = Literal["male", "female"]

ACTIVITY_FACTORS: dict[str, float] = {
    "sedentary":   1.2,
    "light":       1.375,
    "moderate":    1.55,
    "active":      1.725,
    "very_active": 1.9,
}

ACTIVITY_LABELS_JA: dict[str, str] = {
    "sedentary":   "座り仕事メイン（ほぼ運動なし）",
    "light":       "軽い運動（週1〜3日）",
    "moderate":    "中程度の運動（週3〜5日）",
    "active":      "ハードな運動（週6〜7日）",
    "very_active": "肉体労働 / 1日2回トレーニング",
}

SAFETY_FLOOR = {"male": 1500, "female": 1200}


@dataclass
class TDEEResult:
    bmr_kcal: float
    tdee_kcal: float
    target_kcal: float
    deficit_kcal: int
    protein_target_g: float
    fat_target_g: float
    carbs_target_g: float


def calc_bmr(weight_kg: float, height_cm: float, age: int, sex: SexType) -> float:
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    return base + 5 if sex == "male" else base - 161


def calc_tdee(
    weight_kg: float,
    height_cm: float,
    age: int,
    sex: SexType,
    activity_level: str,
    deficit_kcal: int = 350,
) -> TDEEResult:
    bmr = calc_bmr(weight_kg, height_cm, age, sex)
    factor = ACTIVITY_FACTORS.get(activity_level, 1.375)
    tdee = bmr * factor
    floor = SAFETY_FLOOR.get(sex, 1200)
    target = max(float(floor), tdee - deficit_kcal)

    protein_g = round(1.6 * weight_kg, 1)
    fat_g = round((target * 0.25) / 9, 1)
    carbs_g = round(max(0.0, (target - protein_g * 4 - fat_g * 9) / 4), 1)

    return TDEEResult(
        bmr_kcal=round(bmr, 1),
        tdee_kcal=round(tdee, 1),
        target_kcal=round(target, 1),
        deficit_kcal=deficit_kcal,
        protein_target_g=protein_g,
        fat_target_g=fat_g,
        carbs_target_g=carbs_g,
    )


def format_profile_context(profile: dict, result: TDEEResult) -> str:
    sex_ja = "男性" if profile["sex"] == "male" else "女性"
    return (
        f"{sex_ja}・{profile['age']}歳・身長{profile['height_cm']}cm・"
        f"体重{profile['weight_kg']}kg・目標体重{profile['goal_weight_kg']}kg。"
        f"1日の目標摂取カロリー: {result.target_kcal:.0f}kcal "
        f"（TDEE {result.tdee_kcal:.0f}kcal - {result.deficit_kcal}kcal赤字）。"
        f"PFC目標: たんぱく質{result.protein_target_g}g / "
        f"脂質{result.fat_target_g}g / 炭水化物{result.carbs_target_g}g。"
    )
