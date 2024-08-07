from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import os
import sys
import alert

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, static_folder='../UI/static', template_folder='../UI/templates')
CORS(app)

"""base"""
@app.route('/')
def index():
    return render_template('index.html')

"""
Gets daily weather data. Reqests the day month and year from the user. Calls the alert function to get and dailyfy the hourly data from a certain date
"""
@app.route('/api/weather')
def get_weather_data():
    day = request.args.get('day')
    month = request.args.get('month')
    year = request.args.get('year')

    data = alert.data(day, month, year)
    if data:
        return jsonify(data)
    else:
        return jsonify({'error': 'Date not found'}), 404
        

"""
Gets hourly data. Requests the date from the user that selects which date the want to see the hourly data from.
"""
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