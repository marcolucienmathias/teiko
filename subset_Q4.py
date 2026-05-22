## QUESTION 4

import sqlite3
import pandas as pd

output = 'filtered_baseline_data.csv'

# Connect to the database
conn = sqlite3.connect("research_data.db")

#specific subset
base_conditions = """
    condition = 'melanoma' 
    AND sample_type = 'PBMC' 
    AND treatment = 'miraclib' 
    AND time_from_treatment_start = 0
"""

save_qry = f"SELECT * FROM project_data WHERE {base_conditions}"
df_base_conditions = pd.read_sql_query(save_qry, conn)
df_base_conditions.to_csv(output, index = False)

#how many samples from each project

query_projects = f"""
    SELECT project, COUNT(sample) as sample_count
    FROM project_data
    WHERE {base_conditions}
    GROUP BY project;
"""
df_projects = pd.read_sql_query(query_projects, conn)
print("--- Samples per Project ---")
print(df_projects, "\n")
df_projects.to_csv('samples_per_project.csv', index=False)


#how many subjects were responders vs non-responders?
query_response = f"""
    SELECT response, COUNT(DISTINCT subject) as subject_count
    FROM project_data
    WHERE {base_conditions}
      AND response IN ('yes', 'no')
    GROUP BY response;
"""
df_response = pd.read_sql_query(query_response, conn)
print("--- Subjects by Response ---")
print(df_response, "\n")
df_response.to_csv('subjects_by_response.csv', index=False)


#how many subjects were males vs females?
#DISTINCT counts subjects not samples 
query_sex = f"""
    SELECT sex, COUNT(DISTINCT subject) as subject_count
    FROM project_data
    WHERE {base_conditions}
    GROUP BY sex;
"""
df_sex = pd.read_sql_query(query_sex, conn)
print("--- Subjects by Sex ---")
print(df_sex)
df_sex.to_csv('subjects_by_sex.csv', index=False)

conn.close()
