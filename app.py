import requests
import os
import glob
import time

from picamera import PiCamera
from time import sleep
import RPi.GPIO as GPIO

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
camera = PiCamera()
camera.resolution = (2592, 1944)
camera.contrast = 40

button = 11
blueled = 18
greenled = 16
redled = 13

GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(greenled, GPIO.OUT, initial = 0)
GPIO.setup(redled, GPIO.OUT, initial = 0)
GPIO.setup(blueled, GPIO.OUT, initial = 0)

def read_temp_raw():
    f = open(device_file, 'r')
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
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_f


while(1):
    tempHolder = round(read_temp(), 2)
    if tempHolder < 73:
        GPIO.output(greenled, 0)
        GPIO.output(redled, 0)
        GPIO.output(blueled, 1)
    if (tempHolder >=73 and tempHolder < 75):
        GPIO.output(redled, 0)
        GPIO.output(blueled, 0)
        GPIO.output(greenled, 1)
    if tempHolder >= 75:
        GPIO.output(greenled, 0)
        GPIO.output(blueled, 0)
        GPIO.output(redled, 1)
    camera.start_preview()
    sleep(2)
    camera.capture('/home/pi/Desktop/production/enviropifinalcode/pic_to_send.jpg')
    camera.stop_preview()
    picToSend = {'file': open('pic_to_send.jpg', 'rb')}
    dataToSend = {'name':'Board Room', 'temperature':tempHolder, 'location':3}
    source = requests.post('https://enviropi-backend.herokuapp.com/images', files=picToSend, data=dataToSend)
    print(source.content)
    print(source.status_code)
    print(tempHolder)
    sleep(15)
