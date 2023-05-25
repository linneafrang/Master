# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 15:33:47 2023

@author: linfra
"""
import pandas as pd
import numpy as np

structureNames = ['heart', 'tricuspidalvalve', 'superiorvenacava','rightventricle', 'rightcoronararte', 'rightatrium', 'pulmonicvalve', 'pulmonaryartery', 'pericard', 'nodesinus',
                  'nodeav', 'mitralvalve', 'leftventricle', 'leftmaincoartery', 'leftcircumflex', 'leftatrium', 'leftantdescarter', 'inferiorvenacava', 'aorticvalve', 'aorta']
structureNames_c = []
for structureName in structureNames:
    structureNames_c.append(f'{structureName}+k')

df = pd.read_csv("01dvhValuesx_cleaned_new.csv", sep=';', decimal=',')


# sets up empty dataframes:
column_names = ["Patient", 'Plan', "Comparison", "Structure", "Volume"]
df_plan = pd.DataFrame(columns=column_names)
df_contrast = pd.DataFrame(columns=column_names)
df_w1 = pd.DataFrame(columns=column_names)

df['Structure'] = df['Structure'].apply(str.lower)
        
for index,row in df.iterrows():
    if row['Structure'] in structureNames:
        if row['Plan'] == 'FB':
            new_row = {'Patient': row['Patient'], 'Plan': row['Plan'], 'Comparison': 'Plan',  'Structure': row['Structure'], 'Volume': row['Volume']}
            df_plan = pd.concat([df_plan, pd.DataFrame([new_row])], axis=0, ignore_index=True)

        elif row['Plan'] == 'FB_w1':
            new_row = {'Patient': row['Patient'], 'Plan': row['Plan'], 'Comparison': 'Week 1',  'Structure': row['Structure'], 'Volume': row['Volume']}
            df_w1 = pd.concat([df_w1, pd.DataFrame([new_row])], axis=0, ignore_index=True)
            
    elif row['Structure'] in structureNames_c:
        new_row = {'Patient': row['Patient'], 'Plan': row['Plan'], 'Comparison': 'Contrast',  'Structure': row['Structure'][:-2], 'Volume': row['Volume']}
        df_contrast = pd.concat([df_contrast, pd.DataFrame([new_row])], axis=0, ignore_index=True)
        
df_plan = df_plan.drop('Plan', axis = 1)
df_w1 = df_w1.drop('Plan', axis = 1)
df_contrast = df_contrast.drop('Plan', axis = 1)

# turn tables around to useful format
df_comp_c_plan_w1 = pd.concat([df_plan, df_contrast, df_w1])
df_comp_c_plan_w1 = df_comp_c_plan_w1.pivot_table(values='Volume', index=['Structure', 'Patient'], columns='Comparison', aggfunc='first')
df_comp_c_plan_w1.to_csv("02FullVolumePlanAndContrastAndWeek1.csv", sep=";", decimal=",", na_rep = np.nan)