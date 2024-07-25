from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import os
import sys

# Add the API directory to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import alert  # Import your alert module

# Initialize Flask app with custom static and template folder paths
app = Flask(__name__, static_folder='../UI/static', template_folder='../UI/templates')
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/weather')
def get_weather_data():
    data = alert.data()  # Call the data() function from alert.py
    if data:
        return jsonify(data)
    else:
        return jsonify({'error': 'Date not found'}), 404
        

@app.route('/api/weather/hourly', methods=['GET'])
def get_hourly_weather():
    date = request.args.get('date')
    if date:
        data = alert.hourly_data(date)
        if data:
            return jsonify(data)
        else:
            return jsonify({'error': 'Date not found'}), 404
    else:
        return jsonify({'error': 'Date parameter is required'}), 400

if __name__ == '__main__':
    app.run(debug=True)