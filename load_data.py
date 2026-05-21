import csv
import sqlite3

conn = sqlite3.connect("research_data.db")
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS project_data (
    project INTEGER PRIMARY KEY,
    subject TEXT NOT NULL,
    condition TEXT NOT NULL,
    age INTEGER,
    sex TEXT,
    treatment TEXT,
    response TEXT,
    sample TEXT,
    sample_type TEXT,
    time_from_treatment_start INTEGER,
    b_cell INTEGER,
    cd8_t_cell INTEGER,
    cd4_t_cell INTEGER,
    nk_cell INTEGER,
    monocyte INTEGER);""")

with open("cell-count.csv", "r") as file:
    reader = csv.DictReader(file)

    for row in reader:
        cursor.execute(
            """
            INSERT INTO project_data (
                subject, condition, age, sex, treatment, response, 
                sample, sample_type, time_from_treatment_start, 
                b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                row["subject"],
                (row["condition"]) if row["condition"] else None,
                int(row["age"]) if row["age"] else None,
                row["sex"],
                row["treatment"],
                row["response"],
                row["sample"],
                row["sample_type"],
                (
                    int(row["time_from_treatment_start"])
                    if row["time_from_treatment_start"]
                    else None
                ),
                int(row["b_cell"]) if row["b_cell"] else 0,
                int(row["cd8_t_cell"]) if row["cd8_t_cell"] else 0,
                int(row["cd4_t_cell"]) if row["cd4_t_cell"] else 0,
                int(row["nk_cell"]) if row["nk_cell"] else 0,
                int(row["monocyte"]) if row["monocyte"] else 0,
            ),
        )
conn.commit()
conn.close()