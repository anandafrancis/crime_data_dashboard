"""
Created on Mon Apr 25 07:10:00 2022

@author: anandafrancis
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re

class CrimeReport:
    
    def __init__(self):
        """Constructor"""
        
        # intialize dataframe to merge all registered crime reports to
        self.data = pd.DataFrame()
        
        
    
    def load_report(self, file): 
        ''' 
        Purpose:
            Read csv into pandas dataframe and merge all loaded csv files into one dataframe
        
        Args:
            file (str): name of file user is registering or link to file
        
        Return:
            None, concatenates dataframes
            
        '''
        
        # read csv file
        df = pd.read_csv(file)
        
        # merge pandas with previously loaded csv
        self.data = pd.concat([self.data, df], axis=0)
        
    
    def _assign_offcode_group(self):
        '''
        Purpose:
            for all nan values, assign the appropriate offense group based on offense code of crime
            
        Args:
            None
            
        Return:
            dataframe with no nan values in offense code group
        '''
        
        # create dict with keys as offense code groups and values as list of corresponding codes
        off_codes = {off: list(self.data[self.data.offense_code_group == off].offense_code.unique()) 
                     for off in self.data['offense_code_group'].unique()}
        
        # reverse the dictionary so that keys are the codes and values are its corresponding offense code group 
        pairs = {code: off for off in off_codes.keys() for code in off_codes[off]}
        
        # remove any offense code without offense code group
        self.data = self.data[self.data.offense_code.isin(pairs.keys())]
        
        # mend dataframe
        self.data['offense_code_group'] = self.data.apply(lambda row: pairs[row.offense_code], axis=1)
        
        return self.data
        
    def clean_data(self, lowercase_cols=True, min_lat=42, fix_shootings=True, title_case_cols=[], offcodegroup_needed=True, 
                   no_nan_cols=[], fix_time=True, del_cols=[], fix_streets=True):
        '''
        Purpose:
            for all nan values, assign the appropriate offense group based on offense code of crime
            
        Args:
            lowercase_cols (bool): boolean value indicating to put column names in lowercase
            min_lat (int/float): minimum latitude to remove values not in region
            fix_shootings (bool): boolean value indicating if shootings values need to be standardized
            title_case_cols (list): list of columns to put values in title case
            offcodegroup_needed (bool): boolean value indicating if off code group columns needs to be fixed to remove nan values
            no_nan_cols (list): list of columns to remove nan values
            fix_time (bool): boolean value indicating if time column needs to be translated to datetime object
            del_cols (list): list of columns to remove from dataframe
            fix_streets (bool): boolean value indicating to clean and standardize street names
            
        Return:
            None, cleans dataframe
        '''
        
        # turn all column names to lowercase
        if lowercase_cols == True:
            cols = [col.lower() for col in self.data.columns]
            self.data = self.data.rename(dict(zip(self.data.columns, cols)), axis=1)
            
        # remove incorrect location data
        self.data = self.data[(self.data.lat > min_lat)]
        
        # standardize shooting data
        if fix_shootings == True:
            shoot_dict = {0: 0, 1:1, np.nan:0, 'Y':1}
            self.data['shooting'] = self.data.apply(lambda row: shoot_dict[row['shooting']], axis=1)
         
        # change all capitalized values to title case    
        for col in title_case_cols:
            self.data[col] = self.data[col].str.title()
        
        # remove any data without offense code group
        if offcodegroup_needed == True:
            self.data = CrimeReport._assign_offcode_group(self)
            
        else:
            del_cols.append('offense_code_group')
            
        # drop nan values from "important" columns
        self.data = self.data.dropna(subset=no_nan_cols)
        
        if fix_time == True:
            # turn str of time to datetime object 
            self.data['datetime'] = self.data['occurred_on_date'].apply(lambda x: datetime.fromisoformat(x))
    
            # create time object for month and year only
            self.data['mon_yr'] = self.data.apply(lambda row: str(datetime(month=row['month'], 
                                                                         year=row['year'], day=1)), axis=1)
            # create time object for day, month, year only
            self.data['day_mon_yr']= self.data.apply(lambda row: str(datetime(month=row['month'], day=row['datetime'].day,
                                                                         year=row['year'])), axis=1)

        # remove unneccesary columns
        self.data = self.data.drop(columns=del_cols)
        
        if fix_streets == True:
            # remove zip code, city and state from location
            self.data['street'] = self.data['street'].apply(lambda row: row.split('\n')[0])
            
            # add intersection col
            self.data['intersection'] = self.data['street'].apply(lambda row: bool(re.findall('&', row)))
        
