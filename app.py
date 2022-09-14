import dash
from dash import Dash, dcc, html, Input, Output, dash_table #pip install dash
#import jupyter_dash #integrated in jupyter notebooks
#from jupyter_dash import JupyterDash as JD
import dash_leaflet as dl
#import dash_leaflet.express as dlx #pip install --upgrade protobuf==3.20.0 --user before importing and if necessarym, restart the kernel
import requests
import json
#from dash_extensions.javascript import assign, arrow_function, Namespace
import pandas as pd
#import geopandas as gpd
import numpy as np
import random
from flask_caching import Cache
import os
import dash_bootstrap_components as dbc

#pip list --format=freeze > requirements.txt

# #querying data from pg_featureserv API for bcfishpass
request = 'https://features.hillcrestgeo.ca/bcfishpass/collections/bcfishpass.streams/items.json'
query = '?properties=watershed_group_code,segmented_stream_id&filter=watershed_group_code%20=%20%27HORS%27' #this query slows things down for some reason

request1 = 'https://tiles.hillcrestgeo.ca/bcfishpass/bcfishpass.streams.json'
query1 = '?properties=watershed_group_code,segmented_stream_id&filter=watershed_group_code%20=%20%27HORS%27'

response_API = requests.get(request+query)
response_API1 = requests.get(request1+query1)

parse = response_API.text
stream = json.loads(parse)



prior_table = pd.read_csv('D:\\CWF\\repos\\app\\app\\tables\\priority_barriers.csv', index_col=False)
inter_table = pd.read_csv('D:\\CWF\\repos\\app\\app\\tables\\inter_barriers.csv', index_col=False)
#D:\\CWF\\repos\\JB\\Jupyter-Book-4\\Tutorials\\Jupyter_Book\\mynewbook\\app\\

def priority(row):
    request = 'https://features.hillcrestgeo.ca/bcfishpass/collections/bcfishpass.crossings/items.json?watershed_group_code=HORS&aggregated_crossings_id=' + str(row['aggregated_crossings_id'])
    response_api = requests.get(request)
    parse = response_api.text
    result = json.loads(parse)
    features = result['features']
    hab_gain=0
    cost_benefit=0
    for i in range(len(features)):
        if features[i]['properties']['aggregated_crossings_id'] == row['aggregated_crossings_id']:
            hab_gain = features[i]['properties']['all_spawningrearing_belowupstrbarriers_km']
    
    if hab_gain != 0: cost_benefit = row['estimated_cost']/hab_gain
    
    return hab_gain,cost_benefit

prior_table['hab_gain'] = prior_table.apply(lambda row: priority(row)[0], axis=1)
prior_table['cost_benefit_ratio'] = prior_table.apply(lambda row: priority(row)[1], axis=1)


# parse1 = response_API1.text
# gjson = json.loads(parse1)

# #api call function
# def apiCall(w):
#     request = 'https://features.hillcrestgeo.ca/bcfishpass/collections/bcfishpass.streams/items.json'
#     query = '?properties=watershed_group_code,segmented_stream_id&filter=watershed_group_code%20=%20%27' + w + '%27' #this query slows things down for some reason

#     request1 = 'https://features.hillcrestgeo.ca/bcfishpass/collections/bcfishpass.crossings/items.json'
#     query1 = '?properties=aggregated_crossings_id,pscis_status,barrier_status,access_model_ch_co_sk,all_spawningrearing_per_barrier,all_spawningrearing_km&filter=watershed_group_code%20=%20%27' + w + '%27%20AND%20all_spawningrearing_km%3e0'

#     response_API = requests.get(request+query)
#     response_API1 = requests.get(request1+query1)

#     parse = response_API.text
#     parse1 = response_API1.text

#     return parse, parse1


# prior_table = pd.read_csv('tables\priority_barriers.csv', index_col=False)
# inter_table = pd.read_csv('tables\inter_barriers.csv', index_col=False)

#configuring the app
#useful resources include:
#https://github.com/Coding-with-Adam/Dash-by-Plotly/blob/master/Other/Dash_Introduction/intro.py
#https://dash-leaflet.herokuapp.com/
#https://github.com/plotly/jupyter-dash/blob/master/notebooks/getting_started.ipynb

from sre_constants import IN


app = dash.Dash(__name__)
server = app.server
cache = Cache()
cache.init_app(app.server, config={'CACHE_TYPE': 'SimpleCache'})
timeout = 20
#making dropdown option based on property in data table
id_list = []

#ns = Namespace("myNamespace", "mySubNamespace")

#priority vs intermediate barrier list

# prior_table = pd.read_csv('tables\priority_barriers.csv', index_col=False)
# inter_table = pd.read_csv('tables\inter_barriers.csv', index_col=False)

# def priority(row):
#     request = 'https://features.hillcrestgeo.ca/bcfishpass/collections/bcfishpass.crossings/items.json?watershed_group_code=HORS&aggregated_crossings_id=' + str(row['aggregated_crossings_id'])
#     response_api = requests.get(request)
#     parse = response_api.text
#     result = json.loads(parse)
#     features = result['features']
#     hab_gain=0
#     cost_benefit=0
#     for i in range(len(features)):
#         if features[i]['properties']['aggregated_crossings_id'] == row['aggregated_crossings_id']:
#             hab_gain = features[i]['properties']['all_spawningrearing_belowupstrbarriers_km']
    
#     if hab_gain != 0: cost_benefit = row['estimated_cost']/hab_gain
    
#     return hab_gain,cost_benefit

# prior_table['hab_gain'] = prior_table.apply(lambda row: priority(row)[0], axis=1)
# prior_table['cost_benefit_ratio'] = prior_table.apply(lambda row: priority(row)[1], axis=1)


#seperate GeoJSOn for selected filtering

 
    #-----------------------------------------------------------------------------------------------------------------------------------

# #point to layer 
# point_to_layer = assign("function(feature, latlng, context){return L.circleMarker(latlng);}")
# ------------------------------------------------------------------------------
prior_drop =  dcc.Dropdown(
                    options=[
                        {'label': 'Priority Barrier List', 'value': 'priority'},
                        {'label': 'Intermediate Barrier List', 'value': 'intermediate'}
                    ],
                    id='dd',
                    style={'width': '500px'}
                )

watershed_drop = dcc.Dropdown(
                    options=[
                        {'label': 'HORS', 'value': 'HORS'},
                        {'label': 'BULK', 'value': 'BULK'},
                        {'label': 'LNIC', 'value': 'LNIC'},
                        {'label': 'ELKR', 'value': 'ELKR'}
                    ],
                    value = 'HORS',
                    id='watershed',
                    style={'width': '500px'}
                )
# App layout
app.layout = html.Div([

    html.H1("Web Application Dashboard for Fish Passage BC", style={'text-align': 'left'}),

    

    dbc.Row([
        dbc.Col(prior_drop, width = 2),
        dbc.Col(watershed_drop, width = 2)
    ], id="dropdown"),
    
    

    dl.Map(children=[
        
        
        dl.LayersControl(
        [dl.BaseLayer(dl.TileLayer(url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    attribution='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'), name='ESRI Topographic', checked=False),
                    dl.BaseLayer(dl.TileLayer(), name='Base', checked=True), dl.BaseLayer(dl.Overlay(children = ns("pbf2dash")), name='test')] +
        [ dl.Overlay(children=[], checked=True, id='pass', name='Passable')]+
        [ dl.Overlay(children=[], checked=True, id='pot', name='Potential')]+
        [ dl.Overlay(children=[], checked=True, id='bar', name='Barrier')]+
        [ dl.Overlay(children=[], checked=True, id='other', name='Unknown')] +
        [dl.Overlay(dl.GeoJSON(data=stream, id="streams", zoomToBounds=True), name='Stream Network',checked=True)])
        ],
        id='map',
        style={'width': '1500px', 'height': '500px'}, #style is key as map will not show up without it
        center=[52.6,-120.5],
        zoom=8 
    ),

    html.Br(),


    dash_table.DataTable(
                        columns=[
                            {'name': 'Crossing ID', 'id': 'id', 'type': 'numeric'},
                            {'name': 'PSCIS status', 'id': 'pscis_status', 'type': 'text'},
                            {'name': 'Barrier Status', 'id': 'barrier_status', 'type': 'text'},
                            {'name': 'Acess Model', 'id': 'access_model_ch_co_sk', 'type': 'text'},
                            {'name': 'All habitat', 'id': 'all_spawningrearing_per_barrier', 'type': 'numeric'},
                            {'name': 'Latitude', 'id': 'lat', 'type': 'numeric'},
                            {'name': 'Longitude', 'id': 'lon', 'type': 'numeric'}
                        ],
                        data=[],
                        sort_action="native",
                        sort_mode="multi",
                        filter_action="native",
                        style_data={
                            'color': 'white',
                            'backgroundColor': 'black'
                        },
                        id='table2',
                        active_cell= None
                        ),
    
    html.Br(),
    
    html.H2(id='test')

], id = 'app')



# ------------------------------------------------------------------------------
# Connect Leaflet Map to Dash Components
@cache.memoize()

#api call function
def apiCall(w):
    request = 'https://features.hillcrestgeo.ca/bcfishpass/collections/bcfishpass.streams/items.json'
    query = '?properties=watershed_group_code,segmented_stream_id&filter=watershed_group_code%20=%20%27' + w + '%27' #this query slows things down for some reason

    request1 = 'https://features.hillcrestgeo.ca/bcfishpass/collections/bcfishpass.crossings/items.json'
    query1 = '?properties=aggregated_crossings_id,pscis_status,barrier_status,access_model_ch_co_sk,all_spawningrearing_per_barrier,all_spawningrearing_km&filter=watershed_group_code%20=%20%27' + w + '%27%20AND%20all_spawningrearing_km%3e0'

    response_API = requests.get(request+query)
    response_API1 = requests.get(request1+query1)

    parse = response_API.text
    parse1 = response_API1.text

    return parse, parse1

def apiCall_prior(w,l):

    list1 = "("
    if l == 'intermediate':
        for i in inter_table['intermediate'].values:
            if i == (inter_table['intermediate'].iat[-1]):
                list1 = list1 + str(i) + ")"
            else:
                list1 = list1 + str(i) + ","
    elif l == 'priority':
        for i in prior_table['aggregated_crossings_id'].values:
            if i == (prior_table['aggregated_crossings_id'].iat[-1]):
                list1 = list1 + str(i) + ")"
            else:
                list1 = list1 + str(i) + ","


    request = 'https://features.hillcrestgeo.ca/bcfishpass/collections/bcfishpass.streams/items.json'
    query = '?properties=watershed_group_code,segmented_stream_id&filter=watershed_group_code%20=%20%27' + w + '%27' #this query slows things down for some reason

    request1 = 'https://features.hillcrestgeo.ca/bcfishpass/collections/bcfishpass.crossings/items.json'
    query1 = '?properties=aggregated_crossings_id,pscis_status,barrier_status,access_model_ch_co_sk,all_spawningrearing_per_barrier,all_spawningrearing_km&filter=watershed_group_code%20=%20%27' + w + '%27%20AND%20all_spawningrearing_km%3e0%20AND%20aggregated_crossings_id%20IN%20' + list1

    response_API = requests.get(request+query)
    response_API1 = requests.get(request1+query1)

    parse = response_API.text
    parse1 = response_API1.text

    return parse, parse1

def get_data(features):
    Passable = []
    potential = []
    barrier = []
    other = []
    for i in range(len(features)):
        if features[i]['properties']['barrier_status'] == 'PASSABLE':
            Passable.append(
                dl.CircleMarker(
                    id = str(features[i]['properties']['aggregated_crossings_id']),
                    color='white',
                    fillColor = '#32cd32',
                    fillOpacity = 1, 
                    center = (features[i]['geometry']['coordinates'][1], features[i]['geometry']['coordinates'][0]), 
                    children=[
                        dl.Tooltip(str(features[i]['properties']['aggregated_crossings_id'])),
                        dl.Popup(str(features[i]['properties']['aggregated_crossings_id'])),
                    ],
                )
            )
        elif features[i]['properties']['barrier_status'] == 'POTENTIAL':
            potential.append(
                dl.CircleMarker(
                    color='white',
                    fillColor = '#ffb400',
                    fillOpacity = 1, 
                    center = (features[i]['geometry']['coordinates'][1], features[i]['geometry']['coordinates'][0]), 
                    children=[
                        dl.Tooltip(str(features[i]['properties']['aggregated_crossings_id'])),
                        dl.Popup(str(features[i]['properties']['aggregated_crossings_id']) + "\n NEWS: idk whats going on!"),
                    ],
                )
            )
        elif features[i]['properties']['barrier_status'] == 'BARRIER':
            barrier.append(
                dl.CircleMarker(
                    id="marker",
                    color='white',
                    fillColor = '#d52a2a',
                    fillOpacity = 1, 
                    center = (features[i]['geometry']['coordinates'][1], features[i]['geometry']['coordinates'][0]), 
                    children=[
                        dl.Tooltip(str(features[i]['properties']['aggregated_crossings_id']), id="tooltip"),
                        dl.Popup(str(features[i]['properties']['aggregated_crossings_id'])),
                    ],
                )
            )
        else:
            other.append(
                dl.CircleMarker(
                    color = 'white',
                    fillColor = '#965ab3',
                    fillOpacity = 1,
                    center = (features[i]['geometry']['coordinates'][1], features[i]['geometry']['coordinates'][0]), 
                    children=[
                        dl.Tooltip(str(features[i]['properties']['aggregated_crossings_id'])),
                        dl.Popup()
                    ],
                )
            )

    pass_cluster = dl.MarkerClusterGroup(id='markers', children=Passable)
    pot_cluster = dl.MarkerClusterGroup(id='markers', children=potential)
    bar_cluster = dl.MarkerClusterGroup(id='barriers', children=barrier)
    other_cluster = dl.MarkerClusterGroup(id='markers1', children=other)
    return pass_cluster, pot_cluster, bar_cluster, other_cluster

# features = gjson['features']
def get_tabledata(features):
    id_list = []
    for i in range(len(features)):
        pscis=features[i]['properties']['pscis_status']
        barr=features[i]['properties']['barrier_status']
        acc=features[i]['properties']['access_model_ch_co_sk']
        all=features[i]['properties']['all_spawningrearing_per_barrier']
        cross_id = str(features[i]['properties']['aggregated_crossings_id'])
        lat = features[i]['geometry']['coordinates'][1]
        lon = features[i]['geometry']['coordinates'][0]

        temp = dict(id = cross_id, pscis_status=pscis, barrier_status=barr, access_model_ch_co_sk=acc, all_spawningrearing_per_barrier=all, lat = lat, lon = lon)

        id_list = id_list + [temp,]
    return id_list

def get_latlon(features):
    id_list = []
    for i in range(len(features)):
        cross_id = str(features[i]['properties']['aggregated_crossings_id'])
        lat = features[i]['geometry']['coordinates'][1]
        lon = features[i]['geometry']['coordinates'][0]

        temp = dict(id = cross_id,lat = lat, lon = lon)

        id_list = id_list + [temp,]
    return id_list



@app.callback(
    [Output('pass', 'children'), Output('pot', 'children'), Output('bar', 'children'), Output('other', 'children'), Output('streams', 'data'), Output('table2','data')], [Input('watershed', 'value'), Input('dd', 'value')]
)
def update_map(value, priority):

    
    
    
    if value == 'BULK':
        parse, parse1 = apiCall('BULK')
        B_gjson = json.loads(parse1)
        B_stream = json.loads(parse)
        features = B_gjson['features']
        return get_data(features)[0], get_data(features)[1], get_data(features)[2], get_data(features)[3], B_stream, get_tabledata(features)
    elif value == 'LNIC':
        parse, parse1 = apiCall('LNIC')
        B_gjson = json.loads(parse1)
        B_stream = json.loads(parse)
        features = B_gjson['features']
        return get_data(features)[0], get_data(features)[1], get_data(features)[2], get_data(features)[3], B_stream, get_tabledata(features)
    elif value == 'ELKR':
        parse, parse1 = apiCall('ELKR')
        B_gjson = json.loads(parse1)
        B_stream = json.loads(parse)
        features = B_gjson['features']
        return get_data(features)[0], get_data(features)[1], get_data(features)[2], get_data(features)[3], B_stream, get_tabledata(features)
    elif value == 'HORS':
        parse, parse1 = apiCall('HORS')
        B_gjson = json.loads(parse1)
        B_stream = json.loads(parse)
        features = B_gjson['features']

        

        if priority == 'intermediate':
            parse, parse1 = apiCall_prior('HORS',priority)
            B_gjson = json.loads(parse1)
            B_stream = json.loads(parse)
            features = B_gjson['features']
            data = []
            for i in range(0, len(inter_table.iloc[:,0])):
                id_list = get_tabledata(features)
                id_index = dict((p['id'],j) for j,p in enumerate(id_list))
                index1 = id_index.get(str(inter_table.iloc[:,0][i]), -1)
                data = data + [id_list[index1],]
            return get_data(features)[0], get_data(features)[1], get_data(features)[2], get_data(features)[3], B_stream, data
        elif priority == 'priority':
            parse, parse1 = apiCall_prior('HORS',priority)
            B_gjson = json.loads(parse1)
            B_stream = json.loads(parse)
            features = B_gjson['features']
            data=[]
            for i in range(0, len(prior_table.iloc[:,0])):
                id_list = get_latlon(features)
                id_index = dict((p['id'],j) for j,p in enumerate(id_list))
                index1 = id_index.get(str(prior_table.iloc[:,0][i]), -1)
                data = data + [id_list[index1],]
            data = pd.DataFrame(data)
            new = pd.concat([prior_table,data], axis=1, join="inner")#.drop_duplicates()#.reset_index(drop=True)
            data = new.set_index('aggregated_crossings_id', drop=False).to_dict(orient="records")#.drop('id',axis=1)

            return get_data(features)[0], get_data(features)[1], get_data(features)[2], get_data(features)[3], B_stream, data
            
        else:
           return get_data(features)[0], get_data(features)[1], get_data(features)[2], get_data(features)[3], B_stream, get_tabledata(features) 
    
        
    
    else: 
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    
    
@app.callback(
    [Output('map', 'center'), Output('map', 'zoom')], [Input('table2', 'active_cell'), Input('watershed', 'value')]
)
def marker(cell, value):
    if value == 'HORS':
        if cell['column_id'] == "id" or cell['column_id'] == "aggregated_crossings_id":
            parse1 = apiCall(value)[1]
            B_gjson = json.loads(parse1)
            features = B_gjson['features']
            id_list = get_tabledata(features)
            for i in id_list:
                if str(i['id']) == cell['row_id']:
                    lat = i['lat']
                    lon = i['lon']
                    center = [lat,lon]
            return center, 16 
    elif value == 'BULK':
        if cell['column_id'] == "id":
            parse1 = apiCall(value)[1]
            B_gjson = json.loads(parse1)
            features = B_gjson['features']
            id_list = get_tabledata(features)
            for i in id_list:
                if str(i['id']) == cell['row_id']:
                    lat = i['lat']
                    lon = i['lon']
                    center = [lat,lon]
            return center, 16

    elif value == 'LNIC':
        if cell['column_id'] == "id":
            parse1 = apiCall(value)[1]
            B_gjson = json.loads(parse1)
            features = B_gjson['features']
            id_list = get_tabledata(features)
            for i in id_list:
                if str(i['id']) == cell['row_id']:
                    lat = i['lat']
                    lon = i['lon']
                    center = [lat,lon]
            return center, 16

    elif value == 'ELKR':
        if cell['column_id'] == "id":
            parse1 = apiCall(value)[1]
            B_gjson = json.loads(parse1)
            features = B_gjson['features']
            id_list = get_tabledata(features)
            for i in id_list:
                if str(i['id']) == cell['row_id']:
                    lat = i['lat']
                    lon = i['lon']
                    center = [lat,lon]
            return center, 16           
    
    else:
        return dash.no_update, dash.no_update

# @app.callback(
#     [Output('table2', 'active_cell'), Output('test', 'children')], [Input('table2', 'active_cell'), Input('watershed', 'value'), Input('map', 'click_lat_lng')]
# )

# def click_marker(cell, value, click):
#     if value == 'HORS':
#         parse1 = apiCall(value)[1]
#         B_gjson = json.loads(parse1)
#         features = B_gjson['features']
#         id_list = get_tabledata(features)
#         for i in id_list:
#             if ((-0.001 <= (click[0] - i['lat'])) and ((click[0] - i['lat'])<= 0.001)) and ((-0.001 <= (click[0] - i['lon'])) and ((click[0] - i['lon'])<= 0.001)):
#                 return cell, (i['lat'])
#             else: return dash.no_update, dash.no_update

#app.clientside_callback("functions(x){return x;}", Output("test", "children"), Input(marker, "n_clicks"))

# @app.callback(
#     Output("test", "children"),[Input("barriers", "children")]
# )
# def click_marker(marker_id):
#     #print(marker_id[0])
#     return "KJFDHGLIDUGHIKGJC: {}".format(marker_id[0])

# @app.callback(
#     [Output('pass', 'children'), Output('pot', 'children'), Output('bar', 'children'), Output('other', 'children'), Output('streams', 'data'), Output('table2','data')], [Input('table2','derived_virtual_data'),Input('watershed', 'value'), Input('dd', 'value')]
# )
# def filter_trigger(rows, value, priority):

#     parse, parse1 = apiCall('HORS')
#     B_gjson = json.loads(parse1)
#     B_stream = json.loads(parse)
#     features = B_gjson['features']

#     if rows is not None:

#         dff = pd.DataFrame(rows) 
        
#         data = []
#         for i in range(0, len(dff.iloc[:,0])):
#             id_list = get_tabledata(features)
#             id_index = dict((p['id'],j) for j,p in enumerate(id_list))
#             index1 = id_index.get(str(dff.iloc[:,0][i]), -1)
#             data = data + [id_list[index1],]
#         return get_data(features)[0], get_data(features)[1], get_data(features)[2], get_data(features)[3], B_stream, data

    # else:

    #     return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output('table2', 'columns'), [Input('dd', 'value')]
)
def priority_filter(value):
    if value == 'priority':
        columns=[
                    {'name': 'Crossing ID', 'id': 'aggregated_crossings_id', 'type': 'numeric'},
                    {'name': 'Stream Name', 'id': 'stream_name', 'type': 'text'},
                    {'name': 'Road Name', 'id': 'road_name', 'type': 'text'},
                    {'name': 'Owner', 'id': 'owner', 'type': 'text'},
                    {'name': 'Proposed Fix', 'id': 'proposed_fix', 'type': 'text'},
                    {'name': 'Estimated Cost', 'id': 'estimated_cost', 'type': 'text'},
                    {'name': 'Upstream Habitat Quality', 'id': 'upstr_hab_quality', 'type': 'text'},
                    {'name': 'Barrier Type', 'id': 'barrier_type', 'type': 'text'},
                    {'name': 'Habitat Gain', 'id': 'hab_gain', 'type': 'numeric'},
                    {'name': 'Cost Benefit Ratio', 'id': 'cost_benefit_ratio', 'type': 'numeric'},
                    {'name': 'Upstream Habitat Quality', 'id': 'upstr_hab_quality', 'type': 'text'},
                    {'name': 'Priority', 'id': 'priority', 'type': 'text'},
                    {'name': 'Next Steps', 'id': 'next_steps', 'type': 'text'},
                    {'name': 'Reasoning', 'id': 'reason', 'type': 'text'},
                    {'name': 'Notes', 'id': 'notes', 'type': 'text'}
                    # {'name': 'Latitude', 'id': 'lat', 'type': 'numeric'},
                    # {'name': 'Longitude', 'id': 'lon', 'type': 'numeric'}
                ]
        return columns
    else:
        columns=[
                    {'name': 'Crossing ID', 'id': 'id', 'type': 'numeric'},
                    {'name': 'PSCIS status', 'id': 'pscis_status', 'type': 'text'},
                    {'name': 'Barrier Status', 'id': 'barrier_status', 'type': 'text'},
                    {'name': 'Acess Model', 'id': 'access_model_ch_co_sk', 'type': 'text'},
                    {'name': 'All habitat', 'id': 'all_spawningrearing_per_barrier', 'type': 'numeric'},
                    {'name': 'Latitude', 'id': 'lat', 'type': 'numeric'},
                    {'name': 'Longitude', 'id': 'lon', 'type': 'numeric'}
                ]
        return columns

        



        
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True, port = random.choice(range(2000, 10000)))
    #app.run_server(debug=True, port = random.choice(range(2000, 10000)))
