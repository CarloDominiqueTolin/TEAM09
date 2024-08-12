from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.express as px
import pandas as pd
import requests
import dash_bootstrap_components as dbc
import json
import dash_leaflet as dl
from datetime import datetime
import plotly.graph_objs as go
import math
import convert_gps

API_URL = "http://192.168.100.5:5000"

mapComponent = dl.Map([
    dl.ImageOverlay(
        opacity=0.3, 
        url="/assets/test.png", 
        bounds=convert_gps.calculate_bounds(14.625505226722284, 121.05958838475424, 10)[1]
    ), 
    dl.Marker(
        position=[0.0, 0.0], 
        id='station-loc-1',
        children=[dl.Tooltip(content="Ground Station")]
    ),
    dl.TileLayer(
        url="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png",
        attribution='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>'
    ),
    ], bounds=convert_gps.calculate_bounds(14.625505226722284, 121.05958838475424, 5)[1], style={'height': '90%'})



app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True
) 

CameraModal= dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Stereo All Sky Camera Feed", className="display-4 modal-title"), className="dark"),
            dbc.ModalBody(
                [
                    html.Div([
                        html.Div(
                            [
                                html.H1("All Sky Camera A", className='display-1 text-center'),
                                # html.Img(
                                #     src="https://content.invisioncic.com/g327141/monthly_2021_08/image.png.ed286fb8c3bfa5f20ef821e2f36ec2ba.png",
                                #     style={"width":"100%"}
                                #     ),
                                html.Iframe(src='http://192.168.100.80:8000/video_feed', width='640px', height='480px'),
                                html.P(f"GPS Coordinate: ", id="cam-feed-gps-1")
                            ],className="cam-feed-panel"
                        )
                        ],className='cameras-panel'
                    )
                ],className="dark"),
            dbc.ModalFooter(
                dbc.Button(
                    "Close", id="cam-close", className="ms-auto", n_clicks=0
                ), className="dark"
            )
        ],
        className="dark",
        id="cam-modal",
        is_open=False
    )

def devicesTable(columns,data):
    df = pd.json_normalize(data)

    table = dbc.Table.from_dataframe(
        df[columns], 
        striped=True, 
        bordered=True, 
        hover=True
    )
    
    return table

options = [
    {"label": "2 mins", "value": 2},
    {"label": "5 mins", "value": 5},
    {"label": "10 mins", "value": 10},
    {"label": "30 mins", "value": 30},
    {"label": "1 hr", "value": 60},
    {"label": "2 hrs", "value": 2 * 60},
    {"label": "6 hrs", "value": 6 * 60},
    {"label": "12 hrs", "value": 12 * 60},
    {"label": "24 hrs", "value": 24 * 60},
]

DatabaseModal = dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("System Database", className="display-4 modal-title"), className="dark"),
            dbc.ModalBody(
                [
                    html.Div(
                        [
                            dbc.Tabs(
                                id="db-tabs",
                                active_tab="tab-0",
                                children=[
                                    dbc.Tab(label="Devices"),
                                    dbc.Tab(label="System Logs"),
                                    dbc.Tab(label="Weather Data"),
                                    dbc.Tab(label="Cloud Images"),
                                ],
                            ),
                        ],className="db-sidebar"
                    ),
                    html.Div(
                        [
                            html.H1("Database",id='db-tab-title',className="display-1 db-select-title"),
                            html.Hr(),
                            dcc.Dropdown(
                                id="db-time-dropdown",
                                options=options,
                                value=options[0]["value"],
                                clearable=False
                            ),
                            html.Div(
                                id="data-tables",
                                style={'overflowY': 'scroll',"height":"75%"},
                            )
                            # dbc.Pagination(max_value=10)
                        ],className='db-main-panel'
                    )
                        
                ],className="dark db-panel"),
            dbc.ModalFooter(
                dbc.Button(
                    "Close", id="db-close", className="ms-auto", n_clicks=0
                ), className="dark"
            )
        ],
        className="dark",
        id="db-modal",
        is_open=False,
        size="xl"
    )

GraphsModal = dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Sensor Reading Graphs", className="display-4 modal-title"), className="dark"),
            dbc.ModalBody(
                [
                    html.Div(
                        [
                            dbc.Tabs(
                                id="graphs-tabs",
                                active_tab="tab-0",
                                children=[
                                    dbc.Tab(label="Temperature"),
                                    dbc.Tab(label="Pressure"),
                                    dbc.Tab(label="Humidity"),
                                    dbc.Tab(label="Rainfall"),
                                ],
                            ),
                        ],className="db-sidebar"
                    ),
                    html.Div(
                        [
                            html.H1(id='graphs-tab-title',className="display-1 db-select-title"),
                            html.Hr(),
                            dcc.Dropdown(
                                id="graph-time-dropdown",
                                options=options,
                                value=options[0]["value"],  
                                clearable=False
                            ),
                            dcc.Graph(
                                className="w-100 h-75",
                                id = "station-graph"    
                            )
                        ],className='db-main-panel'
                    )
                        
                ],className="dark db-panel"),
            dbc.ModalFooter(
                dbc.Button(
                    "Close", id="graphs-close", className="ms-auto", n_clicks=0
                ), className="dark"
            )
        ],
        className="dark",
        id="graphs-modal",
        is_open=False,
        size="xl"
    )


SidePanel = html.Div([
    html.I(className="bi bi-camera-video-fill me-2 h3", id='cam-feed-button', n_clicks=0),
    html.I(className="bi bi-database-fill me-2 h3", id='database-button', n_clicks=0),
    html.I(className="bi bi-list-task me-2 h3", id='actions-button', n_clicks=0),
    html.I(className="bi bi-file-earmark-ruled-fill me-2 h3", id='graphs-button', n_clicks=0),
    CameraModal,
    DatabaseModal,
    GraphsModal
    
    ], className="side-panel"
)

def DeviceCard(idx):
    return (html.Div([
        html.H1(f'Ground Station', className="display-1 device-title"),
        html.Hr(),
        html.Div(
            [
                html.Div([
                    html.H2("System Information"),
                    html.Div(
                        [
                            html.P(id=f"status-value-{idx}", className="lead", style={"fontSize":"16px"}),
                        ], className='device-info d-flex align-items-center'),
                    html.Div(
                        [
                            html.P(id=f"location-value-{idx}", className="lead", style={"fontSize":"12px"}),
                        ], className='device-info d-flex align-items-center'), 
                    html.Div(
                        [
                            html.P(id=f"orientation-value-{idx}", className="lead", style={"fontSize":"12px"}),
                        ], className='device-info d-flex align-items-center')
                ], className="top-panel"),
                
                html.Hr(),
                
                html.Div([
                    html.H2('Sensor Parameters'),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.I(className="bi bi-thermometer h2"),
                                    html.P("0 *C", className="display-1", id=f"temp-value-{idx}"),
                                ], className = 'parameter-card'),
                            html.Div(
                                [
                                    html.I(className="bi bi-speedometer2 h2"),
                                    html.P("0 hPa", className="display-1", id=f"pressure-value-{idx}")
                                ], className = 'parameter-card'),
                            html.Div(
                                [
                                    html.I(className="bi bi-moisture h2"),
                                    html.P("0 RH%", className="display-1", id=f"humidity-value-{idx}")
                                ], className = 'parameter-card'),
                            html.Div(
                                [
                                    html.I(className="bi bi-cloud-rain-fill h2"),
                                    html.P("0 mm", className="display-1", id=f"rainfall-value-{idx}")
                                ], className = 'parameter-card')
                        ],className='weather-data-container'),
                        
                ], className="bottom-panel")
            ],className='row-container'),
            html.Hr(style={"margin-bottom":"0px","marginTop":"5%"}),
            html.Div(
                [
                    html.P(
                        "Last Data Update:",
                        style={"textAlign":"right","fontSize":"12px"},
                        id=f"delay-value-{idx}"
                    ),
                    html.P(
                        "Timestamp:",
                        style={"textAlign":"right","fontSize":"12px"},
                        id=f"timestamp-value-{idx}"
                    )
                ],className="time-info"
            )
        ],className="device-card"
    ))


MainPanel = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.H1('Nowea System Manager', className="display-1"),
                        html.P('Rain Cloud Location Tracking', className="display-1")
                    ]),
                html.P(id="now-time", className="display-1", style={"fontSize":"24px"}),
                dcc.Interval(
                    id='time-interval',
                    interval=1000,  # in milliseconds
                    n_intervals=0
                )
            ],className="main-heading"),
        
        html.Div([
            html.Div(
                [
                    mapComponent,
                    html.Div([
                        html.P("Last Update:"),
                        html.P("Timestamp:"),
                    ], className="d-flex justify-content-between")
                ], className='map-display'),
            
            html.Div(
                [
                    DeviceCard(1)
                ],className='device-display'),
        ],className="data-container"),
        html.Div(id="local-loc", className="main-footer d-flex justify-content-end pr-3"),
    ], className = "main-panel"
)


app.layout = html.Div(
    [
        SidePanel,
        MainPanel,
        dcc.Geolocation(id="geolocation"),
        dcc.Interval(
            id='interval-component',
            interval=2000,  # in milliseconds
            n_intervals=0
        )
    ],className='app'
)


# Define variables to store previous timestamps
prev_timestamp1 = None
prev_timestamp2 = None

# Define the time threshold for declaring as "Offline" (in seconds)
offline_threshold = 30

df = pd.read_csv('assets/data.csv')
df_len = len(df)
data = json.loads(df.to_json(orient="records"))

@app.callback(
    Output('status-value-1', 'children'),
    Output('status-value-1', 'style'),
    Output('orientation-value-1', 'children'),
    Output('location-value-1', 'children'),
    Output('station-loc-1', 'position'),
    
    Output('temp-value-1', 'children'),
    Output('pressure-value-1', 'children'),
    Output('humidity-value-1', 'children'),
    Output('rainfall-value-1', 'children'),
    Output('delay-value-1', 'children'),
    Output('timestamp-value-1', 'children'),

    #Output('cam-feed-gps-1', 'children'),
    
    #Output('local-loc','children'),
    
    [Input('interval-component', 'n_intervals'),Input("geolocation", "position")]
)
def update_text(n_intervals,location):
    #print(data[n_intervals])
    print(n_intervals%20)
    return (
        # [html.I(className="bi bi-heart-pulse-fill h6"), device1_status],
        # style1,
        # [html.I(className="bi bi-compass h6"), f"{x1}x {y1}y {z1}z"],
        # [html.I(className="bi bi-geo-alt-fill h6"), f"{round(loc_lat1,4)}, {round(loc_long1,4)} GPS"],
        # [loc_lat1, loc_long1],
        
        # f"{data1['air_temperature']} *C",
        # f"{data1['pressure']} hPa",
        # f"{data1['humidity']} RH%",
        # f"{data1['rainfall_amount']} mm",
        # f"Last update: {time_difference1}s ago",
        # f"Timestamp: {data1['timestamp']}",
        
        # f"GPS Coordinates: {round(loc_lat1,4)}, {round(loc_long1,4)}",
        
        # f"Current Location: lat {location['lat']},lon {location['lon']} | Accuracy {location['accuracy']} meters"
        [html.I(className="bi bi-heart-pulse-fill h6"), "Online"],
        {"color":'#16ca49',"fontSize":"16px"},
        [html.I(className="bi bi-compass h6"), f"{0.1}x {0.2}y {0.0}z"],
        [html.I(className="bi bi-geo-alt-fill h6"), f"{round(14.622645133667016,4)}, {round(121.14287153782796,4)} GPS"],
        [round(14.622645133667016,4), round(121.14287153782796,4)],
        
        f"{1} *C",
        f"{2} hPa",
        f"{3} RH%",
        f"{4} mm",
        f"Last update: {5}s ago",
        f"Timestamp: {7}",
        
        f"GPS Coordinates: {round(14.622645133667016,4)}, {round(121.14287153782796,4)}",
        
        f""
    )
    
    
@app.callback(
 Output("db-tab-title",'children'),
 Output("data-tables",'children'),
 State("db-time-dropdown",'value'),
 [Input("db-tabs",'active_tab'),Input('interval-component', 'n_intervals')]
)
def update_db_panel(drop_value, tab_value,interv):
    # app.logger.info(tab_value)
    if tab_value=="tab-0":
        response = requests.get(f'{API_URL}/devices')
        columns=[
            "id",
            "location.latitude",
            "location.longitude",
            "orientation.x",
            "orientation.y",
            "orientation.z"
        ]
        if response.status_code != 200:
            data = {}
        else:
            data = response.json()['data']
        return "Ground Stations",None #devicesTable(columns,data)
    elif tab_value=="tab-1":
        return "System Logs"
    elif tab_value=="tab-2":
        response = requests.get(
            f'{API_URL}/weather-logs/100',
            json = {
                "minutes":drop_value
            }
        )
        columns=["timestamp","device_id","air_temperature","humidity","pressure","rainfall_amount"]
        if response.status_code != 200:
            data = {}
        else:
            try:
                data = response.json()['data']
                return "Weather Sensors",devicesTable(columns,data)
            except Exception as e:
                return "Weather Sensors", None
                
    elif tab_value=="tab-3":
        return "Cloud Images"
    else:
        return "asdf"
    
def updateGraph(data, station_a):
    traceA = go.Scatter(
        x=station_a["timestamp"],
        y=station_a[data], 
        mode='lines', 
        name='Station A')
    fig = go.Figure(data=[traceA])
    fig.update_layout(
        xaxis=dict(title=None, showticklabels=True),  
        yaxis=dict(title=None, showticklabels=True),
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='#292828',
        showlegend=False,
        paper_bgcolor='#292828',
        font_color="#e7e7e7"
    )
    return fig
    
    
@app.callback(
 Output("graphs-tab-title",'children'),
 Output("station-graph",'figure'),
 State("graph-time-dropdown","value"),
 [Input("graphs-tabs",'active_tab'),Input('interval-component', 'n_intervals')]
)
def update_db_panel(drop_value,tab_value,interv):
    response = requests.get(
        f'{API_URL}/weather-logs/duration',
        json = {
            "minutes":drop_value
        }
    )
    if response.status_code != 200:
        data = {}
    else:
        data = response.json()['data']
        df = pd.DataFrame(data, columns = [           
            'device_id',
            'air_temperature',
            'pressure',
            'humidity',
            'rainfall_amount',
            'timestamp'
        ])
        df = df.sort_values(by='timestamp')
        station_a = df[df['device_id']==1]
        station_b = df[df['device_id']==2]
        
        
    if tab_value=="tab-0":
        return "Temperature", updateGraph("air_temperature",station_a)
    elif tab_value=="tab-1":
        return "Pressure", updateGraph("pressure",station_a)
    elif tab_value=="tab-2":
        return "Humidity", updateGraph("humidity",station_a)
    elif tab_value=="tab-3":
        return "Rainfall", updateGraph("rainfall_amount",station_a)
    else:
        return "asdf", None, None


# @app.callback(
#     Output("graph", "figure"), 
#     Input("candidate", "value"))
# def display_choropleth(candidate):
#     fig = px.scatter_mapbox(
#         device_locations, 
#         lat="lat", 
#         lon="lon",
#         color_discrete_sequence=["#1690ff"], 
#         zoom=12, 
#         center={"lon":121.062232,"lat":14.626261})
#     fig.update_layout(mapbox_style="dark", mapbox_accesstoken=token)
#     fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
#     return fig


@app.callback(
    Output("cam-modal", "is_open"),
    [Input("cam-feed-button", "n_clicks"), Input("cam-close", "n_clicks")],
    [State("cam-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output("db-modal", "is_open"),
    [Input("database-button", "n_clicks"), Input("db-close", "n_clicks")],
    [State("db-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output("graphs-modal", "is_open"),
    [Input("graphs-button", "n_clicks"), Input("graphs-close", "n_clicks")],
    [State("graphs-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("now-time", "children"),
    [Input("time-interval", "n_intervals")],
)
def update_time(x):
    return datetime.now().strftime("%A, %Y-%m-%d %H:%M:%S")

if __name__ == '__main__':
    app.run(debug=True)