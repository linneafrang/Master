#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 12:58:21 2023

@author: linneafrang
"""
import pandas as pd
import numpy as np

df = pd.read_csv('FULLcombindedDF.csv', sep=';', decimal=',')

# combine by structure: to calculate mean D and H
df_mean2 = df.groupby(['Structure', 'Comparison'], as_index = False).aggregate({'DICE':'mean', 'HD95':'mean'})
df_mean3 = df.groupby(['Structure', 'Comparison'], as_index = False).aggregate({'DICE':np.std, 'HD95':np.std})
df_mean3 = df_mean3.rename(columns = {'DICE':'Dstd', 'HD95':'Hstd'})
df_mean4 = pd.concat([df_mean2, df_mean3[['Dstd', 'Hstd']]], axis = 1)

df_mean4.to_csv("Filer/Compare.D-H.Cplan.Aw1.Aplan.csv", sep=";", decimal=",")

df_write = df_mean4.pivot_table(values=['DICE', 'HD95', 'Dstd', 'Hstd'], index=['Structure'], columns='Comparison', aggfunc='first')
df_write.columns = df_write.columns.to_flat_index()
df_write.to_csv("Filer/Compare.D-H.Cplan.Aw1.AplanSTD.csv", sep=";", decimal=",")

# combine by structure and patient: mean d and H
df_mean5 = df.groupby(['Structure', 'Comparison', 'Patient'], as_index = False).aggregate({'DICE':'mean', 'HD95':'mean'})
df_mean5_std = df.groupby(['Structure', 'Comparison', 'Patient'], as_index = False).aggregate({'DICE':np.std, 'HD95':np.std})
df_mean5_std = df_mean5_std.rename(columns = {'DICE':'Dstd', 'HD95':'Hstd'})
df_mean5_std = pd.concat([df_mean5, df_mean5_std[['Dstd', 'Hstd']]], axis = 1)

df_mean5_std = df_mean5_std.pivot_table(values=['DICE', 'HD95', 'Dstd', 'Hstd'], index=['Structure', 'Patient'], columns='Comparison', aggfunc='first')
df_mean5_std.columns = df_mean5_std.columns.to_flat_index()
df_mean5_std = df_mean5_std.rename(columns = {('DICE', 'Contrast'):'D.Cplan', ('DICE', 'Week 1'):'DAw1', ('HD95', 'Contrast'):'HCplan', ('HD95', 'Week 1'):'HAw1'})
df_mean5_std = df_mean5_std.rename(columns = {('Dstd', 'Contrast'):'DstdCplan', ('Dstd', 'Week 1'):'DstdAw1', ('Hstd', 'Contrast'):'HstdCplan', ('Hstd', 'Week 1'):'HstdAw1'})

df_mean5_std.to_csv("Filer/Compare.D-H.Cplan.Aw1.Aplan.Patients.csv", sep=";", decimal=",")

df_mean6 = df_mean5.pivot_table(values=['DICE', 'HD95'], index=['Structure', 'Patient'], columns='Comparison', aggfunc='first')
df_mean6.columns = df_mean6.columns.to_flat_index()
df_mean6 = df_mean6.rename(columns  = {('DICE', 'Contrast'):'DCplan', ('DICE', 'Week 1'):'DAw1', ('HD95', 'Contrast'):'HCplan', ('HD95', 'Week 1'):'HAw1'})

# including volume:

df_v = pd.read_csv('Filer/CompareVolumePlanAndContrastAndWeek1.csv', sep=';', decimal=',', index_col = ('Structure', 'Patient'))
df_v = df_v.rename(columns = {'Contrast':'VCplan', 'Plan': 'VAplan', 'Week 1': 'VAw1'})


df_mean7 = pd.concat([df_mean6, df_v], axis =1)

df_mean7.to_csv("Filer/CompareV-D-H.Cplan.Aw1.Aplan.csv", sep=";", decimal=",")