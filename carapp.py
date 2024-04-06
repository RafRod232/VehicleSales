from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import numpy as np
import plotly.express as px
import os
import zipfile
current_directory = os.getcwd()
with zipfile.ZipFile("car_prices.zip", 'r') as zip_ref:
    zip_ref.extractall(path=current_directory)


df = pd.read_csv("car_prices.csv")
# getting rid of useless column
df.drop(columns=["vin"], inplace=True)
#getting rid of null values
df.dropna(inplace=True)
# creating column to see if selling price caused a profit or loss
df['return'] = np.where(df['sellingprice'] > df['mmr'], 'profit', 'loss')
# creating a column to get month of purchase
df['month'] = df['saledate'].apply(lambda x: x.split()[1])

app = Dash(__name__)

app.layout = html.Div(className="Parent_Div", children=[
    html.Div(id="Title", children='Car Salesman Information', style={'textAlign': 'center','font-size': 75,'font-family': 'FreeMono, monospace','font-style': 'italic'}),
    html.P(id="Subtitle", children='The Graphs Below are to Help Car Salesmen Understand Vehicle Information For When They are Looking to Sell a Car', style={'textAlign': 'center','font-size': 35,'font-family': 'FreeMono, monospace','font-style': 'italic'}),
    html.Div(id="Row_2",children=[
        dcc.Dropdown(options=[{'label': make, 'value': make} for make in sorted(df.make.unique())], value="", id='make-dropdown-selection', style={"width": "50%","margin":"auto"}),
        dcc.Dropdown(value="", id='model-dropdown-selection', style={"width": "50%","margin":"auto"}),
        dcc.RangeSlider(
            id='year-slider',
            min=df['year'].min(),
            max=df['year'].max(),
            step=1,
            marks={},
            value=[df['year'].min(), df['year'].max()]
        ),
        dcc.Graph(id='graph1',style={"width":"75%", "margin":"auto"})
    ], style={"display": "flex","flex-direction" : "column"}),
    html.Div(id="Row_3",children=[
        html.Div(className="Row_3_1", children=[ 
            html.Div(dcc.Dropdown(options=[{'label': make, 'value': make} for make in sorted(df.make.unique())], value="", id='make-dropdown-selection3'),style={"width": "50%","margin":"auto"}),
            html.Div(dcc.Dropdown(value="", id='model-dropdown-selection2', style={"width": "50%","margin":"auto"})),
            html.Div(dcc.Graph(id='graph3'), style=dict(width="100%",margin='auto')) 
        ]),
        html.Div(className="Row_3_2", children=[  
            html.Div(dcc.Dropdown(options=[{'label': make, 'value': make} for make in sorted(df.make.unique())], value="", id='make-dropdown-selection2'),style={"width": "50%","margin":"auto"}),
            html.Div(dcc.Graph(id='graph2'),style=dict(width="100%",margin='auto'))
        ])
    ]),
    html.Div(id="Row_4",children=[  
            html.Div(dcc.Dropdown(options=[{'label': make, 'value': make} for make in sorted(df.make.unique())], value="", id='make-dropdown-selection4'),style={"width": "50%","margin":"auto"}),
            html.Div(dcc.Graph(id='graph4'),style=dict(width="100%",margin='auto'))
            ])
])

#updates the dropdown to the models of the selected car make
@app.callback(Output('model-dropdown-selection', 'options'),Input('make-dropdown-selection', 'value'))
def set_model_options(selected_make):
    filtered_df = df[df['make'] == selected_make]
    return [{'label': model, 'value': model} for model in filtered_df['model'].unique()]

#update slider on years from chosen make and model
@app.callback(Output('year-slider', 'min'),Output('year-slider', 'max'),Output('year-slider', 'marks'),Output('year-slider', 'value'),Input('make-dropdown-selection', 'value'),Input('model-dropdown-selection', 'value'))
def update_year_slider(selected_make, selected_model):
    if selected_make and selected_model:
        filtered_df = df[(df['make'] == selected_make) & (df['model'] == selected_model)]
    elif selected_make: 
        filtered_df = df[df['make'] == selected_make]
    else: 
        filtered_df = df
    min_year = filtered_df['year'].min() 
    max_year = filtered_df['year'].max() 
    marks = {year: str(year) for year in range(min_year, max_year + 1)}
    return min_year, max_year, marks, [min_year, max_year]

@app.callback(Output('graph1', 'figure'),Input('make-dropdown-selection', 'value'),Input('model-dropdown-selection', 'value'),Input('year-slider', 'value'))
def update_graph(selected_make, selected_model, year_range):
    min_year, max_year = year_range
    if selected_make is not None and selected_model is not None:
        filtered_df = df[(df['make'] == selected_make) & (df['model'] == selected_model) & (df['year'] >= min_year) & (df['year'] <= max_year)]
        color_map = {'profit': 'green', 'loss': 'red'}
        return px.scatter(filtered_df, x='mmr', y='sellingprice', color='return', color_discrete_map=color_map,title='View Car Year, Make, and Model Profit/Loss')
    elif selected_make is not None:
        filtered_df = df[(filtered_df['make'] == selected_make) & (df['year'] >= min_year) & (df['year'] <= max_year)]
        color_map = {'profit': 'green', 'loss': 'red'}
        return px.scatter(filtered_df, x='mmr', y='sellingprice', color='return', color_discrete_map=color_map,title='View Car Year, Make, and Model Profit/Loss')
    elif selected_model is not None:
        filtered_df = df[(df['model'] == selected_model) & (df['year'] >= min_year) & (df['year'] <= max_year)]
        color_map = {'profit': 'green', 'loss': 'red'}
        return px.scatter(filtered_df, x='mmr', y='sellingprice', color='return', color_discrete_map=color_map,title='View Car Year, Make, and Model Profit/Loss')
    else:
        filtered_df = df[(df['year'] >= min_year) & (df['year'] <= max_year)]
        color_map = {'profit': 'green', 'loss': 'red'}
        return px.scatter(filtered_df, x='mmr', y='sellingprice', color='return', color_discrete_map=color_map,title='View Car Year, Make, and Model Profit/Loss')

#getting the months that sold the most of the car make    
@app.callback(Output('graph2', 'figure'), Input('make-dropdown-selection2', 'value'))
def updategraph2(selected_make):
    if selected_make is not None:
        filtered_df = df[df['make'] == selected_make]
        return px.histogram(filtered_df, x='month', title=f'Frequency of {selected_make} Sales Based on Month')

#updates the dropdown to the models of the selected 2nd selected car make
@app.callback(Output('model-dropdown-selection2', 'options'),Input('make-dropdown-selection3', 'value'))
def set_model_options2(selected_make):
    filtered_df = df[df['make'] == selected_make]
    return [{'label': model, 'value': model} for model in filtered_df['model'].unique()]

#returning the selling price of the make and model of the car and comparing it by its odometer
@app.callback(Output('graph3', 'figure'), Input('make-dropdown-selection3', 'value'), Input('model-dropdown-selection2', 'value'))
def updategraph3(selected_make,selected_model):
    if selected_make is not None and selected_model is not None:
        filtered_df = df[(df['make'] == selected_make) & (df['model'] == selected_model)]
        return px.scatter(filtered_df, x='odometer', y='sellingprice',title='Selling Price Compared to Odometer',color='year')
    elif selected_make is not None:
        filtered_df = df[(df['make'] == selected_make) & (df['model'] == selected_model)]
        return px.scatter(filtered_df, x='odometer', y='sellingprice',title='Selling Price Compared to Odometer',color='year')
    elif selected_model is not None:
        filtered_df = df[(df['make'] == selected_make) & (df['model'] == selected_model)]
        return px.scatter(filtered_df, x='odometer', y='sellingprice',title='Selling Price Compared to Odometer',color='year')
    else:
        filtered_df = df[(df['make'] == selected_make) & (df['model'] == selected_model)]
        return px.scatter(filtered_df, x='odometer', y='sellingprice',title='Selling Price Compared to Odometer',color='year')

#histogram for which type of car like sedan or suv get sold most from certain brand
@app.callback(Output('graph4', 'figure'), Input('make-dropdown-selection4', 'value'))
def updategraph4(selected_make):
    if selected_make is not None:
        filtered_df = df[df['make'] == selected_make]
        return px.histogram(filtered_df, x='body', title=f'Frequency of {selected_make} Sales Based on Body Type')

if __name__ == '__main__':
    app.run_server(debug=True)
