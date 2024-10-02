import pandas as pd
import tensorflow as tf
from keras import layers, models
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine
from sklearn.preprocessing import LabelEncoder
import json
from sklearn.model_selection import train_test_split
import requests
from observations import isRaining

c = open('API/info.json')
cred = json.load(c)
engine = create_engine(cred[1]['link'])

def labeling(df):
    le = LabelEncoder()
    for col in df.columns.tolist():
        tp = df[col].dtype
        if tp != 'float64' and tp != 'int64':
            df[col] = le.fit_transform(df[col])

    return df

def testing_frame():

    types = ['dat','tim','temp', 'real_feel', 'dew_point','humidity', 'wind_speed', 'rain', 'precip', 'visibility', 'pressure']
    query = """SELECT * FROM hourly_data"""
    otp = pd.read_sql_query(query, engine)

    df = pd.DataFrame()
    for i in range(3, len(otp)):
        row = {}
        for j in range(0,4):
            if j == 0:
                row['rain'] = otp.iloc[i]['rain']
            else:
                for x in types:
                    row[f'{j} {x}'] = otp.iloc[i-j][x]
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    return labeling(df)


#def rain_prediction(): call this once the model has been trained, reqeusts, prediction, post

#nuearal network, logistical regression, decision tree
def build_neural_network(input_shape):
    # Build the network
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(64, activation='sigmoid', input_shape=input_shape),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    return model

def training(model, xt, yt):

    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
    model.fit(xt, yt, epochs=10)

    return model



def trainer():
    data = testing_frame()

    y = data['rain']
    x = data.drop('rain', axis=1)

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    input_shape = (x_train.shape[1],)
    print('yup')

    model = build_neural_network(input_shape)
    history = training(model, x_train, y_train)
    history.save('API/current-model.keras')


def rain_predict(ob_station):
    model = tf.keras.models.load_model('API/current-model.keras')

    data = requests.get(f'https://api.weather.gov/stations/{ob_station}/observations').json()
    types = ['dat','tim','temp', 'real_feel', 'dew_point','humidity', 'wind_speed', 'rain', 'precip', 'visibility', 'pressure']
    pred_data = pd.DataFrame()
    hours = 0
    it = 0
    row = {}

    while hours < 3:
        timestamp = str(data['features'][it]['properties']['timestamp'])
        dt = datetime.fromisoformat(timestamp)

        date = dt.date()
        hour = (int(dt.time().strftime('%H'))+20)%24
        if int(dt.time().strftime('%H')) < hour:
            date = date-timedelta(days=1)
        if data['features'][it]['properties']['temperature']['value'] is not None and data['features'][it]['properties']['dewpoint']['value'] is not None:
            temp = round(float(data['features'][it]['properties']['temperature']['value'])*9.0/5.0+32,2)
    
            dewPoint = round(float(data['features'][it]['properties']['dewpoint']['value'])*9.0/5.0,2)+32
    
            windSpeed = 0
            w = data['features'][it]['properties']['windSpeed']['value']
            if w is not None:
                windSpeed = round(float(data['features'][it]['properties']['windSpeed']['value'])*0.621371,2)
    
            pressure = float(data['features'][it]['properties']['barometricPressure']['value'])
    
            visibility = int(data['features'][it]['properties']['visibility']['value']*0.000621371)
    
            precip = 0
            p = data['features'][it]['properties']['precipitationLastHour']['value']
            if p is not None:
                precip = round(float(data['features'][it]['properties']['precipitationLastHour']['value'])*0.0393701,3)
            humidity = round(float(data['features'][it]['properties']['relativeHumidity']['value'])/100.0,2)
    
            realFeel = temp
            if temp>=80 and data['features'][it]['properties']['heatIndex']['value'] is not None:
                realFeel = int(data['features'][it]['properties']['heatIndex']['value'])*9.0/5.0+32
            elif temp<=50 and data['features'][it]['properties']['windChill']['value'] is not None:
                realFeel = int(data['features'][it]['properties']['windChill']['value'])*9.0/5.0+32,
    
            rain = isRaining(data['features'][it]['properties']['textDescription'])

            vals = [date,hour,temp,realFeel,dewPoint,humidity,windSpeed,rain,precip,visibility,pressure]
            
            for i in range(len(vals)):
                row[f'{hours} {types[i]}'] = vals[i]
            
            hours+=1
        it+=1
    if row is not None:
        pred_data = pd.concat([pred_data, pd.DataFrame([row])], ignore_index=True)
        pred_data = labeling(pred_data)
        return f'{ob_station} has a {round(model.predict(pred_data)[0][0]*100,2)}% chance of precipitation in the next hour'
                



