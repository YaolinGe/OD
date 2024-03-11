import paho.mqtt.client as mqtt
import time
import random

# MQTT settings
broker_address = "localhost"  # Use the address of your MQTT broker
port = 1883
topic = "sensor/data"

# Create a new MQTT client instance
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "DataCollector")

# Connect to the MQTT broker
client.connect(broker_address, port=port)

# Simulate collecting data and publishing
while True:
    data = random.random()  # Simulate sensor data
    client.publish(topic, str(data))
    print(f"Published: {data}")
    time.sleep(.01)  # Publish every 1 second
