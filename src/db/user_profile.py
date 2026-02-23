from src.db.schema import get_connection


def upsert_profile(db_path: str, data: dict) -> None:
    con = get_connection(db_path)
    cur = con.cursor()
    cur.execute("SELECT id FROM user_profile LIMIT 1")
    row = cur.fetchone()
    if row:
        cur.execute(
            """UPDATE user_profile SET
               age=?, sex=?, height_cm=?, weight_kg=?, goal_weight_kg=?,
               activity_level=?, calorie_deficit=?,
               updated_at=datetime('now','localtime')
               WHERE id=?""",
            (
                data["age"], data["sex"], data["height_cm"], data["weight_kg"],
                data["goal_weight_kg"], data["activity_level"], data["calorie_deficit"],
                row["id"],
            ),
        )
    else:
        cur.execute(
            """INSERT INTO user_profile
               (age, sex, height_cm, weight_kg, goal_weight_kg, activity_level, calorie_deficit)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                data["age"], data["sex"], data["height_cm"], data["weight_kg"],
                data["goal_weight_kg"], data["activity_level"], data["calorie_deficit"],
            ),
        )
    con.commit()
    con.close()


def get_profile(db_path: str) -> dict | None:
    con = get_connection(db_path)
    cur = con.cursor()
    cur.execute("SELECT * FROM user_profile ORDER BY id LIMIT 1")
    row = cur.fetchone()
    con.close()
    return dict(row) if row else None
