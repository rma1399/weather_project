import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import json

c = open('info.json')
cred = json.load(c)

# Create SQLAlchemy engine
engine = create_engine(cred[1]['link'])

def get_daily_temps():
    l = []
    # Getting weather data from database
    query = "SELECT dat, MAX(temp) FROM hourly_data GROUP BY dat ORDER BY dat"
    daily_highs = pd.read_sql_query(query, engine)

    query = "SELECT dat, MIN(temp) FROM hourly_data GROUP BY dat ORDER BY dat"
    daily_lows = pd.read_sql_query(query, engine)


    for i in range(len(daily_highs)):
        l.append([daily_highs.iloc[i]['dat'], daily_highs.iloc[i]['max'], daily_lows.iloc[i]['min']])

    return l

def get_daily_precip():
    l = []
    query = "SELECT dat, SUM(precip) AS total_precip FROM hourly_data GROUP BY dat ORDER BY dat"
    daily_precip = pd.read_sql_query(query,engine)

    for i in range(len(daily_precip)):
        l.append(daily_precip.iloc[i]['total_precip'])

    return l

def get_weather_type():
    l = []
    query = "SELECT dat FROM hourly_data GROUP BY dat ORDER BY dat"
    num_days = pd.read_sql_query(query,engine)

    for i in range(len(num_days)):
        query = f"SELECT dat, temp, precip, visibility FROM hourly_data WHERE dat = '{num_days.iloc[i]['dat']}'"
        hourly_days = pd.read_sql_query(query,engine)

        l.append(hours_to_type(hourly_days))

    return l


def hours_to_type(hours_data):
    weather_types = {'Cloudy': 0, 'Sunny': 0, 'Precip': 0, 'Partly Cloudy': 0}

    for i in range(len(hours_data)):
        if float(hours_data.iloc[i]['precip'])>0:
            return precip_type(hours_data.iloc[i]['dat'])
        elif int(hours_data.iloc[i]['visibility'])>=8:
            weather_types['Sunny']+=1
        elif int(hours_data.iloc[i]['visibility'])<5:
            weather_types['Cloudy']+=1
        else:
            weather_types['Partly Cloudy']+=1

    return max(weather_types, key=weather_types.get)

def precip_type(dat):
    #called wit date
    query = f"SELECT MIN(real_feel), MAX(real_feel) FROM hourly_data WHERE precip > 0 AND dat = '{dat}'"
    precip_temps = pd.read_sql_query(query,engine)

    if precip_temps.iloc[0]['min']>32:
        return 'Rain'
    elif precip_temps.iloc[0]['max']<33:
        return 'Snow'
    else:
        return 'Mixed Precipitation'

dates = {}
temps = get_daily_temps()
precip = get_daily_precip()
weather = get_weather_type()

for i in range(len(temps)):
    temps[i].append(precip[i])
    temps[i].append(weather[i])
    dates[temps[i][0]] = temps[i][1:]
    print(temps[i][0], dates[temps[i][0]], '\n')

#print(dates)