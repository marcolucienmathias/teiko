import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu


conn = sqlite3.connect("research_data.db") #open

query = "SELECT * FROM project_data" #get

df = pd.read_sql_query(query, conn)

conn.close()

cell_cols = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte'] #5 cells

def rowsum(x):
    return sum([x['b_cell'], x['cd8_t_cell'], x['cd4_t_cell'], x['nk_cell'], x['monocyte']])

def indiv_cell_generator(x, cell_cols): #generator to split into individual cell_types per sample
    for _, x in df.iterrows():

        cell_tot = rowsum(x)

        for cell_type in cell_cols:
            yield {'sample' : x['sample'], 'total_count' : cell_tot, 'population' : cell_type, 'count' : x[cell_type], 'percentage' : 100 * (x[cell_type] / cell_tot)}

df_out = pd.DataFrame(indiv_cell_generator(df,cell_cols))

print(df_out) #generate summary table
df_out.to_csv('relative_frequencies_table.csv', index=False)


### Q3:

#ONLY INCLUDE PBMC SAMPLES:

df_out_3 = df_out.merge(df[['sample', 'sample_type', 'response', 'treatment', 'condition']], how = 'left', on = 'sample')
df_out_3 = df_out_3[(df_out_3['sample_type'] == 'PBMC') & (df_out_3['condition'] == 'melanoma') & (df_out_3['treatment'] == 'miraclib')]
## FILTER FOR PMBC, MELANOMA, MIRACLIB

#make responders
responders = df_out_3[df_out_3['response'] == 'yes']
#make nonresponders
nonresponders = df_out_3[df_out_3['response'] == 'no']

plt.figure(figsize=(12, 6))
#predefine fig

sns.boxplot(
    data=df_out_3, #combined df
    x='population', #cell_type
    y='percentage', #rel freq
    hue='response', 
    palette={'yes': 'green', 'no': 'red'}
)

plt.title('Cell Type Specific Relative Frequencies: Melanoma Patients Taking Miraclib, Responders vs Non-Responders (PBMC)')
plt.ylabel('Relative Frequency (%)')
plt.xlabel('Cell Type')
plt.legend(title='Response')
plt.tight_layout()

plt.savefig('relfreq_plot.png', dpi=300, bbox_inches = 'tight')

plt.show(block=False)


populations = df_out_3['population'].unique()

print("Statistical Significance Test (Mann-Whitney U):")

print("-" * 50) #formatting

significant_populations = []
stats_records = []

for pop in populations:

    responder_data = responders[responders['population'] == pop]['percentage']
    nonresponder_data = nonresponders[nonresponders['population'] == pop]['percentage']
    
  
    stat, p_value = mannwhitneyu(responder_data, nonresponder_data, alternative='two-sided')

    stats_records.append(
        {"cell_type": pop,
            "u_statistic": stat,
            "p_value": p_value,
            "statistically_significant": "YES" if p_value < 0.05 else "NO"})
    
    #formatting for sig.

    sig_marker = "*" if p_value < 0.05 else ""
    print(f"{pop:<15} p-value = {p_value:.4e} {sig_marker}")
    
    if p_value < 0.05:
        significant_populations.append(pop)

print("-" * 50) #end formatting
 
df_stats = pd.DataFrame(stats_records)
df_stats.to_csv("clinical_trial_statistics.csv", index=False) #save to root


