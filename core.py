#!/usr/bin/python3
import time, configparser
import paho.mqtt.client as mqtt

config = configparser.ConfigParser()

#config['CORE'] = {'state': 'AUTO', 't_auto': '15', 'converter': 'ON', 'frequency': '5', 'hot_valves': '0', 'cold_valves': '100'}
#config['CORE']['key'] = 'value'

#with open('config.ini', 'w') as configfile:
#    config.write(configfile)

config.read('config.ini')

state = config['CORE']['state']

t_auto = config['CORE'].getint('t_auto')

converter = config['CORE']['converter']

frequency = config['CORE'].getint('frequency')

hot_valves = config['CORE'].getint('hot_valves')

cold_valves = config['CORE'].getint('cold_valves')


temperature1 = 1000

temperature2 = 1000

temperature3 = 1000

temperature4 = 1000

humidity1 = 1000

humidity2 = 1000

# publish state every INTERVAL seconds
state_pub_counter_interval = 10
state_pub_counter = state_pub_counter_interval




def on_connect(client, obj, flags, rc):
    print('Connected')

    client.subscribe('in/vent_state', qos = 1)
    client.subscribe('in/t_auto', qos = 1)
    
    client.subscribe('in/converter', qos = 1)
    client.subscribe('in/frequency', qos = 1)

    client.subscribe('feedback1', qos = 1)
    client.subscribe('feedback2', qos = 1)
    client.subscribe('feedback3', qos = 1)
    client.subscribe('feedback4', qos = 1)

    client.subscribe('temperature1', qos = 1)
    client.subscribe('temperature2', qos = 1)
    client.subscribe('temperature3', qos = 1)
    client.subscribe('temperature4', qos = 1)

    client.subscribe('humidity1', qos = 1)
    client.subscribe('humidity2', qos = 1)
    
    client.publish('vent_state', 'Core connected')

    
def on_message(client, userdata, msg):

    global t_auto, frequency, state

    if msg.topic == 'in/vent_state':

        if msg.payload == b'MANUAL':

            state = 'MANUAL'

            config['CORE']['state'] = 'MANUAL'
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            
            client.publish('vent_state_pub', state)

        elif msg.payload == b'AUTO':

            state = 'AUTO'

            config['CORE']['state'] = 'AUTO'
            with open('config.ini', 'w') as configfile:
                config.write(configfile)

            client.publish('vent_state_pub', state)



    elif msg.topic == 'in/t_auto':

        try: 
            t = int(msg.payload)
            if (t >= 0 and t <= 50):
                t_auto = t
                
                config['CORE']['t_auto'] = str(t_auto)
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)
                
                client.publish('t_auto_pub', t_auto)
            else:
                client.publish('t_auto_pub', 'Wrong value')
        except ValueError:
            client.publish('t_auto_pub', 'Wrong value')

            
    
    elif msg.topic == 'in/converter':

        if msg.payload == b'ON':

            if state == 'AUTO':

                client.publish('converter_pub', 'Switch to MANUAL!')

            elif state == 'MANUAL':

                config['CORE']['converter'] = 'ON'
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)

                client.publish('converter_com', 'ON')
            
        elif msg.payload == b'OFF':
            
            if state == 'AUTO':

                client.publish('converter_pub', 'Switch to MANUAL!')

            elif state == 'MANUAL':

                config['CORE']['converter'] = 'OFF'
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)

                client.publish('converter_com', 'OFF')

            
        
    elif msg.topic == 'in/frequency':

        if state == 'AUTO':

            client.publish('frequency_pub', 'Switch to MANUAL!')

        elif state == 'MANUAL':

            config['CORE']['frequency'] = str(msg.payload)
            with open('config.ini', 'w') as configfile:
                config.write(configfile)

            client.publish('frequency_com', str(msg.payload))


        
    else:
        print(msg.topic + ': ' + str(msg.payload) + str(msg.qos))

        
client = mqtt.Client(client_id = 'Core', clean_session = True)
client.on_connect = on_connect
client.on_message = on_message
client.connect('127.0.0.1', 1883, 300)
#client.loop_forever()
client.loop_start()


while True:

    print(state + ' ' + str(t_auto) + ' ' + converter + ' ' + str(frequency) + ' ' + str(hot_valves) + ' ' + str(cold_valves))
    

    state_pub_counter -= 1

    if state_pub_counter < 1:

        state_pub_counter = state_pub_counter_interval

        client.publish('vent_state_pub', state)
        
        time.sleep(1)

        client.publish('t_auto_pub', t_auto)

        time.sleep(1)

    print(state_pub_counter)
    
    
    time.sleep(1)


