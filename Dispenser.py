import os
import time
import ujson
import machine
import network
from umqtt.simple import MQTTClient
from machine import Pin, PWM

wifi_ssid = ""
wifi_password = ""
aws_endpoint = 
thing_name = ""
client_id = ""
private_key = ""
private_cert = ""


with open(private_cert, 'rb') as f:
    cert = f.read()
with open(private_key, 'rb') as f:
    key = f.read()


topic_pub = ""
topic_sub = ""
ssl_params = {"key": key, "cert": cert, "server_side": False}


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('Connecting to network...')
    wlan.connect(wifi_ssid, wifi_password)
    while not wlan.isconnected():
        time.sleep(1)
print('Connection successful')
print('Network config:', wlan.ifconfig())


mqtt = None
def mqtt_connect(client=client_id, endpoint=aws_endpoint, sslp=ssl_params):
    global mqtt
    mqtt = MQTTClient(client_id=client, server=endpoint, port=8883, keepalive=1200, ssl=True, ssl_params=sslp)
    try:
        print("Connecting to AWS IoT...")
        mqtt.connect()
        print("Connected")
    except Exception as e:
        print("Failed to connect to AWS IoT:", e)


SERVO_PIN = 13
servo = PWM(Pin(SERVO_PIN), freq=50)

def set_servo_angle(angle):
    duty = int(40 + (angle / 180) * 115)
    servo.duty(duty)

set_servo_angle(0)


EN_PIN1 = 21
DIR_PIN1 = 23
STEP_PIN1 = 22
enable_pin1 = Pin(EN_PIN1, Pin.OUT)
direction_pin1 = Pin(DIR_PIN1, Pin.OUT)
step_pin1 = Pin(STEP_PIN1, Pin.OUT)

def enable_motor1():
    enable_pin1.value(0)

def disable_motor1():
    enable_pin1.value(1)

def step_motor1(steps, direction, delay=0.001):
    direction_pin1.value(direction)
    for _ in range(steps):
        step_pin1.value(1)
        time.sleep(delay)
        step_pin1.value(0)
        time.sleep(delay)

EN_PIN2 = 5
DIR_PIN2 = 19
STEP_PIN2 = 18
enable_pin2 = Pin(EN_PIN2, Pin.OUT)
direction_pin2 = Pin(DIR_PIN2, Pin.OUT)
step_pin2 = Pin(STEP_PIN2, Pin.OUT)

def enable_motor2():
    enable_pin2.value(0)

def disable_motor2():
    enable_pin2.value(1)

def step_motor2(steps, direction, delay=0.001):
    direction_pin2.value(direction)
    for _ in range(steps):
        step_pin2.value(1)
        time.sleep(delay)
        step_pin2.value(0)
        time.sleep(delay)


def mqtt_subscribe(topic, msg):
    print("Message received...")
    message = ujson.loads(msg.decode('utf-8'))

    # 수신한 데이터를 숫자로 변환
    when = int(message.get("when", 0))
    name1 = int(message.get("name1", 0))
    dose1 = int(message.get("dose1", 0))
    name2 = int(message.get("name2", 0))
    dose2 = int(message.get("dose2", 0))

    print("Received Data:", when, name1, dose1, name2, dose2)


    if when == 1:
        set_servo_angle(30)
        time.sleep(1)

        if name1 == 1 and dose1 > 0:
            enable_motor1()
            step_motor1(200 * dose1, 1, 0.003)
            time.sleep(2)
            disable_motor1()

        if name2 == 2 and dose2 > 0:
            enable_motor2()
            step_motor2(200 * dose2, 1, 0.003)
            time.sleep(2)
            disable_motor2()

        set_servo_angle(0)

    elif when == 2:
        if name1 == 1 and dose1 > 0:
            enable_motor1()
            step_motor1(200 * dose1, 1, 0.003)
            time.sleep(1)
            disable_motor1()

        if name2 == 2 and dose2 > 0:
            enable_motor2()
            step_motor2(200 * dose2, 1, 0.003)
            time.sleep(1)
            disable_motor2()

    elif when == 3:
        set_servo_angle(-30)
        time.sleep(1)

        if name1 == 1 and dose1 > 0:
            enable_motor1()
            step_motor1(200 * dose1, 1, 0.003)
            time.sleep(1)
            disable_motor1()

        if name2 == 2 and dose2 > 0:
            enable_motor2()
            step_motor2(200 * dose2, 1, 0.003)
            time.sleep(1)
            disable_motor2()

        set_servo_angle(0)


def mqtt_publish(topic, message):
    try:
        print("Publishing message to AWS IoT...")
        mqtt.publish(topic, message)
        print("Message published")
    except Exception as e:
        print("Failed to publish message:", e)


try:
    mqtt_connect()
    mqtt.set_callback(mqtt_subscribe)
    mqtt.subscribe(topic_sub)
except Exception as e:
    print("Unable to connect to MQTT:", e)


while True:
    try:
        mqtt.check_msg()
    except Exception as e:
        print("Error checking message:", e)
    
    print("명령 대기중")
    time.sleep(5)

