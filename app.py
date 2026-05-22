import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu

#setup
st.set_page_config(page_title="Immune Cell Dashboard", layout="wide")
st.title("Immune Cell Analysis")

#cache to speed up
@st.cache_data

def load_data():
    df = pd.read_csv('cell-count.csv')
    df['response'] = df['response'].apply(lambda x : 'None' if pd.isnull(x) else x)
    
    #long_format (P2 analog)
    cell_cols = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']
    df_long = pd.melt(df, id_vars=['sample', 'condition', 'treatment', 'sample_type', 'response', 'time_from_treatment_start', 'sex'], 
                      value_vars=cell_cols, var_name='population', value_name='count')
    df_long['total_count'] = df_long.groupby('sample')['count'].transform('sum')
    df_long['percentage'] = (df_long['count'] / df_long['total_count']) * 100
    
    return df, df_long

raw_df, df_long = load_data()


available_times = sorted(raw_df['time_from_treatment_start'].unique())
available_conditions = sorted(raw_df['condition'].unique())
available_treatments = sorted(raw_df['treatment'].unique())
available_tissues = sorted(raw_df['sample_type'].unique())
available_responses = sorted(raw_df['response'].unique())
available_sexes = sorted(raw_df['sex'].unique())

#multiselect filters
st.sidebar.header("Filters")
selected_condition = st.sidebar.multiselect("Select Conditions", options=available_conditions, default=available_conditions)
selected_treatment = st.sidebar.multiselect("Select Treatment", options=available_treatments, default=available_treatments)
selected_tissue = st.sidebar.multiselect("Select Sample Type", options=available_tissues, default =available_tissues)
selected_times = st.sidebar.multiselect("Select Timepoints", options=available_times, default=available_times)
selected_response = st.sidebar.multiselect("Select Response", options=available_responses, default=available_responses)
selected_sex = st.sidebar.multiselect('Select Sex', options=available_sexes, default=available_sexes)


#generate filtered df
df_filtered = df_long[
    (df_long['condition'].isin(selected_condition)) &
    (df_long['treatment'].isin(selected_treatment)) & 
    (df_long['sample_type'].isin(selected_tissue)) &
    (df_long['time_from_treatment_start'].isin(selected_times)) &
    (df_long['response'].isin(selected_response)) &
    (df_long['sex'].isin(selected_sex))
]

#main
if df_filtered.empty:
    st.warning("No data matches these filters. Please adjust the sidebar.")
else:
    
    #quick stats
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_samples = df_filtered['sample'].nunique()
    responders = df_filtered[df_filtered['response'] == 'yes']['sample'].nunique()
    non_responders = df_filtered[df_filtered['response'] == 'no']['sample'].nunique()
    male = df_filtered[df_filtered['sex'] == 'M']['sample'].nunique()
    female = df_filtered[df_filtered['sex'] == 'F']['sample'].nunique()
    
    col1.metric("Total Samples", total_samples)
    col2.metric("Responders", responders)
    col3.metric("Non-Responders", non_responders)
    col4.metric('Males', male)
    col5.metric('Females', female)

    st.divider() #spacing

    #boxplot
    st.subheader("Relative Frequency: Responders vs Non-Responders")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(
        data=df_filtered, x='population', y='percentage', hue='response',
        palette={'yes': 'mediumseagreen', 'no': 'indianred', 'None' : 'gray'}, ax=ax #added None for multiselect
    )
    ax.set_ylabel('Relative Frequency (%)')
    ax.set_xlabel('Cell Population')
    st.pyplot(fig)  #streamlit plot in middle

    st.divider() #spacing

    #stats
    st.subheader("Statistical Significance (Mann-Whitney U)")
    
    populations = df_filtered['population'].unique()
    stats_records = []
    
    for pop in populations:
        res_data = df_filtered[(df_filtered['population'] == pop) & (df_filtered['response'] == 'yes')]['percentage']
        non_data = df_filtered[(df_filtered['population'] == pop) & (df_filtered['response'] == 'no')]['percentage']
        #split by response --> y/n

        if len(res_data) > 0 and len(non_data) > 0:
            stat, p_value = mannwhitneyu(res_data, non_data, alternative='two-sided')
            stats_records.append({
                'Population': pop,
                'P-Value': f"{p_value:.4f}",
                'Mean Responder (%)': f"{res_data.mean():.2f}",
                'Mean Non-Responder (%)': f"{non_data.mean():.2f}",
                'Significance': '*' if p_value < 0.05 else ''
            })
            
    if stats_records:
        st.dataframe(pd.DataFrame(stats_records), use_container_width=True) #show stats
    
    #downlaod button
    csv = df_filtered.to_csv(index=False, header = True).encode('utf-8')
    st.download_button(
        label="Download Filtered Data (with current selections) as CSV",
        data=csv,
        file_name='filtered_clinical_data.csv',
        mime='text/csv',
    )