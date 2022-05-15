# system libs
import threading
import gpio
import json
import fs
# networking
from zdm import zdm
from networking import wifi
from protocols import http, mqtt
# custom drivers
from drivers import hcsr04, hx711, servo, pump
# custom drivers for arducam
from drivers.arducam import arduchip, OV2640
from drivers import arducam_setup
# files
import pins
import credentials

print("Retrieving configuration parameters...")
"""
f = fs.FileIO("/zerynth/config.json", "rb")
data = f.read()
configs = json.loads(data)
f.close()

print(configs)
"""
FOOD_THRESH = 1.0
WATER_THRESH = 0
ANGLE = 40
FOOD_STORAGE_THRESH = 3.0
WATER_STORAGE_THRESH = 20.0


print("Initializing drivers...")
gpio.mode(pins.PIR_PIN, INPUT)
food_us = hcsr04.HCSR04(pins.TRIG_FS, pins.ECHO_FS)
water_us = hcsr04.HCSR04(pins.TRIG_WS, pins.ECHO_WS)
load_cell = hx711.HX711(pins.LC_DT, pins.LC_SCK)
servo = servo.Servo(pin=pins.SERVO_PIN)
pump_system = pump.Pump(pump_pin=pins.PUMP, level_pin=pins.WL_SENS, level_power_pin=pins.WL_POW)

print("Initializing camera...")
arduchip = arduchip.Arduchip(nss=D5)
internal_sensor = OV2640.OV2640()
arducam_setup.init_camera(arduchip, internal_sensor)


print("Initializing load cell...")
print("Starting calibration...")
try:
    load_cell.tare()

    print("Place tare")
    sleep(5000)
    print("Calibrating...")
    res = load_cell.average() - load_cell.offset
    load_cell.scale = res / 10
    print("Calibration complete")
except IOError as e:
    print("Load cell error, please check the wiring.")

print("Configuring MQTT client...")
mqtt_client = mqtt.MQTT("test.mosquitto.org", "09")

def calibration(client : mqtt.MQTT, topic : str, message):
    print(topic)

    if 'tare' in topic:
        print("Tare...")
        load_cell.tare()
    elif 'calibration' in topic:
        if message == 'ACK':
            print("Continua calibrazione")
            # se ricevo il peso calibro
            load_cell.calibrate()
        elif message != 'PlaceWeight':
            print("Calibrazione in corso")
            # salvo il peso noto ricevuto tramite mqtt
            load_cell.known_weight = float(message)
            # chiamo la funzione tare a vuoto
            load_cell.tare()
            # invio un messaggio chiedendo di mettere un peso
            client.publish("birdhub/loadCell/calibration", 'PlaceWeight')
            

mqtt_client.on("birdhub/loadCell/+", calibration)
# aggiungere le altre callback


#### THREADING ####

lock = threading.Lock()
# da cambiare
def pir_routine():
    client = http.HTTP()

    CAM_ROUTE = "http://192.168.1.128:5000/cam"

    while True:
        pir = gpio.get(pins.PIR_PIN)
        if pir == LOW:
            sleep(500)
            continue
        sleep(2000)
        agent.publish({"value": 1}, "pir")
        lock.acquire()
        buf = arduchip.take_photo()
        lock.release()
        while True:
            print("Sending...")

            try:
                res = client.post(CAM_ROUTE, body=bytes(buf),  headers={'Content-Type': 'application/octet-stream'})
                if res.status == 200:
                    print("Data has been received!")
                    break

            except Exception as e:
                print(e)
                print("Retrying...")
            sleep(500)

        while pir == HIGH:
            pir = gpio.get(pins.PIR_PIN)

def check_up():
    
    CHECKING_TIME = 5000
    
    while True:
        
        print("Sending data to the cloud...")
        lock.acquire()
        try:
            
            food_storage = food_us.get_distance()
            agent.publish({"value": food_storage}, "food_storage")
            water_storage = water_us.get_distance()
            agent.publish({"value": water_storage}, "water_storage")
        except TimeoutError as e:
            print("Ultrasound is not responding, please check the wiring.")

    
        if food_storage > FOOD_STORAGE_THRESH:
            try: 
                count = 0
                while not load_cell.is_ready():
                    count = count + 1
                    if count > 100:
                        print("Load cell is not responding.")

                print("Reading from load cell...")
                bowl_level = load_cell.read()
                print("Food level inside the bowl:", bowl_level)
        
                while bowl_level < FOOD_THRESH:

                    while gpio.get(pins.PIR_PIN) == HIGH:
                        sleep(500)

                    print("Pouring food...")
                    servo.rotate_and_go_back(ANGLE)

                    if load_cell.is_ready():
                        bowl_level = load_cell.read()
                        print("Food level inside the bowl:", bowl_level)
                
            except IOError as e:
                print("Internal load cell error.")
                
                
        if water_storage > WATER_STORAGE_THRESH:

            water_level = pump_system.get_water_level()
            print("Water level:", water_level)

            while water_level < WATER_THRESH:
                print("Pumping...")
                while gpio.get(pins.PIR_PIN) == HIGH:
                        sleep(500)
                pump_system.pump()
                water_level = pump_system.get_water_level()
        
        print("Checkup's over!")
        lock.release()
        sleep(CHECKING_TIME)
        
while True:
    
    try:
        print("Configuring wifi...")
        wifi.configure(
            ssid=credentials.ssid,
            password=credentials.passwd)
        print("Connecting to wifi...")
        wifi.start()
        print("Connected!",wifi.info())

        mqtt_client.connect()
        while not mqtt_client.is_connected():
            sleep(1000)

        print("MQTT client is connected.")

        print("Starting threads...")
    
        agent = zdm.Agent()
        agent.start()

        while not agent.connected():
            print("Waiting for agent to start...")
            sleep(1000)

        print("ZDM is online: ", agent.online())

        pir_t = threading.Thread(target=pir_routine)
        pir_t.start()

        check_t = threading.Thread(target=check_up)
        check_t.start()

        mqtt_client.loop()
        # inserire qui registrazioni callback
        # CHECKING_TIME = 10*60*1000    

        # quando da un guru meditation error: o una eccezione è stata rilanciata oppure
        # ci si sta sconnettendo dal wifi quando non si dovrebbe
        # importante se un thread si blocca fare attenzione che l'altro non sia in 
        # attesa attiva tipo while TRue

    except WifiBadPassword:
        print("Bad Password")
    except WifiBadSSID:
        print("Bad SSID")
    except WifiException:
        print("Generic Wifi Exception")
    except Exception as e:
        print(e)
    finally:
        pir_t.join()
        #check_t.join()
        agent.stop()
        mqtt_client.disconnect()
        wifi.stop()

    print("Reconnecting")
    sleep(5000)