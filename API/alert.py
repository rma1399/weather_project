import pandas as pd
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine
import json

c = open('API/info.json')
cred = json.load(c)
engine = create_engine(cred[1]['link'])

"""
grabs the highest and lowest temps from the requested day using SQLAcademy Engine
"""
def get_daily_temps(start):
    l = []
    # Getting weather data from database
    query = f"""SELECT dat, MAX(temp) FROM hourly_data WHERE dat = '{start}' GROUP BY dat ORDER BY dat"""
    print(query)
    daily_highs = pd.read_sql_query(query, engine)

    query = f"""SELECT dat, MIN(temp) FROM hourly_data WHERE dat = '{start}' GROUP BY dat ORDER BY dat"""
    daily_lows = pd.read_sql_query(query, engine)


    for i in range(len(daily_highs)):
        l.append([daily_highs.iloc[i]['dat'], float(daily_highs.iloc[i]['max']), float(daily_lows.iloc[i]['min'])])

    return l

"""
grabs the daily precipitation from the requested day using SQLAcademy Engine
"""
def get_daily_precip(start):
    l = []
    query = f"""
    SELECT SUM(precip) AS total_precip
    FROM (
    SELECT DISTINCT tim, precip FROM hourly_data WHERE dat = '{start}' ORDER BY tim)"""
    daily_precip = pd.read_sql_query(query,engine)

    for i in range(len(daily_precip)):
        l.append(daily_precip.iloc[i]['total_precip'])

    return l

"""
grabs the weather type from the requested day using SQLAcademy Engine
"""
def get_weather_type(start):
    l = []
    query = f"""SELECT dat FROM hourly_data WHERE dat = '{start}' GROUP BY dat ORDER BY dat"""
    num_days = pd.read_sql_query(query,engine)

    for i in range(len(num_days)):
        query = f"SELECT dat, temp, precip, visibility, rain FROM hourly_data WHERE dat = '{num_days.iloc[i]['dat']}'"
        hourly_days = pd.read_sql_query(query,engine)

        l.append(hours_to_type(hourly_days))

    return l

"""
take the hourly_data and captures which type of weather happened on the day from the precipitation and visibility data
"""
def hours_to_type(hours_data):
    weather_types = {'Cloudy': 0, 'Sunny': 0, 'Precip': 0, 'Partly Cloudy': 0}

    for i in range(len(hours_data)):
        if float(hours_data.iloc[i]['precip'])>0 or hours_data.iloc[i]['rain']:
            return precip_type(hours_data.iloc[i]['dat'])
        elif int(hours_data.iloc[i]['visibility'])>=8:
            weather_types['Sunny']+=1
        elif int(hours_data.iloc[i]['visibility'])<5:
            weather_types['Cloudy']+=1
        else:
            weather_types['Partly Cloudy']+=1

    return max(weather_types, key=weather_types.get)

"""
trying to decipher the precipitation type using temperature
"""
def precip_type(dat):
    #called with date
    query = f"SELECT MIN(real_feel), MAX(real_feel) FROM hourly_data WHERE dat = '{dat}' AND rain = 't'"
    precip_temps = pd.read_sql_query(query,engine)

    if precip_temps.iloc[0]['min']>32:
        return 'Rain'
    elif precip_temps.iloc[0]['max']<33:
        return 'Snow'
    else:
        return 'Mixed Precipitation'

"""
formalizes the data into an appropriate dictionary
"""
def data(day, month, year):
    day = int(day)
    month = int(month)
    month +=1
    year = int(year)

    print(day, month, year)
    start = date(year, month, day)

    dates = {}
    temps = get_daily_temps(start)
    precip = get_daily_precip(start)
    weather = get_weather_type(start)

    for i in range(len(temps)):
        temps[i].append(precip[i])
        temps[i].append(weather[i])
        dates[temps[i][0].strftime('%Y-%m-%d')] = temps[i][1:]

    return dates

"""
pulls the hourly data from the database from the requested date
"""
def hourly_data(dat):
    hours = {}
    query = f"SELECT * FROM hourly_data WHERE dat = '{dat}'"
    hourly_nums = pd.read_sql_query(query,engine)

    result_dict = hourly_nums.drop(columns='dat').to_dict(orient='index')
    hours = {tim: {k: v for k, v in values.items()} for tim, values in result_dict.items()}

    return hours
