#!/usr/bin/python3
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

def move(position):
    GPIO.output(5, 1)
    GPIO.output(5, 0)
    print('Move to ' + str(position))


def on_connect(client, obj, flags, rc):
    print('Connected')
    client.subscribe('hot_valves_com', qos = 1)
    client.subscribe('cold_valves_com', qos = 1)
    client.publish('vent_state', 'Valves connected')

    
def on_message(client, userdata, msg):
    
    if msg.topic == 'hot_valves_com':  

        try: 
            klapan1_value = int(msg.payload)
            if (klapan1_value >= 0 and klapan1_value <= 100):
                move(klapan1_value)
            else:
                client.publish('vent_state', 'Wrong value')
        except ValueError:
            client.publish('vent_state', 'Wrong value')
            
        
    elif msg.topic == 'cold_valves_com':

        print(msg.payload)
        
    else:
        print(msg.topic + ': ' + str(msg.payload) + str(msg.qos))

        
client = mqtt.Client(client_id = 'Valves', clean_session = True)
client.on_connect = on_connect
client.on_message = on_message
client.connect('127.0.0.1', 1883, 300)
#client.loop_forever()
client.loop_start()


while True:

    # Read all the ADC channel values in a list.
    values = [0]*8
    
    for i in range(8):
        # The read_adc function will get the value of the specified channel (0-7).
        values[i] = mcp.read_adc(i)
        
    # Print the ADC values.

    interpolate1 = round(values[0] / 10.24)
    print(values[0])
    print(interpolate1)
    client.publish('feedback_hot1', interpolate1)
        
    time.sleep(5)


