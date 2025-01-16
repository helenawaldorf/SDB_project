# further data cleaning

import pandas as pd

# comma to point replacment 
berlin_demo_data = pd.read_csv('data/preprocessed_data/berlin_districts_demographics_translated.csv')
berlin_employ_data = pd.read_csv('data/preprocessed_data/berlin_districts_employment_translated.csv')

for column in berlin_demo_data.select_dtypes(include=['object']).columns:
    berlin_demo_data[column] = berlin_demo_data[column].str.replace(',', '.')
    
for column in berlin_employ_data.select_dtypes(include=['object']).columns:
    berlin_employ_data[column] = berlin_employ_data[column].str.replace(',', '.')

merged_berlin_data = pd.merge(berlin_demo_data, berlin_employ_data, on = 'district_name', how ='inner')

berlin_demo_data.to_csv('data/preprocessed_data/berlin_districts_demographics_translated_modified.csv', index=False)
berlin_employ_data.to_csv('data/preprocessed_data/berlin_districts_employment_translated_modified.csv', index=False)
merged_berlin_data.to_csv('data/preprocessed_data/berlin_districts_data.csv', index=False)

# excel to csv 
hamburg_data = pd.read_excel('data/preprocessed_data/hamburg_districts_data_translated.xlsx')
hamburg_data.to_csv('data/preprocessed_data/hamburg_districts_data_translated.csv', index=False)