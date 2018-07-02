#!/usr/bin/python3

# sensors posting interval
delay = 2

import time, os, glob
import paho.mqtt.client as mqtt
import Adafruit_DHT

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device2_folder = glob.glob(base_dir + '28*')[1]
device_file = device_folder + '/w1_slave'
device2_file = device2_folder + '/w1_slave'


def on_connect(client, obj, flags, rc):
    print('Connected')
    client.publish('vent_state', 'Sensors connected')

        
client = mqtt.Client(client_id = 'Sensors', clean_session = True)
client.on_connect = on_connect
#client.on_message = on_message
client.connect('127.0.0.1', 1883, 300)
#client.loop_forever()
client.loop_start()


def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp2_raw():
    f = open(device2_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

def read_temp2():
    lines = read_temp2_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp2_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c
	
while True:

    # humidity1, temperature1 = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 21)
    humidity1, temperature1 = Adafruit_DHT.read(Adafruit_DHT.DHT22, 21)
    
    if humidity1 is not None and temperature1 is not None:
        print('Temp={0:0.2f}C  Humidity={1:0.2f}%'.format(temperature1, humidity1))
        client.publish('temperature1', "{:.2f}".format(temperature1))
        time.sleep(delay)
        client.publish('humidity1', "{:.2f}".format(humidity1))
    else:
        # add errors handling
        print('Failed to get reading. Try again!')


    humidity2, temperature2 = Adafruit_DHT.read(Adafruit_DHT.DHT22, 20)

    if humidity2 is not None and temperature2 is not None:
        print('Temp = {0:0.2f}C  Humidity = {1:0.2f}%'.format(temperature2, humidity2))
        client.publish('temperature2', "{:.2f}".format(temperature2))
        time.sleep(delay)
        client.publish('humidity2', "{:.2f}".format(humidity2))
    else:
        print('Failed to get reading. Try again!')


    t3 = read_temp()
    print(t3)
    client.publish('temperature3', "{:.2f}".format(t3))
    time.sleep(delay)

    
    t4 = read_temp2()
    print(t4)
    client.publish('temperature4', "{:.2f}".format(t4))
    time.sleep(delay)
