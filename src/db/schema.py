import sqlite3

CREATE_USER_PROFILE = """
CREATE TABLE IF NOT EXISTS user_profile (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    age             INTEGER NOT NULL,
    sex             TEXT    NOT NULL CHECK(sex IN ('male', 'female')),
    height_cm       REAL    NOT NULL,
    weight_kg       REAL    NOT NULL,
    goal_weight_kg  REAL    NOT NULL,
    activity_level  TEXT    NOT NULL
                    CHECK(activity_level IN
                          ('sedentary','light','moderate','active','very_active')),
    calorie_deficit INTEGER NOT NULL DEFAULT 350,
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);
"""

CREATE_FOOD_LOG = """
CREATE TABLE IF NOT EXISTS food_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date      TEXT    NOT NULL,
    meal_type     TEXT    NOT NULL
                  CHECK(meal_type IN ('朝食','昼食','夕食','間食')),
    recipe_id     TEXT,
    recipe_title  TEXT    NOT NULL,
    calories_kcal REAL    NOT NULL,
    protein_g     REAL    NOT NULL DEFAULT 0,
    fat_g         REAL    NOT NULL DEFAULT 0,
    carbs_g       REAL    NOT NULL DEFAULT 0,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);
"""

CREATE_WEIGHT_LOG = """
CREATE TABLE IF NOT EXISTS weight_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date     TEXT    NOT NULL UNIQUE,
    weight_kg    REAL    NOT NULL,
    body_fat_pct REAL,
    created_at   TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);
"""


def init_db(db_path: str) -> None:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.executescript(CREATE_USER_PROFILE + CREATE_FOOD_LOG + CREATE_WEIGHT_LOG)
    con.commit()
    con.close()


def get_connection(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con
