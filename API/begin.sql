CREATE TABLE hourly_data (
    dat DATE NOT NULL,
    tim INT NOT NULL,
    temp INT NOT NULL,
    real_feel FLOAT NOT NULL,
    dew_point INT NOT NULL,
    humidity FLOAT NOT NULL,
    wind_speed VARCHAR(20) NOT NULL,
    rain BOOLEAN NOT NULL,
    precip FLOAT NOT NULL,
    visibility FLOAT NOT NULL,
    pressure FLOAT NOT NULL
)

