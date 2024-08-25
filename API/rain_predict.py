import pandas as pd
import tensorflow as tf
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine
import json

c = open('API/info.json')
cred = json.load(c)
engine = create_engine(cred[1]['link'])

def testing_frame():
    types = ['dat','tim','temp', 'real_feel', 'dew_point','humidity', 'wind_speed', 'rain', 'precip', 'visibility', 'pressure']
    query = """SELECT * FROM hourly_data"""
    otp = pd.read_sql_query(query, engine)

    df = pd.DataFrame()
    for i in range(3, len(otp)):
        row = {}
        for j in range(0,3):
            if j == 0:
                row['rain'] = otp.iloc[i]['rain']
            else:
                for x in types:
                    row[f'{j} {x}'] = otp.iloc[i-j][x]
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    
    return df

training_data = testing_frame()


