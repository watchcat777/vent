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


converter_pub = 1000

frequency_pub = 2000

feedback_hot1 = 3000

feedback_hot2 = 3000

feedback_cold1 = 3500

feedback_cold2 = 3500

temperature1 = 4000

temperature2 = 4000

temperature3 = 5000

temperature4 = 5000

humidity1 = 4500

humidity2 = 4500


# publish state every INTERVAL seconds
state_pub_counter_interval = 10
state_pub_counter = state_pub_counter_interval


def on_connect(client, obj, flags, rc):
    print('Connected')

    client.subscribe('in/vent_state', qos = 1)
    client.subscribe('in/t_auto', qos = 1)
    
    client.subscribe('in/converter', qos = 1)
    client.subscribe('converter_pub', qos = 1)
    
    client.subscribe('in/frequency', qos = 1)
    client.subscribe('frequency_pub', qos = 1)

    client.subscribe('in/hot_valves', qos = 1)
    client.subscribe('in/cold_valves', qos = 1)
    client.subscribe('feedback_hot1', qos = 1)
    client.subscribe('feedback_hot2', qos = 1)
    client.subscribe('feedback_cold1', qos = 1)
    client.subscribe('feedback_cold2', qos = 1)

    client.subscribe('temperature1', qos = 1)
    client.subscribe('temperature2', qos = 1)
    client.subscribe('temperature3', qos = 1)
    client.subscribe('temperature4', qos = 1)

    client.subscribe('humidity1', qos = 1)
    client.subscribe('humidity2', qos = 1)
    
    client.publish('vent_state', 'Core connected')

    
def on_message(client, userdata, msg):

    global state, t_auto, converter, converter_pub, frequency, frequency_pub, hot_valves,  feedback_hot1, feedback_hot2, cold_valves, feedback_cold1, feedback_cold2, temperature1, temperature2, temperature3, temperature4, humidity1, humidity2

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


    elif msg.topic == 'converter_pub':

        if msg.payload == b'ON':

            converter_pub = 'ON'

        elif msg.payload == b'OFF':

            converter_pub = 'OFF'

        elif msg.payload == b'RS485 USB ERROR':

            converter_pub = 'ERROR'

        elif msg.payload == b'RS485 READ ERROR':

            converter_pub = 'ERROR'

            
    elif msg.topic == 'in/frequency':

        if state == 'AUTO':

            client.publish('frequency_pub', 'Switch to MANUAL!')

        elif state == 'MANUAL':

            config['CORE']['frequency'] = str(int(msg.payload))
            with open('config.ini', 'w') as configfile:
                config.write(configfile)

            client.publish('frequency_com', msg.payload)


    elif msg.topic == 'frequency_pub':

        if msg.payload == b'RS485 USB ERROR':

            frequency_pub = 'ERROR'

        elif msg.payload == b'RS485 READ ERROR':

            frequency_pub = 'ERROR'

        else:

            frequency_pub = int(msg.payload)


    elif msg.topic == 'in/hot_valves':

        if state == 'AUTO':

            client.publish('feedback_hot1', 'Switch to MANUAL!')
            time.sleep(1)
            client.publish('feedback_hot2', 'Switch to MANUAL!')

        elif state == 'MANUAL':

            config['CORE']['hot_valves'] = str(int(msg.payload))
            with open('config.ini', 'w') as configfile:
                config.write(configfile)

            client.publish('hot_valves_com', msg.payload)


    elif msg.topic == 'in/cold_valves':

        if state == 'AUTO':

            client.publish('feedback_cold1', 'Switch to MANUAL!')
            time.sleep(1)
            client.publish('feedback_cold2', 'Switch to MANUAL!')

        elif state == 'MANUAL':

            config['CORE']['cold_valves'] = str(int(msg.payload))
            with open('config.ini', 'w') as configfile:
                config.write(configfile)

            client.publish('cold_valves_com', msg.payload)


    # valves pubs
    

    elif msg.topic == 'temperature1':

        temperature1 = int(msg.payload)


    # t, h pubs

        

        
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

    print(str(converter_pub) + ' ' + str(frequency_pub) + ' ' + str(feedback_hot1) + ' ' + str(feedback_hot2) + ' ' + str(feedback_cold1) + ' ' + str(feedback_cold2))
    
    print(str(temperature1) + ' ' + str(humidity1) + ' ' + str(temperature2) + ' ' + str(humidity2) + ' ' + str(temperature3) + ' ' + str(temperature4))
    

    state_pub_counter -= 1

    if state_pub_counter < 1:

        state_pub_counter = state_pub_counter_interval
   
        client.publish('vent_state_pub', state)
        
        time.sleep(1)

        client.publish('t_auto_pub', t_auto)

        time.sleep(1)

    print(state_pub_counter)
    
    
    time.sleep(3)


