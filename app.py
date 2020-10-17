from flask import Flask, render_template, request, redirect
import threading
import time
import Adafruit_DHT
import RPi.GPIO as GPIO
from time import sleep
from gpiozero import InputDevice
import requests
import json

#DHT Sensor
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 21
global count
count = 0
app = Flask(__name__)

#Light Sensor
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
pin_to_circuit = 22

 



def rc_time (pin_to_circuit):
    
    
    counter = 0
    #Output on the pin for 
    GPIO.setup(pin_to_circuit, GPIO.OUT)
    GPIO.output(pin_to_circuit, GPIO.LOW)
    time.sleep(3)

    #Change the pin back to input
    GPIO.setup(pin_to_circuit, GPIO.IN)
  
    #Count until the pin goes high
    while (GPIO.input(pin_to_circuit) == GPIO.LOW):
        counter += 1
    return counter

def light():
    while True:
        print(rc_time(pin_to_circuit))
        if (rc_time(pin_to_circuit)) < 10000:
            print("Enough light")
            message = str ("Enough light")
        else:
            print("Not enough light")
            message=str("Not enough light")
        break
    return(message)

def temperature():
    while True: 
        humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
        sleep(2)
        if humidity is not None and temperature is not None:
            print("Temp={0:0.1f}C Humidity={1:0.1f}%".format(temperature, humidity))
            tempvalues=str("Temp={0:0.1f}C Humidity={1:0.1f}%".format(temperature, humidity))
        else:
            print("Sensor failure. Check wiring.")
            tempvalues=str("ERROR")
        time.sleep(2)
        return(tempvalues)


def water():
    no_rain = InputDevice(27)
    buzzer=12
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(buzzer,GPIO.OUT)
    while True:
        if not no_rain.is_active:
            print("Water detected")
        elif no_rain.is_active:
        #while True:
        #global waterstatus
            global count
            print("No water for" , count , "hours")
            count = count + 1
            if count == 3:
                GPIO.output(buzzer,GPIO.HIGH)
                print ("Beep")
                GPIO.setup(11,GPIO.OUT)
                print ("LED on")
                GPIO.output(11,GPIO.HIGH)
                time.sleep(1)
        #global buzzer
        #buzzer = True
                print("No water for" , count , "hours")
                count = 0
            #else:
                #continue
        sleep(5) 
        
        
        
        return(count)


@app.route('/', methods =['POST', 'GET'])
def index():
    
    if request.method == 'POST': 
        city = request.form['city'] 
    else: 
        # for default name mathura 
        city = 'Portsmouth'
  
    # your API key will come here 
    api = '1f3c808f2bac07877b5c140362cfc84c'
  
    # source contain json data from api 
    #source = requests.urlopen('http://api.openweathermap.org/data/2.5/weather?q =' + city + '&appid =' + api).read() 
    source = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=metric&appid=1f3c808f2bac07877b5c140362cfc84c'
    # converting JSON data to a dictionary 
    #list_of_data = json.loads(source) 
    r = requests.get(source).json()
    # data for variable list_of_data 
    data = {
            'city' : city,
            'temperature' : r['main']['temp'],
	    'temp_max': r['main']['temp_max'],
	    'temp_min': r['main']['temp_min'],
            'description' : r['weather'][0]['description'],
            'wind_speed': r['wind']['speed'],
	    
            
        }
    print(data) 


    tempvalues = temperature()
    count = water()
    message = light()
    
    return render_template('index.html',tempvalues=tempvalues,count=count,message=message,data=data)
    

@app.route('/disable_buzzer',methods=["GET","POST"])
def disable_buzzer():
    GPIO.setwarnings(False)
    #Select GPIO mode
    GPIO.setmode(GPIO.BCM)
    #Set buzzer - pin 23 as output
    buzzer=12
    GPIO.setup(buzzer,GPIO.OUT)
    GPIO.output(buzzer,GPIO.LOW)
    
    print ("No Beep")
    print ("LED off")
    GPIO.output(11,GPIO.LOW)
    
    global motionsensor
    motionsensor = False
    
    tempvalues = temperature()
    message = light()
    count = water()
    GPIO.cleanup
    return render_template('index.html',tempvalues=tempvalues,count=count,message=message)
"""
@app.route('/disable_motion',methods=["GET","POST"])
def disable_motion():
"""
@app.route('/enable_motion',methods=["GET","POST"])
def enable_motion():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.IN) 

    global motionsensor
    motionsensor = True
    
    buzzer=12

    GPIO.setup(buzzer,GPIO.OUT)
    while motionsensor is True:
        i = GPIO.input(4)
        if i == 0:
            print ("no motion")
            sleep(5)
        elif i == 1:
            print ("motion")
	    
            GPIO.output(buzzer,GPIO.HIGH)
            print ("Beep")
            GPIO.setup(11,GPIO.OUT)
            print ("LED on")
            GPIO.output(11,GPIO.HIGH)
            time.sleep(1)
	    
            sleep(5)
    return render_template('index.html',tempvalues=tempvalues,count=count,message=message)







GPIO.cleanup





if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=False, threaded=True)
