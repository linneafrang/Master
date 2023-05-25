# -*- coding: utf-8 -*-
"""
Created on Thu May  4 16:30:54 2023

@author: linfra
"""

import pandas as pd
import numpy as np

# photon:
df_photon = pd.read_csv("dvhValues2104.csv", sep=';', decimal=',')
df_photon = df_photon.drop(['V30%', 'Unnamed: 0', 'Cohort', 'ECLIPSEMinDose [Gy]', 'ECLIPSEVolume [cc]'], axis=1)

column_names = df_photon.columns.values.tolist()
values_names = column_names[3:]
# changes rows to columns
df_pivot_photon = df_photon.pivot_table(values=values_names, index=['Name', 'Structure'], columns='Plan', aggfunc='first')
df_pivot_photon.columns = df_pivot_photon.columns.to_flat_index()
df_pivot_photon['Beam'] = 'Photon'
df_pivot_photon.to_csv("export/PhotonDVH-plans-in-separate-columns.csv", sep=";", decimal=",")

#proton:
df_proton = pd.read_csv("dvhValuesRaystation.csv", sep=';', decimal=',',  encoding='cp1252')
df_proton = df_proton.drop(['Unnamed: 0', 'Cohort', 'ECLIPSEMinDose [Gy]', 'ECLIPSEMeanDose [Gy]', 'ECLIPSEMaxDose [Gy]', 
                            'ECLIPSEVolume [cc]'], axis=1)
df_proton['Plan'] = df_proton['Plan'].replace({'autoFB(AIP_plan)':'FB', 'autoFB(AIP_uke1)':'FB_w1'})

column_names = df_proton.columns.values.tolist()
values_names = column_names[3:]
# sepeartes plans:
df_pivot_proton = df_proton.pivot_table(values=values_names, index=['Name', 'Structure'], columns='Plan', aggfunc='first')
df_pivot_proton.columns = df_pivot_proton.columns.to_flat_index()
df_pivot_proton['Beam'] = 'Proton'

#imports Dmean for proton from Raystation seperately
df_dmean_proton =  pd.read_csv("RaystationDmean.csv", sep=';', decimal=',', encoding= 'unicode_escape')
# removes empty columns
df_dmean_proton = df_dmean_proton[['Name', 'Structure', 'AplanDmean', 'CplanDmean', 'Aw1Dmean']]
df_dmean_proton['Beam'] = 'Proton'

# reimports photon pivot to have without index
df_photon_new = pd.read_csv("PhotonDVH-plans-in-separate-columns.csv", sep=';', decimal=',')
df_photon_new2 = df_photon_new.iloc[:,[6,7,-1]]
# concat
df_combine_photon_proton = pd.concat([df_dmean_proton, df_photon_new2], axis = 1)
df_combine_photon_proton = df_combine_photon_proton.drop(['Beam'], axis = 1)
df_combine_photon_proton.to_csv("export/Photon-Proton-DVH-plans-in-separate-columns.csv", sep=";", decimal=",")

#calculate difference (in percent) photon to proton
df_combine_photon_proton2 = df_combine_photon_proton.groupby(['Structure']).aggregate('median').reset_index()
df_combine_photon_proton2 = df_combine_photon_proton2.iloc[:,[0,2,5]]
df_combine_photon_proton2 = df_combine_photon_proton2.rename(columns = {'AplanDmean': 'ProtonDmean', "('ECLIPSEMeanDose [Gy]', 'FB')":'PhotonDmean'})
df_diff = pd.DataFrame(columns = ['Structure', 'PhotonDmean','ProtonDmean', 'Diff'])

for index, row in df_combine_photon_proton2.iterrows():
    photon = row['PhotonDmean']
    proton = row['ProtonDmean']
    diff = photon-proton
    diff_p = round(diff/photon *100,1)
    
    new_row = {'Structure': row['Structure'], 'PhotonDmean': photon, 'ProtonDmean': proton,'Diff': diff_p}
    df_diff = pd.concat([df_diff, pd.DataFrame([new_row])], axis=0, ignore_index=True)

#seperate column for Dmean, separeted by Beam column value
df_dmean_proton_aplan = df_dmean_proton.iloc[:, [0,1,2,-1]]
df_photon_new_aplan = df_photon_new.iloc[:,[0,1,6,-1]]
df_photon_new_aplan = df_photon_new_aplan.rename(columns = {"('ECLIPSEMeanDose [Gy]', 'FB')":'AplanDmean'})

df_rows = pd.concat([df_dmean_proton_aplan, df_photon_new_aplan])
df_rows = df_rows.sort_values(['Structure', 'Name'])
df_rows.to_csv("export/Photon-Proton-DVH-plans-in-separate-rows.csv", sep=";", decimal=",")

# create Heart VS sub:
df_dmean_proton = df_dmean_proton.drop(['Beam'], axis = 1)
column_names = df_dmean_proton.columns.values.tolist()
# only Dmean
values_names = column_names[2]
df_pivot_proton_heart = df_dmean_proton.pivot_table(values=values_names, index=['Name'], columns=['Structure'], aggfunc='first')
df_pivot_proton_heart.to_csv("export/HeartVSSub-Proton-DVH-plans-in-separate-columns.csv", sep=";", decimal=",")

# calculate median and IQR for dmean proton:
df_dmean_proton_plan = df_dmean_proton.drop(['Name', 'CplanDmean', 'Aw1Dmean'], axis =1)
median_dmean_proton = df_dmean_proton_plan.groupby(['Structure']).aggregate('median').reset_index()
df_iqr_proton_dmean = pd.DataFrame(columns=['Structure', '(q1 - q3)'])

for col in df_pivot_proton_heart:
    q3 = round(np.quantile(df_pivot_proton_heart[col], 0.75), 2)
    q1 = round(np.quantile(df_pivot_proton_heart[col], 0.25), 2)
    
    new_row = {'Structure':col, '(q1 - q3)': f"({q1}-{q3})" }
    df_iqr_proton_dmean = pd.concat([df_iqr_proton_dmean, pd.DataFrame([new_row])], axis=0, ignore_index=True)
    
#change dmean to lot plan and w1 - one column
#split in two, concat to one column
df_dmean_proton_w1 = df_dmean_proton.drop(['Name', 'CplanDmean', 'AplanDmean'], axis =1)
df_dmean_proton_w1['Plan'] = 'Aw1'
df_dmean_proton_w1 = df_dmean_proton_w1.rename(columns ={'Aw1Dmean':'Dmean'})
df_dmean_proton_plan['Plan'] = 'Aplan'
df_dmean_proton_plan = df_dmean_proton_plan.rename(columns ={'AplanDmean':'Dmean'})
df_dmean_box = pd.concat([df_dmean_proton_plan, df_dmean_proton_w1])
df_dmean_box.to_csv("export/Proton-DVH-plans-in-same-columns.csv", sep=";", decimal=",")

df_dmean_proton.set_index(['Name', 'Structure'], inplace=True)
df_proton_all = pd.concat([df_pivot_proton, df_dmean_proton], axis = 1)
df_proton_all = df_proton_all.drop(['Beam'], axis = 1)
df_proton_all.to_csv("export/Proton-DVH-plans-in-separate-columns.csv", sep=";", decimal=",")

#concat proton and photon, other than dmean
df_pivot_photon = df_pivot_photon.add_suffix('_photon')
df_pivot_proton = df_pivot_proton.add_suffix('_proton')
df_pivot_all = pd.concat([df_pivot_photon, df_pivot_proton], axis = 1)
df_pivot_all.to_csv("export/Proton-Photon-DVH-metrics-in-seperate-columns.csv", sep=";", decimal=",")
df_pivot_all_median = df_pivot_all.groupby(['Structure']).aggregate('median')


#calculate diff photon, precentage reduction
df_photon_new_aplan_heartvssub = df_photon_new_aplan.iloc[:,1:3]
df_photon_new_aplan_heartvssub = df_photon_new_aplan_heartvssub.groupby(['Structure']).aggregate('median').reset_index()
df_photon_new_aplan_heartvssub_diff = pd.DataFrame(columns=['Structure', 'Diff [Gy]', 'Diff [%]'])

for index, row in df_photon_new_aplan_heartvssub.iterrows():
    new = row['AplanDmean']
    heart = df_photon_new_aplan_heartvssub.iloc[2,1]
    diff = new - heart
    diff_p = round(diff/heart *100,1)
    
    new_row = {'Structure': row['Structure'], 'Diff [Gy]': diff, 'Diff [%]': diff_p}
    df_photon_new_aplan_heartvssub_diff = pd.concat([df_photon_new_aplan_heartvssub_diff, pd.DataFrame([new_row])], axis=0, ignore_index=True)
    
#for proton:
df_proton_new_aplan_heartvssub_diff = pd.DataFrame(columns=['Structure', 'Diff [Gy]', 'Diff [%]'])
for index, row in median_dmean_proton.iterrows():
    new = row['AplanDmean']
    heart = median_dmean_proton.iloc[2,1]
    diff = new - heart
    diff_p = round(diff/heart *100,1)
        
    new_row = {'Structure': row['Structure'], 'Diff [Gy]': diff, 'Diff [%]': diff_p}
    df_proton_new_aplan_heartvssub_diff = pd.concat([df_proton_new_aplan_heartvssub_diff, pd.DataFrame([new_row])], axis=0, ignore_index=True)
    
#calculate iqr for v15 and v30
df_iqr_proton_photon = pd.DataFrame(columns=['Metric','Structure', '(q1 - q3)'])
df_pivot_all = df_pivot_all.drop(columns = ['Beam_photon', 'Beam_proton'])


for col in df_pivot_all:
    df_pivot_all2 = pd.DataFrame(df_pivot_all[col])
    df_pivot_all2 = df_pivot_all2.pivot_table(values=col, index=['Name'], columns=['Structure'], aggfunc='first')
    for col2 in df_pivot_all2:
        q3 = round(np.quantile(df_pivot_all2[col2], 0.75), 2)
        q1 = round(np.quantile(df_pivot_all2[col2], 0.25), 2)
    
        new_row = {'Metric': col,'Structure':col2, '(q1 - q3)': f"({q1}-{q3})" }
        df_iqr_proton_photon = pd.concat([df_iqr_proton_photon, pd.DataFrame([new_row])], axis=0, ignore_index=True)