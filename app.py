# -*- coding: utf-8 -*-
# author: Jorge Gomes for VOST Portugal

# PROCIV CHECKER

# ________________________________________
# Import Libraries 
import json
import requests
import pandas as pd 
import datetime as dt 
from datetime import datetime, timedelta, date 
# ________________________________________
# Import Plotly Libraries
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
# _________________________________________
# Import Dash and Dash Bootstrap Components
import dash
import dash_daq as daq
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
# _________________________________________
# INITIAL VARIABLES

# Define Start Date to Today
end_date = dt.datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.today() - timedelta(days=2)).strftime('%Y-%m-%d')
# Define Initial button status
selector = 1
# Define Initial Limit 
limit = 100000

# Define Initial URLs
url_bar = f"https://api.fogos.pt/v2/incidents/search" \
f"?before={end_date}" \
f"&after={start_date}" \
f"&limit={limit}" \
f"&all={selector}" \



# _________________________________________
# GET FIRST JSON DATA and DATA Treatment 

# Get response from URL 
response = requests.get(url_bar)

# Get the json content from the response
json = response.json()

# Create Pandas Dataframe from the normalized json response
# that begins at "data" level. 
# Depending on your json file this may vary. 
# Use print(json) in order to check the  structure of your json fle
df_in = pd.json_normalize(json,'data')

# Create day column by extracting the day from the date column
df_in['day'] = pd.DatetimeIndex(df_in['date']).day
# Convert seconds to Date Time format 
df_in['dateTime.sec'] = pd.to_datetime(df_in['dateTime.sec'], unit='s')

# _________________________________________
# Create Dataframes for the first graphs

df_in_pie = df_in.groupby(['natureza','day','familiaName'],as_index=False)['sadoId'].nunique()
df_in_bar = df_in.groupby(['natureza','date'],as_index=False)['sadoId'].nunique()
df_in_line = df_in.groupby(['dateTime.sec'],as_index=False)['sadoId'].nunique()


# _________________________________________
# DEFINE THE THREE INITIAL GRAPHS 

# Define pie, bar, and line graphs 
fig_pie = px.pie(df_in_pie,names='natureza',values='sadoId',color='natureza',hole=0.5,color_discrete_sequence=px.colors.sequential.Viridis)
fig_bar = px.bar(df_in_bar,x='date',y='sadoId', color='natureza',color_discrete_sequence=px.colors.sequential.Viridis_r,template='plotly_dark')
fig_line = px.line(df_in_line,x='dateTime.sec',y='sadoId', color_discrete_sequence=px.colors.sequential.Viridis_r,template='plotly_dark')

# Styling for graphs

fig_pie.update_traces(textposition='inside', textinfo='value+percent+label')
fig_pie.update_layout(uniformtext_minsize=12, uniformtext_mode='hide',template='plotly_dark')

# _________________________________________
# START DASH APP 

app = dash.Dash(
    external_stylesheets=[dbc.themes.CYBORG],
    #suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)


# START APP LAYOUT 
app.layout = dbc.Container(
    [
        # First Row
        dbc.Row(
            [
                # Ttitle Column 
                dbc.Col(
                    html.H4("VOST PORTUGAL",
                        style={
                            "borderWidth": "1vh",
                            "width": "100%",
                            "background-color":"#353535",
                            "borderColor": "#353535",
                            "opacity": "unset",
                        }
                    ),
                    width={"size": 6},
                ),
                # SUBTITLE (RIGHT) TITLE COLUMN 
                dbc.Col(
                    html.H4("Dashboard Operacional",
                        style={
                            "borderWidth": "1vh",
                            "width": "100%",
                            "background-color":"#BDBBB0",
                            "text-align":"right",
                            "borderColor": "#BDBBB0",
                            "opacity": "unset",
                        }
                    ),
                    width={"size": 6},
                ),
                
            ],
            className="g-0",
        ),  # END OF FIRST ROW 

        # SECOND ROW 
        dbc.Row(
            # HORIZONTAL LINE (NEEDS CSS file in ASSETS FOLDER)
            dbc.Col(
                    html.Hr(
                        style={
                            "borderWidth": "2vh",
                            "width": "100%",
                            "background-color":"#353535",
                            "borderColor": "#CDE6F5",
                            "opacity": "unset",
                        }
                    ),
                    width={"size": 12},
                ),
            ),
        # THIRD ROW 
        dbc.Row(
            [
                dbc.Col(
                    # DATE PICKER 
                    dcc.DatePickerRange(
                        id='date-picker',
                        min_date_allowed=date(1995, 8, 5),
                        max_date_allowed=datetime.today(),
                        initial_visible_month=date(2022, 2, 1),
                        display_format='D/M/Y',
                        start_date=date.today(),
                        end_date=date.today()
                    ),
                width={"size": 2},
                ),
                # TOGGLE SWITCH FOR FIRES
                dbc.Col(
                    
                        html.P("Apenas Inc??ndios"),
                    
                width={"size": 1}
                ),
                dbc.Col(
                    daq.ToggleSwitch(
                            id='fire_switch',
                            vertical=False,
                            size=40,
                            value=False,
                            color="#F8D03D",
                            
                            
                        ), 
                    width={"size": 1}

                    ),
                dbc.Col(
                        html.Div(
                            [
                            html.P("Apenas FMA"),
                            ],style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'right'},
                            ),
                width={"size": 1}
                ),
                
                dbc.Col(
                    daq.ToggleSwitch(
                            id='fma_switch',
                            vertical=False,
                            size=40,
                            value=False,
                            color="#08519C",
                            
                            
                        ), 
                    width={"size": 1}

                    ),
            ],
        ),
        # FOURTH ROW 
        dbc.Row(
            [
                
                        dbc.Col(
                            dcc.Loading(id='loader_pie', 
                                type='cube',
                                color='#FFFFFF',
                                children=[
                                    dcc.Graph(id="graph_pie", figure=fig_pie), # PIE CHART
                                ],
                            ),
                            width={"size": 6}
                        ),

                        dbc.Col(
                            dcc.Loading(id='loader_bar', 
                                type='cube',
                                color='#FFFFFF',
                                children=[
                                    dcc.Graph(id="graph_bar", figure=fig_bar), # BAR CHART
                                    ],
                            ),
                            width={"size": 6}
                        ), 
                    
                
            ],
            className="g-0",
        ),
        # FIFTH ROW 
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="graph_line", figure=fig_line),width={"size": 12}) # LINE GRAPH
            ],
            className="g-0",
        ),
    ],
)
# ____________________________________________________________
# START CALLBACKS 

# Graphs CallBack 
# Three inputs: two from DatePicker one from Toggle Switch

@app.callback(
    
    Output(component_id="graph_pie",component_property="figure"),
    Output(component_id="graph_bar",component_property="figure"),
    Output(component_id="graph_line",component_property="figure"),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
    Input('fire_switch', 'value'),
    Input('fma_switch','value'),

)

# Define what happens when datepicker or toggle switch change

def new_graphs(start_date,end_date,fma_switch,fire_switch):
   
    # Toggle Switch Check 
    # If off selector stays 1 
    # If on selector changes to 0 
    # Yeah, it doesn't make sense. 
    # Should be 0 for all and 1 for specific incidents
    # Complaints? Speak with Tomahock 

    if fire_switch == False and fma_switch == False:
            selector = 1
            fma = 0
            colors = px.colors.sequential.Viridis_r 
            limit = 100000
            url_dash = f"https://api.fogos.pt/v2/incidents/search" \
            f"?before={end_date}" \
            f"&after={start_date}" \
            f"&limit={limit}" \
            f"&fma={fma}" \
            f"&all={selector}" \

    elif fire_switch == True and fma_switch == False:
            selector = 1 
            fma = 1
            colors = px.colors.sequential.Blues
            limit = 100000
            url_dash = f"https://api.fogos.pt/v2/incidents/search" \
            f"?before={end_date}" \
            f"&after={start_date}" \
            f"&limit={limit}" \
            f"&fma={fma}" \
            f"&all={selector}" \

    elif fire_switch == False and fma_switch == True:
            selector = 0
            fma = 0
            colors = px.colors.sequential.Inferno_r
            limit = 100000
            url_dash = f"https://api.fogos.pt/v2/incidents/search" \
            f"?before={end_date}" \
            f"&after={start_date}" \
            f"&limit={limit}" \
            f"&fma={fma}" \
            f"&all={selector}" \

    else:
            selector = 1
            fma = 0
            colors = px.colors.sequential.Viridis_r
            limit = 100000
            url_dash = f"https://api.fogos.pt/v2/incidents/search" \
            f"?before={end_date}" \
            f"&after={start_date}" \
            f"&limit={limit}" \
            f"&fma={fma}" \
            f"&all={selector}" \

    

    # https://api.fogos.pt/v2/incidents/search?before=2022-02-12&after=2022-02-01&limit=100000&fma=0&all=1

    
    # Define URL based on values from Datepicker and Toggle Switch

    # limit = 100000
    # url_dash = f"https://api.fogos.pt/v2/incidents/search" \
    # f"?before={end_date}" \
    # f"&after={start_date}" \
    # f"&limit={limit}" \
    # f"&fma={fma}" \
    # f"&all={selector}" \


    # Get response from API CALL 
    response_dash = requests.get(url_dash)
  
    # Get the json content from the response
    json_dash = response_dash.json()
  
    # Create Pandas Dataframe from the normalized json response
    # that begins at "data" level. 
    # Depending on your json file this may vary. 
    # Use print(json) in order to check the  structure of your json fle
    df_dash = pd.json_normalize(json_dash,'data')

    # Create day column by extracting the day from the date column
    df_dash['day'] = pd.DatetimeIndex(df_dash['date']).day.astype(str)
    # Convert seconds to Date Time format 
    df_dash['dateTime.sec'] = pd.to_datetime(df_dash['dateTime.sec'], unit='s')

   
    # -------------------------------------------
    # Create dataframes for the updated graphs 
    # -------------------------------------------

    df_in_pie = df_dash.groupby(['natureza','day','familiaName'],as_index=False)['sadoId'].nunique()
    df_in_bar = df_dash.groupby(['natureza','date'],as_index=False)['sadoId'].nunique()
    df_in_line = df_dash.groupby(['dateTime.sec','natureza'],as_index=False)['sadoId'].nunique()

   

    df_half = df_in_line.resample('15min', on='dateTime.sec', offset='01s').sadoId.count().to_frame().reset_index()


    # ------------------------------
    # DEFINE THE UPDATED GRAPHS
    # ------------------------------


    # Define pie, bar, and line graphs 
    fig_pie = px.pie(df_in_pie,names='natureza',values='sadoId',color='natureza',hole=0.5,color_discrete_sequence=colors)
    fig_bar = px.bar(df_in_bar,x='date',y='sadoId', color='natureza',color_discrete_sequence=colors,template='plotly_dark')
    fig_line = px.line(df_half,x='dateTime.sec',y='sadoId',color_discrete_sequence=colors,template='plotly_dark')

    # Styling for graphs

    fig_pie.update_traces(textposition='inside', textinfo='value+percent+label')
    fig_pie.update_layout(uniformtext_minsize=12, uniformtext_mode='hide',template='plotly_dark')
    fig_line.update_xaxes(nticks=5)


    # ------------------------------
    #        RETURN CALLBACK
    # ------------------------------


    return fig_pie, fig_bar, fig_line


# Load APP 

if __name__ == "__main__":
    app.run_server(debug=False, port=8081)


# APP ENDS HERE 

# Made with ???? by Jorge Gomes MARCH 2022


