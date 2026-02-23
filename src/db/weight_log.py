from src.db.schema import get_connection


def upsert_weight(
    db_path: str,
    date_str: str,
    weight_kg: float,
    body_fat_pct: float | None = None,
) -> None:
    con = get_connection(db_path)
    con.execute(
        """INSERT INTO weight_log (log_date, weight_kg, body_fat_pct)
           VALUES (?, ?, ?)
           ON CONFLICT(log_date) DO UPDATE SET
               weight_kg=excluded.weight_kg,
               body_fat_pct=excluded.body_fat_pct""",
        (date_str, weight_kg, body_fat_pct),
    )
    con.commit()
    con.close()


def get_weight_history(db_path: str, days: int = 30) -> list[dict]:
    con = get_connection(db_path)
    cur = con.cursor()
    cur.execute(
        """SELECT log_date, weight_kg, body_fat_pct
           FROM weight_log
           ORDER BY log_date DESC
           LIMIT ?""",
        (days,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    con.close()
    return list(reversed(rows))
