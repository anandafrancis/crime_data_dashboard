#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: dashboard.py
@author: laasyapothuganti & anandafrancis
"""

# import necessary libraries
import dash
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output
import sankey as ms
from plotly.subplots import make_subplots
from crime_dash_library import CrimeReport




def main():
    
    # intialize object
    cr = CrimeReport()
    
    # load all csvs into class
    for num in range(15,23):
        cr.load_report(f'crime_20{num}.csv')
        
    # clean dataframe
    cr.clean_data(title_case_cols=['offense_code_group', 'street'],
              no_nan_cols=['street', 'offense_code_group', 'district'], 
              del_cols=['reporting_area', 'occurred_on_date', 'ucr_part', 'location'])
    
    # group dataframe by year and offense
    crime_year_offense = cr.data.groupby(['year', 'offense_code_group']).count()
    
    # obtain list of offenses, street names (for dropdown elements)
    # order lists in alphabetical order
    # add all option to lists
    offense = cr.data['offense_code_group'].unique().tolist()
    offense = sorted(offense)
    offense.insert(0, "All Offense Code Groups")
    street = cr.data['street'].unique().tolist()
    street = sorted(street)
    street.insert(0, "All Streets")
    
    
    app = Dash(__name__)
    
    app.layout = html.Div(
        children=[
            # add title
            html.H1(children="Boston Crime Analytics",
                    style = {"color": "black", "fontSize": "48px", "fontWeight": "bold", "textAlign": "center", "margin": "auto"}
            ),
            # add header
            html.P(
                children="Analyze the types of crimes and the number of crimes committed in Boston from August 2015 to April 2022 on a yearly, monthly, daily, and hourly basis and at a street level",
                style = {"color": "black", "textAlign": "center", "margin": "4px auto", 'maxWidth': '384px'}
            ),
            # add year slider
            html.Div(children="Year", className="menu-title"),
            dcc.Slider(
                id='year-slider', 
                value=2015, 
                min=2015, 
                max=2022, 
                step=1,
                marks={'2015': '2015',
                       '2016': '2016',
                       '2017': '2017',
                       '2018': '2018',
                       '2019': '2019',
                       '2020': '2020',
                       '2021': '2021',
                       '2022': '2022'},
            ),
            # add break
            html.Br(),
            # add offense code group multi-value dropdown
            html.Div(children="Offense Code Group", className="menu-title"),
            dcc.Dropdown(
                id="offense-filter",
                options=offense,
                value="All Offense Code Groups",
                multi = True,
                clearable=False,
                style = dict(width='50%'),
                ),
            # add break
            html.Br(),
            # add map scatter plot
            html.Div(
                children=dcc.Graph(
                    id="graph-chart", config={"displayModeBar": False},
                ),
                className="card",
            ),
            # add bar chart
            html.Div(
                children=dcc.Graph(
                    id="bar-chart", config={"displayModeBar": False}
                ),
                className="card",
            ),
            # add suplots of line graphs
            html.Div(
                children=dcc.Graph(
                    id="line-chart", config={"displayModeBar": False}
                ),
                className="card",
            ),
           # add break
            html.Br(),
            # add street multi-value dropdown
            html.Div(children="Street", className="menu-title"),
            dcc.Dropdown(
                id="street-filter",
                options=street,
                value="All Streets",
                multi = True,
                clearable=False,
                style = dict(width='50%'),
                ),
            # add offense code group multi-value dropdown
            html.Div(children="Crime", className="menu-title"),
            dcc.Dropdown(
                id="crime-filter",
                options=offense,
                value="All Offense Code Groups",
                multi = True,
                clearable=False,
                style = dict(width='50%'),
                ),
            # add sankey diagram
            html.Div(
                children=dcc.Graph(
                    id="street_chart", config={"displayModeBar": False}
                ),
                className="card",
            ),
            html.Div(children="Minimum Crimes", className="menu-title"),
            dcc.Slider(0, 100, 5, value=15, id='count-slider'
            ),
        ],
    )
    
    @app.callback(
        Output("graph-chart", "figure"),
        Output("bar-chart", "figure"),
        Output("line-chart", "figure"),
        Output("street_chart", "figure"),
        Input("year-slider", "value"),
        Input("offense-filter", "value"),
        Input("street-filter", "value"),
        Input("crime-filter", "value"),
        Input("count-slider", "value")
        )
    def update_charts(year, offense, street, crime, count):
        
        # Initial Data Clean/Data Prep
        # convert year to integer
        # filter DataFrame to year selected
        year = int(year)
        year_bool = cr.data['year'] == year
        crime_ybool = cr.data.loc[year_bool,:]
        
        # convert offense code groups to list for all filter in map plot
        offenses = crime_ybool['offense_code_group'].unique().tolist()
       
        # filter grouped year/offense DataFrame by year selected
        crime_obool = crime_year_offense.loc[year]
        
        
        
        # Street to Crime Sankey Diagram
        # return non-updated dashboard when nothing is selected in filter
        if len(street) == 0:
            return dash.no_update
        
        elif isinstance(street, str):
            # keep all streets in DataFrame if all filter is selected
            if street == "All Streets":
                crime_sankey = crime_ybool
            # keep only relevant street in DataFrame if single street is selected
            else:
                crime_sankey = crime_ybool[crime_ybool["street"] == street]
        
        elif isinstance(street, list):
            # keep all streets in DataFrame if all filter is selected
            if "All Streets" in street:
                crime_sankey = crime_ybool
            # keep only relevant streets in DataFrame if multiple streets are selected
            else:
                crime_sankey = crime_ybool[crime_ybool["street"].isin(street)]
        
        # return non-updated dashboard when nothing is selected in filter
        if len(crime) == 0:
            return dash.no_update
        
        elif isinstance(crime, str):
            # keep all offense code groups in DataFrame if all filter is selected
            if crime == "All Offense Code Groups":
                crime_sankey = crime_sankey
            # keep only relevant offense code group in DataFrame if single offense code group is selected
            else:
                crime_sankey = crime_sankey[crime_sankey["offense_code_group"] == crime]
        
        elif isinstance(crime, list):
            # keep all offense code groups in DataFrame if all filter is selected
            if "All Offense Code Groups" in crime:
                crime_sankey = crime_sankey
             # keep only relevant offense code groups in DataFrame if multiple offense code groups are selected
            else:
                crime_sankey = crime_sankey[crime_sankey["offense_code_group"].isin(crime)]

        
        # group DataFrame by street and offense code group
        # sort values in descending order
        # filter DataFrame by count
        # create Sankey diagram
        # source used: https://github.ccs.neu.edu/rachlin/ds3500_sp22
        crime_sankey = crime_sankey.groupby(['street', 'offense_code_group']).size().reset_index(name='count')
        crime_sankey = crime_sankey.sort_values('count', ascending=False)
        crime_sankey = crime_sankey[crime_sankey["count"] >= count]
        street_chart = ms.make_sankey(crime_sankey, 'street', 'offense_code_group', 'count')
        
        
        
        # Map Scatter Plot/Bar Chart/Line Chart Subplots
        # return non-updated dashboard when nothing is selected in filter
        if len(offense) == 0:
            return dash.no_update
        
        elif isinstance(offense, str):
            # plot all offenses when all filter is selected
            # keep all offense code groups in DataFrame when all filter is selected
            if offense == "All Offense Code Groups":
                graph_chart = px.scatter_mapbox(crime_ybool[crime_ybool["offense_code_group"].isin(offenses)], lat="lat", lon="long", 
                                                hover_name="incident_number", hover_data=["year", "offense_code_group", "offense_description", 
                                                "district", "street", "datetime"],
                                                color_discrete_sequence=["fuchsia"], zoom=10, height=600)
                crime = crime_ybool
            
            # plot selected single offense
            # keep selected single offense code group in DataFrame
            else:
                graph_chart = px.scatter_mapbox(crime_ybool[crime_ybool["offense_code_group"]==offense], lat="lat", lon="long", 
                                                hover_name="incident_number", hover_data=["year", "offense_code_group", "offense_description", 
                                                "district", "street", "datetime"],
                                                color_discrete_sequence=["fuchsia"], zoom=10, height=600)
                crime = crime_ybool[crime_ybool["offense_code_group"] == offense]
            
            # make string of offense
            offense_str = offense
            
        elif isinstance(offense, list):
            # plot all offenses when all filter is selected
            # keep all offense code groups in DataFrame when all filter is selected
            if "All Offense Code Groups" in offense:
                graph_chart = px.scatter_mapbox(crime_ybool[crime_ybool["offense_code_group"].isin(offenses)], lat="lat", lon="long", 
                                                hover_name="incident_number", hover_data=["year", "offense_code_group", "offense_description", 
                                                "district", "street", "datetime"],
                                                color_discrete_sequence=["fuchsia"], zoom=10, height=600)
                crime = crime_ybool
            
            # plot selected multiple offenses
            # keep selected multiple offense code groups in DataFrame
            else:
                graph_chart = px.scatter_mapbox(crime_ybool[crime_ybool["offense_code_group"].isin(offense)], lat="lat", lon="long", 
                                                hover_name="incident_number", hover_data=["year", "offense_code_group", "offense_description", 
                                                "district", "street", "datetime"],
                                                color_discrete_sequence=["fuchsia"], zoom=10, height=600)
                crime = crime_ybool[crime_ybool["offense_code_group"].isin(offense)]
            
            # make string of offenses
            offense_str = ""
            for o in offense[:-1]:
                offense_str += f"{o}, "
            offense_str += offense[-1]
            
        # update map plot layout style and margins
        graph_chart.update_layout(mapbox_style="open-street-map")
        graph_chart.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        
        # create grouped DataFrames by month, hour, and day
        crime_month = crime.groupby("month").count()
        cats = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        crime_day = crime.groupby(["day_of_week"]).count().reindex(cats) 
        crime_hour = crime.groupby("hour").count()
        
        # plot bar chart of offense code groups and number of incidents for selected year
        # add title, x-axis label, y-axis label
        bar_chart = px.bar(crime_obool, x=crime_obool.index, y=crime_obool["incident_number"])
        bar_chart.update_layout(height = 600, title_text=f"Number of Incidents for Each Offense Code Group in {year}", xaxis={'categoryorder':'total descending'})
        bar_chart.update_xaxes(title_text="Offense Code Group")
        bar_chart.update_yaxes(title_text='Number of Incidents')
        
        # produce 3 subplots for month, day, and hour DataFrame data
        # add subtitles
        line_chart = make_subplots(rows=1, cols=3, subplot_titles=("Number of Incidents by Month", "Number of Incidents by Day", "Number of Incidents by Hour"))
        
        # plot month with number of incidents 
        line_chart.add_trace(
            go.Scatter(x=crime_month.index, y=crime_month['incident_number']),
            row=1, col=1
        )
        # plot day wit number of incidents
        line_chart.add_trace(
            go.Scatter(x=crime_day.index, y=crime_day['incident_number']),
            row=1, col=2
        )
        # plot hour with number of incidents
        line_chart.add_trace(
            go.Scatter(x=crime_hour.index, y=crime_hour['incident_number']),
            row=1, col=3
        )
        
        # add title, x-axis labels, y-axis label
        line_chart.update_layout(title_text=f"Number of Incidents for {offense_str} by Month, Day, and Hour in {year}", showlegend=False)
        line_chart.update_yaxes(title_text='Number of Incidents', row=1, col=1)
        line_chart.update_xaxes(title_text='Month', row=1, col=1)
        line_chart.update_xaxes(title_text='Day', row=1, col=2)
        line_chart.update_xaxes(title_text='Hour', row=1, col=3)
                
        
        
        return graph_chart, bar_chart, line_chart, street_chart
    
    app.run_server(debug=True)
    
if __name__ == '__main__':
    main()

