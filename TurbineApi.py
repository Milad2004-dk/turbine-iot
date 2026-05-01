from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from flasgger import Swagger
import mysql.connector
import smtplib
from email.mime.text import MIMEText



app = Flask(__name__)
CORS(app)
app.config["SWAGGER"] = {
    "title": "Wind Turbine IOT API v2.0",
    "uiversion": 3,
}
swagger = Swagger(app)

import os

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'turbine-db.mysql.database.azure.com'),
    'user': os.environ.get('DB_USER', 'turbineadmin'),
    'password': os.environ.get('DB_PASSWORD'),
    'database': os.environ.get('DB_NAME', 'turbinedb'),
    'ssl_disabled': False
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)


sender = os.environ.get('EMAIL_SENDER')
receiver = os.environ.get('EMAIL_RECEIVER')
password = os.environ.get('EMAIL_PASSWORD')

    msg = MIMEText(f"ALARM! Turbine {turbine_id} er overophedet!\nTemperatur: {temp}°C overstiger grænse på 75°C!")
    msg['Subject'] = f'ALARM - Turbine {turbine_id} overophedet!'
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, password)
        smtp.sendmail(sender, receiver, msg.as_string())


@app.route('/turbines', methods=['GET'])
def get_turbines():
    """
    Get all wind turbines
    ---
    tags:
      - Turbines
    responses:
      200:
        description: A list of turbines
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM turbines")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)

@app.route('/turbines/<int:turbine_id>', methods=['GET'])
def get_turbine(turbine_id):
    """
    Get a single wind turbine by id
    ---
    tags:
      - Turbines
    parameters:
      - name: turbine_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: The turbine
      404:
        description: Turbine not found
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM turbines WHERE id = %s", (turbine_id,))
    turbine = cursor.fetchone()
    cursor.close()
    conn.close()
    if turbine is None:
        abort(404)
    return jsonify(turbine)

@app.route('/turbines', methods=['POST'])
def create_turbine():
    """
    Register a new wind turbine
    ---
    tags:
      - Turbines
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
            location:
              type: string
            wind_speed:
              type: number
            power_output:
              type: number
            rpm:
              type: number
            status:
              type: string
            temperature:
              type: number
          example:
            name: "Turbine-A1"
            location: "Oresund Zone 3"
            wind_speed: 12.5
            power_output: 2400.0
            rpm: 15.3
            status: "active"
            temperature: 38.2
    responses:
      201:
        description: Created turbine
      400:
        description: Invalid payload
    """
    if not request.json or 'name' not in request.json:
        abort(400)
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO turbines (name, location, wind_speed, power_output, rpm, status, temperature) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (
            request.json['name'],
            request.json.get('location'),
            request.json.get('wind_speed'),
            request.json.get('power_output'),
            request.json.get('rpm'),
            request.json.get('status', 'active'),
            request.json.get('temperature')
        )
    )
    conn.commit()
    turbine_id = cursor.lastrowid
    cursor.execute("SELECT * FROM turbines WHERE id = %s", (turbine_id,))
    turbine = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(turbine), 201

@app.route('/turbines/<int:turbine_id>', methods=['PUT'])
def update_turbine(turbine_id):
    """
    Update sensor data for a wind turbine
    ---
    tags:
      - Turbines
    consumes:
      - application/json
    parameters:
      - name: turbine_id
        in: path
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            wind_speed:
              type: number
            power_output:
              type: number
            rpm:
              type: number
            status:
              type: string
            temperature:
              type: number
    responses:
      200:
        description: Updated turbine
      404:
        description: Turbine not found
    """
    if not request.json:
        abort(400)
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM turbines WHERE id = %s", (turbine_id,))
    turbine = cursor.fetchone()
    if turbine is None:
        cursor.close()
        conn.close()
        abort(404)
    fields = ['name', 'location', 'wind_speed', 'power_output', 'rpm', 'status', 'temperature']
    updates = {f: request.json[f] for f in fields if f in request.json}
    set_clause = ", ".join(f"{k} = %s" for k in updates)
    values = list(updates.values()) + [turbine_id]
    cursor.execute(f"UPDATE turbines SET {set_clause} WHERE id = %s", values)
    conn.commit()
    cursor.execute("SELECT * FROM turbines WHERE id = %s", (turbine_id,))
    updated = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(updated)

@app.route('/turbines/<int:turbine_id>', methods=['DELETE'])
def delete_turbine(turbine_id):
    """
    Delete a wind turbine
    ---
    tags:
      - Turbines
    parameters:
      - name: turbine_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Deletion result
      404:
        description: Turbine not found
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM turbines WHERE id = %s", (turbine_id,))
    turbine = cursor.fetchone()
    if turbine is None:
        cursor.close()
        conn.close()
        abort(404)
    cursor.execute("DELETE FROM turbines WHERE id = %s", (turbine_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'result': True})

alarms = []

@app.route('/sensor-data', methods=['POST'])
def receive_sensor_data():
    """
    Modtag temperaturdata fra IoT sensor
    ---
    tags:
      - Sensors
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - turbine_id
            - temp
          properties:
            turbine_id:
              type: integer
            temp:
              type: number
          example:
            turbine_id: 1
            temp: 80.5
    responses:
      200:
        description: Data modtaget og behandlet
      400:
        description: Mangler data
    """
    if not request.json or 'turbine_id' not in request.json or 'temp' not in request.json:
        abort(400)

    turbine_id = request.json['turbine_id']
    temp = request.json['temp']

    # Event 1 - Sensor Value Received
    print(f"[EVENT 1] Sensor data modtaget: Turbine {turbine_id}, Temp: {temp}°C")

    # Beslutning - Threshold check
    if temp > 75:
        # Event 2 - Anomaly Detected
        alarm = {
            'turbine_id': turbine_id,
            'temp': temp,
            'alarm': 'OVERHEAT',
            'message': f'Temperatur {temp}°C overstiger grænse på 75°C!'
        }
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO alarms (turbine_id, temp, alarm, message) VALUES (%s, %s, %s, %s)",
            (turbine_id, temp, 'OVERHEAT', f'Temperatur {temp}°C overstiger grænse på 75°C!')
        )
        db.commit()
        cursor.close()
        db.close()
        send_alarm_email(turbine_id, temp)

        # Notifikation (log til terminal)
        print(f"[ALARM] Turbine {turbine_id} overophedet! Temp: {temp}°C")

        return jsonify({'status': 'ALARM', 'alarm': alarm}), 200
    else:
        print(f"[NORMAL] Temperatur OK: {temp}°C")
        return jsonify({'status': 'OK', 'temp': temp}), 200


@app.route('/alarms', methods=['GET'])
def get_alarms():
    """
    Hent alle alarmer
    ---
    tags:
      - Sensors
    responses:
      200:
        description: Liste af alarmer
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM alarms ORDER BY created_at DESC")
    alarms_db = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(alarms_db)




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
