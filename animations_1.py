#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 22:21:43 2022

@author: anandafrancis
"""

from crime_dash_library import CrimeReport
import plotly.express as px
import random as r

# intialize class
cr = CrimeReport()

# load all csvs into class
for num in range(15,23):
    cr.load_report(f'crime_20{num}.csv')

# clean dataframe
cr.clean_data(title_case_cols=['offense_code_group', 'street'],
          no_nan_cols=['street', 'offense_code_group', 'district'], 
          del_cols=['reporting_area', 'occurred_on_date', 'ucr_part', 'location'])

# choose random offense code group to make visualization
offense = r.choice(cr.data['offense_code_group'].unique())

# load mapbox key for visualizations 
act = 'pk.eyJ1IjoiYW5hbmRhZnJhbmNpcyIsImEiOiJjbDJldDk4NW0wM3lkM2tubHhkMjhhN254In0.MCN_0yxCGqGSNI6n121X0w'
px.set_mapbox_access_token(act)

year_animation = px.scatter_mapbox(data_frame=cr.data[cr.data["offense_code_group"]==offense].sort_values('year'), 
                               lat='lat', lon='long', animation_frame='year', color='district', 
                               title=f'{offense} Occurences by Year from 2015 to 2022')
                
month_aniamtion = px.scatter_mapbox(data_frame=cr.data[cr.data["offense_code_group"]==offense].sort_values('mon_yr'), 
                               lat='lat', lon='long', animation_frame='mon_yr', color='district', 
                               title=f'{offense} Occurences by Month from Aug 2015 to Apr 2022')
                
day_animation = px.scatter_mapbox(data_frame=cr.data[cr.data["offense_code_group"]==offense].sort_values('day_mon_yr'), 
                               lat='lat', lon='long', animation_frame='day_mon_yr', color='district', 
                               title=f'{offense} Occurences by Day from June 1, 2015 to April 20, 2022')

year_animation.show()
month_animation.show()
day_animation.show()