# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 14:48:01 2023

@author: linfra
"""

import pandas as pd
import numpy as np
from scipy import stats


patientNumbers_c = [1,3,4,7,8,12,16,17]
# patientNumbers_wc = ['2','5','6','13','14','15']
structureNames = ['heart','tricuspidalvalve','superiorvenacava', 'rightventricle', 'rightcoronararte', 'rightatrium', 'pulmonicvalve', 'pulmonaryartery', 'pericard', 'nodesinus', 'nodeav', 'mitralvalve', 'leftventricle', 'leftmaincoartery', 'leftcircumflex', 'leftatrium', 'leftantdescarter', 'inferiorvenacava', 'aorticvalve', 'aorta']                  
comparisonNames = ["Contrast", "Week 1"]

column_names = ["Patient", "Slice number", "Structure", "Comparison", "DICE", "HD95", "MSD", "VS", 'HD']
df = pd.DataFrame(columns=column_names)

done = ['1','2','3','4','5','6','7','8','11','12','13','14','15','16','17']

# only takes with 3D for patient 1,m that is missing 6D
for patientNumberDf in done:
    if patientNumberDf != '1':
        patientNumberDf = pd.read_csv(f"{patientNumberDf}/Output/indices{patientNumberDf}.csv", sep = ';', decimal = ',')
        patientNumberDf = patientNumberDf[patientNumberDf.Comparison != 'Week 1 3D']
        df = pd.concat([df, patientNumberDf], axis=0, ignore_index=True)
    else:
        patientNumberDf = pd.read_csv(f"{patientNumberDf}/Output/indices{patientNumberDf}.csv", sep = ';', decimal = ',')
        df = pd.concat([df, patientNumberDf], axis=0, ignore_index=True)
    
# replaces column name for Week 1, so that they have the same value, even though they had different transfers
df = df.drop(df.columns[-1], axis = 1)
df = df.replace('Week 1 3D', 'Week 1')
df = df.replace('Week 1 6D', 'Week 1')

#removes outliers, by computing z-score
df = df[(np.abs(stats.zscore(df['HD95'])) < 3)]
    
df.to_csv("DataFrames/FULLcombindedDF.csv", sep=";", decimal=",")  

# removes the columns that we are not interested in further
df_smaller = df[df.columns[~df.columns.isin(['HD', 'MSD', 'VS', 'Slice number'])]]


# aggs = ['mean', 'median', 'min', 'max', 'sum']
aggs = ['mean', 'median']
metrics = ['DICE', 'HD95']


for agg in aggs:
    aggregation_functions = {'DICE':agg,'HD95':agg}
    df_agg = df.groupby(['Structure','Comparison', 'Patient']).aggregate(aggregation_functions)
    #df_agg.to_csv(f"DataFrames/combindedDF_{agg}.csv", sep=";", decimal=",", na_rep = '0')
    
    #for mean, calculate variance and standard deviation:
    if agg == aggs[0]:
        # calculate variance
        var_functions = {'DICE':np.var,'HD95':np.var}
        df_var = df.groupby(['Structure','Comparison', 'Patient']).aggregate(var_functions)
        df_var = df_var.rename(columns = {'DICE':'DICE_var','HD95':'HD95_var'})
        df_agg_var_std = pd.merge(df_agg, df_var, on=['Structure','Comparison', 'Patient'])
        
        # calculate standard deviation
        std_functions = {'DICE':np.std,'HD95':np.std}
        df_std = df.groupby(['Structure','Comparison', 'Patient']).aggregate(std_functions)
        df_std = df_std.rename(columns = {'DICE':'DICE_std','HD95':'HD95_std'})
        df_agg_var_std = pd.merge(df_agg_var_std, df_std, on=['Structure','Comparison', 'Patient'])
        
        df_agg.to_csv(f"DataFrames/combindedDF_{agg}.csv", sep=";", decimal=",", na_rep = '0')
        df_agg_var_std.to_csv(f"DataFrames/combindedDF_{agg}_variance.csv", sep=";", decimal=",", na_rep = '0') 
        
        # save in wanted format - dice and hd95 with only contrast and uncertainties:
        for metric in metrics:
            df_metric_var = df_agg_var_std
            df_metric_var = df_metric_var.pivot_table(values=[metric,f'{metric}_var',f'{metric}_std'], index=['Structure', 'Patient'], columns='Comparison', aggfunc='first')
            
            # contrast:
            df_metric_var_c = df_metric_var.drop(df_metric_var.columns[[-1,-3,-5]], axis = 1) #removes week1 columns
            df_metric_var_c = pd.concat([df_metric_var_c[metric].dropna(), df_metric_var_c], axis=1, ignore_index=False, join = 'inner')
            df_metric_var_c = df_metric_var_c.drop(df_metric_var_c.columns[-3], axis = 1) #removes double metric columns
            df_metric_var_c = df_metric_var_c.rename(columns = {df_metric_var_c.columns[0]:f'c_{metric}', df_metric_var_c.columns[1]:f'c_{metric}_std', df_metric_var_c.columns[2]:f'c_{metric}_var'})
            df_metric_var_c.to_csv(f"DataFrames/Tests/withUncertainties/{metric}_{agg}_contrast_var.csv", sep=";", decimal=",", na_rep = np.nan) 
            # week 1:
            df_metric_var_w1 = df_metric_var.drop(df_metric_var.columns[[-2,-4,-6]], axis = 1) #removes contrast columns
            df_metric_var_w1.to_csv(f"DataFrames/Tests/withUncertainties/{metric}_{agg}_week1_var.csv", sep=";", decimal=",", na_rep = np.nan) 
            # both:
            df_metric_var_both  = pd.concat([df_metric_var_c, df_metric_var_w1], axis=1, ignore_index=False, join = 'inner')
            df_metric_var_both = df_metric_var_both.rename(columns = {df_metric_var_both.columns[-3]:f'w1_{metric}', df_metric_var_both.columns[-2]:f'w1_{metric}_std', df_metric_var_both.columns[-1]:f'w1_{metric}_var'})
            df_metric_var_both.to_csv(f"DataFrames/Tests/withUncertainties/{metric}_{agg}_contrast&week1_var.csv", sep=";", decimal=",", na_rep = np.nan) 
            # both without uncertainties:
            df_metric_both  = df_metric_var_both.drop(df_metric_var_both.columns[[-1,-2,-4,-5]], axis = 1) #removes uncertainties
            df_metric_both.to_csv(f"DataFrames/Tests/{metric}_{agg}_contrast&week1.csv", sep=";", decimal=",", na_rep = np.nan) 
    
    
    #for median, calculate interquartile range:
    elif agg == aggs[1]:
        
        column_names_iqr = ["Patient", "Structure", "Comparison", "DICE", "DICE_iqr", "HD95", "HD95_iqr"]
        df_median = pd.DataFrame(columns=column_names_iqr)
        
        for structure in structureNames:
            for comparison in comparisonNames:
                for patient in patientNumbers_c:
                        subset = df_smaller[df_smaller['Patient'] == patient]
                        subsubset = subset[subset['Comparison'] == comparison]
                        subsubsubset = subsubset[subsubset['Structure'] == structure]

                        # some structures are missing dice values if there was no overlap, but the program must go on
                        if subsubsubset.empty:
                            continue
                        # calculates IQR for DICE and HD95   
                        iqr_d = np.quantile(subsubsubset['DICE'], 0.75) - np.quantile(subsubsubset['DICE'], 0.25)
                        iqr_h = np.quantile(subsubsubset['HD95'], 0.75) - np.quantile(subsubsubset['HD95'], 0.25)
                        
                        # adds to new dataframe
                        new_row = {"Structure": structure, "Comparison": comparison, "Patient": patient, "DICE": subsubsubset['DICE'].median(), "DICE_iqr": iqr_d, "HD95": subsubsubset['HD95'].median(), "HD95_iqr":iqr_h}
                        df_median = pd.concat([df_median, pd.DataFrame([new_row])], axis=0, ignore_index=True)
                        
        df_agg.to_csv(f"DataFrames/combindedDF_{agg}.csv", sep=";", decimal=",", na_rep = '0')
        df_median.to_csv(f"DataFrames/combindedDF_{agg}_iqr.csv", sep=";", decimal=",", na_rep = '0')
        
        # save in wanted format - dice and hd95 with only contrast and uncertainties:
        for metric in metrics:
            df_metric_iqr = df_median
            df_metric_iqr = df_metric_iqr.pivot_table(values=[metric,f'{metric}_iqr'], index=['Structure', 'Patient'], columns='Comparison', aggfunc='first')
            #contrast:
            df_metric_iqr_c = df_metric_iqr.drop(df_metric_iqr.columns[[-1,-3]], axis = 1) #removes week1
            df_metric_iqr_c.to_csv(f"DataFrames/Tests/withUncertainties/{metric}_{agg}_contrast_iqr.csv", sep=";", decimal=",", na_rep = np.nan) 
            #week 1:
            df_metric_iqr_w1 = df_metric_iqr.drop(df_metric_iqr.columns[[-2,-4]], axis = 1) #removes contrast
            df_metric_iqr_w1.to_csv(f"DataFrames/Tests/withUncertainties/{metric}_{agg}_week1_iqr.csv", sep=";", decimal=",", na_rep = np.nan)    
            
            # if other metrics added - without uncertainties
    else:
        df_agg.to_csv(f"DataFrames/combindedDF_{agg}.csv", sep=";", decimal=",", na_rep = '0')
    
    
    # export to do statistical testing / illustrations:

    for metric in metrics:
        
        df_metric = df_agg
        df_metric = df_metric.pivot_table(values=metric, index=['Structure', 'Patient'], columns='Comparison', aggfunc='first')
        
        # only contrast: 
        df_metric_c = df_metric.drop(df_metric.columns[-1:], axis = 1) # removes week 1 column
        df_metric_c = df_metric_c.dropna() # removes week 1 rows
        df_metric_c = df_metric_c.rename(columns = {'Contrast':metric})
        df_metric_c.to_csv(f"DataFrames/Tests/{metric}_{agg}_contrast.csv", sep=";", decimal=",", na_rep = np.nan) 
        
        # only week 1:
        df_metric_w1 = df_metric.drop(df_metric.columns[-2], axis = 1) # removes contrast column
        df_metric_w1 = df_metric_w1.rename(columns = {'Contrast':metric})
        df_metric_w1.to_csv(f"DataFrames/Tests/{metric}_{agg}_week1.csv", sep=";", decimal=",", na_rep = np.nan) 