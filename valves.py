#!/usr/bin/python3

# feedbacks posting interval
delay = 10

import time, Adafruit_MCP3008
import Adafruit_GPIO.SPI as SPI
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)

GPIO.output(5, 0)
GPIO.output(6, 0)
GPIO.output(13, 0)
GPIO.output(19, 0)

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
values = [0]*8

hot_flag = 0
hot_valves_value = 0

cold_flag = 0
cold_valves_value = 100

def move_hot(new_position):
    print('Move hot to ' + str(new_position))
    
    GPIO.output(13, 1)
    time.sleep(3)
    hot_position = round(mcp.read_adc(0) / 4.3)
    GPIO.output(13, 0)

    if hot_position > new_position:
        
        while (mcp.read_adc(0) / 4.3) > new_position:
            GPIO.output(13, 1)
            
            hot_position1 = round(mcp.read_adc(0) / 4.3) 
            print(hot_position1)
            hot_position2 = round(mcp.read_adc(2) / 4.3) 
            print(hot_position2)
            
            client.publish('feedback_hot1', hot_position1)
            time.sleep(1.5)
            client.publish('feedback_hot2', hot_position2)
            time.sleep(1.5)
            
    elif hot_position < new_position:
        
        while (mcp.read_adc(0) / 4.3) < new_position:
            GPIO.output(19, 1)

            hot_position1 = round(mcp.read_adc(0) / 4.3) 
            print(hot_position1)
            hot_position2 = round(mcp.read_adc(2) / 4.3) 
            print(hot_position2)
            
            client.publish('feedback_hot1', hot_position1)
            time.sleep(1.5)
            client.publish('feedback_hot2', hot_position2)
            time.sleep(1.5)

    hot_position1 = round(mcp.read_adc(0) / 4.3) 
    print(hot_position1)
    hot_position2 = round(mcp.read_adc(2) / 4.3) 
    print(hot_position2)
            
    client.publish('feedback_hot1', hot_position1)
    time.sleep(1.5)
    client.publish('feedback_hot2', hot_position2)
    time.sleep(1.5)
            
    GPIO.output(13, 0)
    GPIO.output(19, 0)
    


def on_connect(client, obj, flags, rc):
    print('Connected')
    client.subscribe('in/hot_valves', qos = 1) # hot_valves_com
    client.subscribe('in/cold_valves', qos = 1) # cold_valves_com
    client.publish('vent_state', 'Valves connected')

    
def on_message(client, userdata, msg):
    global hot_flag, cold_flag, hot_valves_value, cold_valves_value
    
    if msg.topic == 'in/hot_valves': # hot_valves_com

        try: 
            hot_valves_value = int(msg.payload)
            hot_flag = 1
        except ValueError:
            client.publish('vent_state', 'Wrong value')
            
        
    elif msg.topic == 'cold_valves_com':

        try: 
            cold_valves_value = int(msg.payload)
            cold_flag = 1
        except ValueError:
            client.publish('vent_state', 'Wrong value')

        
client = mqtt.Client(client_id = 'Valves', clean_session = True)
client.on_connect = on_connect
client.on_message = on_message
client.connect('127.0.0.1', 1883, 300)
#client.loop_forever()
client.loop_start()


while True:

    if hot_flag:
        if (hot_valves_value >= 0 and hot_valves_value <= 100):
            move_hot(hot_valves_value)
        else:
            client.publish('vent_state', 'Wrong value')  
        hot_flag = 0

    if cold_flag:
        if (cold_valves_value >= 0 and cold_valves_value <= 100):
            move_cold(cold_valves_value)
        else:
            client.publish('vent_state', 'Wrong value')  
        cold_flag = 0
        

    #if GPIO.input(13) or GPIO.input(19):
    #    values[0] = mcp.read_adc(0)
    #    interpolate1 = round(values[0] / 4.3) 
    #    print(interpolate1)
    #    client.publish('feedback_hot1', interpolate1)
    #    time.sleep(1)
    #else:
    #    print('Wait')
    #    time.sleep(1)

    #interpolate2 = round(values[2] / 4.3) 
    #print(interpolate2)
    #client.publish('feedback_hot2', interpolate2)
    #time.sleep(delay)

    #interpolate3 = round(values[4] / 4.3) 
    #print(interpolate3)
    #client.publish('feedback_cold1', interpolate3)
    #time.sleep(delay)

    #interpolate4 = round(values[6] / 4.3) 
    #print(interpolate4)
    #client.publish('feedback_cold2', interpolate4)
    #time.sleep(delay)


