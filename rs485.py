#!/usr/bin/python3
import minimalmodbus, time
import paho.mqtt.client as mqtt


def on_connect(client, obj, flags, rc):
    print('Connected')
    client.subscribe('converter_com', qos = 1)
    client.subscribe('frequency_com', qos = 1)
    client.publish('vent_state', 'RS485 connected')

    
def on_message(client, userdata, msg):
    
    if msg.topic == 'converter_com':

        if msg.payload == b'ON':
            
            # Registernumber, value, number of decimals, function code 6 or 16
            try:
                converter.write_register(8192, 2, 0, 6)
                print('Turn ON')
            except IOError:
                print('Failed to write')
                client.publish('converter_pub', 'Failed to write')
                
            
        elif msg.payload == b'OFF':
            
            # Registernumber, value, number of decimals, function code 6 or 16
            try:
                converter.write_register(8192, 1, 0, 6)
                print('Turn OFF')
            except IOError:
                print('Failed to write')
                client.publish('converter_pub', 'Failed to write')
            
        
    elif msg.topic == 'frequency_com':

        try: 
            new_frequency = int(msg.payload)
            if (new_frequency >= 0 and new_frequency <= 750):
                # Registernumber, value, number of decimals, function code 6 or 16
                try:
                    converter.write_register(8193, new_frequency, 1, 6)
                    print('New frequency: ' + str(new_frequency))
                except IOError:
                    print('Failed to write')
                    client.publish('frequency_pub', 'Failed to write')
            else:
                client.publish('vent_state', 'Wrong value')
        except ValueError:
            client.publish('frequency_pub', 'Wrong value')
        
        
    else:
        print(msg.topic + ': ' + str(msg.payload) + str(msg.qos))

        
client = mqtt.Client(client_id = 'RS485', clean_session = True)
client.on_connect = on_connect
client.on_message = on_message
client.connect('127.0.0.1', 1883, 300)
#client.loop_forever()
client.loop_start()


try:
    # port name, slave address (in decimal)
    converter = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
    print('Using /dev/ttyUSB0')
except Exception:
    try:
        converter = minimalmodbus.Instrument('/dev/ttyUSB1', 1)
        print('Using /dev/ttyUSB1')
    except Exception:
        client.publish('vent_state_pub', 'RS485 USB ERROR')
        time.sleep(1)
        client.publish('converter_pub', 'RS485 USB ERROR')
        time.sleep(1)
        client.publish('frequency_pub', 'RS485 USB ERROR')


converter.serial.baudrate = 9600


while True:
    
    # Register number, number of decimals, function code 3 or 4
    try:
        frequency = converter.read_register(8193, 1, 3)
        print('Read F: ' + str(frequency))
        client.publish('frequency_pub', str(frequency))
    except IOError:
        print('Failed to read')
        client.publish('frequency_pub', 'RS485 READ ERROR')
        time.sleep(1)
        client.publish('vent_state_pub', 'RS485 READ ERROR')

    time.sleep(3)


    # Register number, number of decimals, function code 3 or 4
    try:
        state = converter.read_register(28, 0, 3)
        print('Read S: ' + str(state))
        if state == 0:
            client.publish('converter_pub', 'OFF')
        elif state == 2:
            client.publish('converter_pub', 'ON')
    except IOError:
        print('Failed to read')
        client.publish('converter_pub', 'RS485 READ ERROR')
        time.sleep(1)
        client.publish('vent_state_pub', 'RS485 READ ERROR')
        
    time.sleep(3)


