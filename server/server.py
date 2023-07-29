import paho.mqtt.client as mqtt
import json
import psycopg2
import os

DATABASE_URL = "postgres://{user}:{password}@{hosturl}:{port}".format(
    user="postgres", password="password", hosturl="timescaleDB", port=5432
)

def databaseInit():
    query_create_sensordata_table = """CREATE TABLE IF NOT EXISTS datalogger(
                                        time TIMESTAMPTZ NOT NULL,
                                        pressure DOUBLE PRECISION,
                                        altitude DOUBLE PRECISION,
                                        seaLevelAltitude DOUBLE PRECISION,
                                        humidity DOUBLE PRECISION,
                                        lightIntensity INTEGER,
                                        distanceHCSR04 DOUBLE PRECISION,
                                        temperature DOUBLE PRECISION
                                        gasValue DOUBLE PRECISION
                                    );
                                    """

    query_create_sensordata_hypertable = (
        "SELECT create_hypertable('datalogger', 'time');"
    )
    databaseInsert(query_create_sensordata_table)
    databaseInsert(query_create_sensordata_hypertable)


def on_connect(mqttc, obj, flags, rc):
    mqttc.subscribe('topic/data')
    print("rc: "+str(rc))
def on_message(mqttc, obj, msg):
    returnDataFromMqttBroker(msg.payload)
def on_publish(mqttc, obj, mid):
    print("mid: "+str(mid))
def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))
def on_log(mqttc, obj, level, string):
    print(string)
def on_disconnect(mqttc,obj,rc):
    print("discoonected reconnecting")
    print(obj)
    print(rc)
    mqttc.connect('localhost', 1883, 6)


mqttc = mqtt.Client("database")
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.on_disconnect = on_disconnect
mqttc.on_log = on_log
# mqttc.connect('mosquitto-docker', 9001, 60)
mqttc.connect('mosquitto', 1883, 60)
print(f'trying to connect.....')



def databaseInsert(query):
    with psycopg2.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        try:
            conn.commit()
        except:
            print("eroor in query")

def insertDataToDB(data):
    values = []
    for value in data.values():
        values.append(value)
    valuesStr = f"'{values[0]}',{values[1]},{values[2]},{values[3]},{values[4]},{values[5]},{values[6]},{value[7]},{values[8]}"
    insert_query = f"INSERT INTO datalogger ({','.join(data.keys())}) VALUES ({valuesStr}) "
    databaseInsert(insert_query)
    # print(insert_query)


def returnDataFromMqttBroker(data):
    dataToDict=json.loads(data)
    # print(dataToDict)
    insertDataToDB(dataToDict)



if __name__ == "__main__":
    #  databaseInit()
     mqttc.loop_forever()