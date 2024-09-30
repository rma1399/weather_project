import pandas as pd
import tensorflow as tf
from keras import layers, models
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine
from sklearn.preprocessing import LabelEncoder
import json

c = open('API/info.json')
cred = json.load(c)
engine = create_engine(cred[1]['link'])

def testing_frame():
    le = LabelEncoder()

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
    
    for col in df.columns.tolist():
        tp = df[col].dtype
        if tp != 'float64' and tp != 'int64':
            df[col] = le.fit_transform(df[col])

    print(df)
    return df

training_data = testing_frame()


#def rain_prediction(): call this once the model has been trained, reqeusts, prediction, post

#nuearal network, logistical regression, decision tree
def build_neural_network():
    
    #netowrk build
    model = models.Sequential()
    model.add(layers.Flatten())
    model.add(layers.Dense(64, activation='sigmoid'))
    model.add(layers.Dense(20))

    return model

def training(model, training_data):

    model.compile(optimizer='adam',
            loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            metrics=['accuracy'])
    history = model.fit(training_data, epochs=10,
    validation_data=(training_data))


model = build_neural_network()
training(model, training_data)