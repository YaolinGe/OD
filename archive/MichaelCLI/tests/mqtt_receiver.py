import dash
from dash import html, dcc
import plotly.graph_objs as go
import paho.mqtt.client as mqtt
from threading import Thread

# MQTT settings
broker_address = "localhost"  # Use the address of your MQTT broker
port = 1883
topic = "sensor/data"

# Global variable to store the received data
sensor_data = []

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, message):
    global sensor_data
    data = str(message.payload.decode("utf-8"))
    sensor_data.append(float(data))
    print(f"Received data: {data}")

# Create a new MQTT client instance specifying the callback API version
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "DashApp")

# Assign the on_message callback function
client.on_message = on_message

# Connect to the MQTT broker
client.connect(broker_address, port=port)

# Start subscribing
client.loop_start()
client.subscribe(topic)

# Dash app to display the sensor data
app = dash.Dash(__name__)
app.layout = html.Div([
    dcc.Graph(id='live-graph', animate=True),
    dcc.Interval(
        id='graph-update',
        interval=1000,
        n_intervals=0
    ),
])

@app.callback(dash.dependencies.Output('live-graph', 'figure'),
              [dash.dependencies.Input('graph-update', 'n_intervals')])
def update_graph(n):
    global sensor_data
    data_plot = go.Scatter(
        x=list(range(len(sensor_data))),
        y=sensor_data,
        name='Scatter',
        mode='lines+markers'
    )

    return {'data': [data_plot], 'layout': go.Layout(xaxis=dict(range=[max(0, len(sensor_data)-50), len(sensor_data)]),
                                                      yaxis=dict(range=[min(sensor_data[-50:], default=0), max(sensor_data[-50:], default=1)]),)}

if __name__ == '__main__':
    # Run the Dash app in a separate thread
    dash_thread = Thread(target=app.run_server)
    dash_thread.start()
