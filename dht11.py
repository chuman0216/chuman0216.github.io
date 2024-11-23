from flask import Flask, render_template, jsonify
from flask_mqtt import Mqtt
from datetime import datetime
import json

app = Flask(__name__)

# MQTT configuration
app.config["MQTT_BROKER_URL"] = "smartadmin.aictlab.com"
app.config["MQTT_BROKER_PORT"] = 1883
app.config["MQTT_USERNAME"] = ""  # Optional
app.config["MQTT_PASSWORD"] = ""  # Optional
app.config["MQTT_REFRESH_TIME"] = 1.0  # Polling interval in seconds

mqtt = Mqtt(app)

# Global variable to store sensor data as a time-series
sensor_data = {"temperature": [], "humidity": [], "timestamps": []}


@app.route("/")
def index():
    return render_template(
        "index3.html"
    )  # Create an HTML file in the 'templates' folder


@app.route("/data")
def data():
    return jsonify(sensor_data)


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    global sensor_data
    payload = message.payload.decode()
    print(f"Received message: {payload}")

    try:
        data = json.loads(payload)
        current_time = datetime.now().strftime(
            "%H:%M:%S"
        )  # Get current time as a string
        sensor_data["temperature"].append(data["temperature"])
        sensor_data["humidity"].append(data["humidity"])
        sensor_data["timestamps"].append(current_time)

        # Limit data to the last 20 entries
        if len(sensor_data["temperature"]) > 20:
            sensor_data["temperature"].pop(0)
            sensor_data["humidity"].pop(0)
            sensor_data["timestamps"].pop(0)
    except Exception as e:
        print(f"Error parsing MQTT message: {e}")


if __name__ == "__main__":
    mqtt.subscribe("sensor/dht11")
    app.run(host="0.0.0.0", port=5001)
