
**Immune Cell Population Dashboard & Pipeline**

This project includes a standardized `Makefile` to automate setup and execution within GitHub Codespaces. Run the following commands sequentially in your terminal:

make setup
make pipeline
make dashboard 

**File Explanation**

1. Setup
Installs all required third-party libraries listed in the `requirements.txt` file.

2. Pipeline
Executes the data pipeline. First initializes the SQLite database, parses the raw CSV file, populates the schema, runs the statistical analyses, and exports all diagnostic tables and high-resolution figures to root.

3. Dashboard
Starts a local web server hosting the Streamlit interactive dashboard.

**Schema Rationale**

The data management architecture relies on a local SQLite database, research_data.db (initialized and loaded via load_data.py.)

DB Schema: ‘project_data’
| Column Name | Data Type | Constraints / Description |
| :--- | :--- | :--- |
| `id` | `INTEGER` | Unique row identifier |
| `project` | `TEXT` | Name/ID of the research study (e.g., prj1) |
| `subject` | `TEXT` | Patient unique identifier |
| `condition` | `TEXT` | Medical diagnosis |
| `age` | `INTEGER` | Patient age |
| `sex` | `TEXT` | Patient biological sex (M/F) |
| `treatment` | `TEXT` | Therapeutic administered |
| `response` | `TEXT` | Clinical treatment outcome responder indicator (yes/no) |
| `sample` | `TEXT` | Unique biospecimen identifier |
| `sample_type` | `TEXT` | Tissue source matrix (e.g., PBMC, Tumor) |
| `time_from_treatment_start` | `INTEGER` | Timepoint tracking index in days (e.g., 0, 7, 14) |
| `b_cell` | `INTEGER` | Raw cell count |
| `cd8_t_cell` | `INTEGER` | Raw cell count |
| `cd4_t_cell` | `INTEGER` | Raw cell count |
| `nk_cell` | `INTEGER` | Raw cell count |
| `monocyte` | `INTEGER` | Raw cell count |


**Architecture Rationale + Scaling Ideas:**

This single-table schema is efficient for prototyping/single projects, but a clinical data model which must scale for hundreds of projects, thousands of patients, and multi-omic analytics will require some adjustments. To support that growth, I would normalize this schema into a star/snowflake structure:

projects Table: This avoids repeating project ‘meta’ details across millions of specimen rows.
subjects Table: (subject_id, age, sex, condition). Demographics are static, tracking them separately.
samples Table: Links tracking times back to a single subject.
cell_counts Table: Contains numeric measurements.

**Code Structure & Design Choices**
This repository contains the following files. Each script handles a discrete stage of the data pipeline:

| File | Description |
| :--- | :--- |
| `cell-count.csv` | Raw input data |
| `requirements.txt` | Project dependencies |
| `Makefile` | Autorun blueprint |
| `load_data.py` | Part 1: .db formation |
| `generate_summary_table_Q2_3.py` | Parts 2&3: form plot + run statistics |
| `subset_Q4.py` | Part 4: Subset queries |
| `app.py` | Interactive Dashboard (streamlit) |
| `subjects_by_sex.csv` | Output of Part 4: Breakdown of sex in subset |
| `samples_per_project.csv` | Output of Part 4: Breakdown of sample count per project in subset |
| `subjects_by_response.csv` | Output of Part 4: Breakdown of responses in subset |
| `clinical_trial_statistics.csv` | Output of Part 3: Mann-Whitney U test results. |
| `relfreq_plot.png` | Output of Part 3: Plot of cell-type relative frequency comparing responders to non-responders. |
| `relative_frequencies_table.csv` | Output of Part 2: long-format cell_type to within sample relative frequency |
| `filtered_baseline_data.csv` | Output of Part 4: baseline data for melanoma patients treated with miraclib |


**Architectural Decisions**

Preserving Floating-Point Precision: Statistical testing via scipy.stats.mannwhitneyu was conducted using maximum unrounded float precision. Percentages are only formatted or truncated during visual display to prevent rounding distortions from skewing the true statistical P-values.

**Dashboard Overview & Functionality**

Dynamic Filters: Selection boxes allow for hot-swappable parameters to filter the data quickly.

Responsive Visualizations: Boxplots which update to reflect selected data.

Dynamic Statistics: Mann-Whitney test for selected data.

Data Portability: Included download button to save filtered data to .csv from dashboard itself.

