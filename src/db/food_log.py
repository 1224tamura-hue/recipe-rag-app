from src.db.schema import get_connection


def add_food_log_entry(db_path: str, entry: dict) -> None:
    con = get_connection(db_path)
    con.execute(
        """INSERT INTO food_log
           (log_date, meal_type, recipe_id, recipe_title,
            calories_kcal, protein_g, fat_g, carbs_g)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            entry["log_date"], entry["meal_type"], entry.get("recipe_id"),
            entry["recipe_title"], entry["calories_kcal"],
            entry.get("protein_g", 0), entry.get("fat_g", 0), entry.get("carbs_g", 0),
        ),
    )
    con.commit()
    con.close()


def get_daily_log(db_path: str, date_str: str) -> list[dict]:
    con = get_connection(db_path)
    cur = con.cursor()
    cur.execute(
        "SELECT * FROM food_log WHERE log_date=? ORDER BY created_at",
        (date_str,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    con.close()
    return rows


def get_daily_totals(db_path: str, date_str: str) -> dict:
    con = get_connection(db_path)
    cur = con.cursor()
    cur.execute(
        """SELECT
               COALESCE(SUM(calories_kcal), 0) AS calories_kcal,
               COALESCE(SUM(protein_g), 0)     AS protein_g,
               COALESCE(SUM(fat_g), 0)         AS fat_g,
               COALESCE(SUM(carbs_g), 0)       AS carbs_g
           FROM food_log WHERE log_date=?""",
        (date_str,),
    )
    row = cur.fetchone()
    con.close()
    return dict(row) if row else {"calories_kcal": 0, "protein_g": 0, "fat_g": 0, "carbs_g": 0}


def delete_food_log_entry(db_path: str, entry_id: int) -> None:
    con = get_connection(db_path)
    con.execute("DELETE FROM food_log WHERE id=?", (entry_id,))
    con.commit()
    con.close()
