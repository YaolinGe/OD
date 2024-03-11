import dash
from dash import html, dcc
import plotly.graph_objs as go
import paho.mqtt.client as mqtt
from threading import Thread

# MQTT settings
broker_address = "localhost"  # Use the address of your MQTT broker
port = 1883
topic = "sensor/data/strain_gauge_ch0"

# Global variable to store the received data
sensor_data = []

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, message):
    global sensor_data
    data = str(message.payload.decode("utf-8"))
    sensor_data.append(data)
    print(f"Received data: {data}")

# Create a new MQTT client instance specifying the callback API version
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "DashApp")

# Assign the on_message callback function
client.on_message = on_message

# Connect to the MQTT broker
client.connect(broker_address, port=port)



if __name__ == '__main__':
    # Start subscribing
    client.loop_start()
    client.subscribe(topic)
    print("started")

