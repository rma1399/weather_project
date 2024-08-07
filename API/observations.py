import requests
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
import math
import json

c = open('API/info.json')
cred = json.load(c)
conn_params = cred[0]

precip_type = ['RAIN', 'SNOW', 'ICING', 'FREEZING RAIN', 'THUNDERSTORMS']

"""
compares the weather forecast to see if the naming conventions contain a precipitory word
"""
def isRaining(w):
    x = w.split(" ")
    for i in x:
        if i.upper() in precip_type:
            return True

    return False

conn = psycopg2.connect(**conn_params)
cursor = conn.cursor()

#get json data from NWS
forecast = requests.get('https://api.weather.gov/stations/KBED/observations').json()

"""
formats data into appropriate types and parses NWS json. Converts metric units into American units
"""
for i in range(len(forecast['features'])-1,0,-1):
    timestamp = str(forecast['features'][i]['properties']['timestamp'])
    dt = datetime.fromisoformat(timestamp)

    date = dt.date()
    hour = (int(dt.time().strftime('%H'))+20)%24
    if int(dt.time().strftime('%H')) < hour:
        date = date-timedelta(days=1)
    if forecast['features'][i]['properties']['temperature']['value'] is not None and forecast['features'][i]['properties']['dewpoint']['value'] is not None:
        temp = round(float(forecast['features'][i]['properties']['temperature']['value'])*9.0/5.0+32,2)
    
        dewPoint = round(float(forecast['features'][i]['properties']['dewpoint']['value'])*9.0/5.0,2)+32
    
        windSpeed = 0
        w = forecast['features'][i]['properties']['windSpeed']['value']
        if w is not None:
            windSpeed = round(float(forecast['features'][i]['properties']['windSpeed']['value'])*0.621371,2)
    
        pressure = float(forecast['features'][i]['properties']['barometricPressure']['value'])
    
        visibility = int(forecast['features'][i]['properties']['visibility']['value']*0.000621371)
    
        precip = 0
        p = forecast['features'][i]['properties']['precipitationLastHour']['value']
        if p is not None:
            precip = round(float(forecast['features'][i]['properties']['precipitationLastHour']['value'])*0.0393701,3)
        humidity = round(float(forecast['features'][i]['properties']['relativeHumidity']['value'])/100.0,2)
    
        realFeel = temp
        if temp>=80:
            realFeel = int(forecast['features'][i]['properties']['heatIndex']['value'])*9.0/5.0+32
        elif temp<=50:
            realFeel = int(forecast['features'][i]['properties']['windChill']['value'])*9.0/5.0+32,
    
        rain = isRaining(forecast['features'][i]['properties']['textDescription'])

        # put data into postgres
        cursor.execute('INSERT INTO hourly_data (dat, tim, temp, real_feel, dew_point, humidity, wind_speed, rain, precip, visibility, pressure) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                       (date, hour, temp, realFeel, dewPoint, humidity, windSpeed, rain, precip, visibility, pressure))
        conn.commit()
