setup:
	pip install -r requirements.txt

pipeline:
	python load_data.py
	python generate_summary_table_Q2_3.py
	python subset_Q4.py

dashboard:
	streamlit run app.py
