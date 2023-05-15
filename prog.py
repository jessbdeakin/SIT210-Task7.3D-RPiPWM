import RPi.GPIO as gpio
import time

READ_PULSE_TIMEOUT = 0xFFFFFFFF
def readPulse(pin, timeout):
    
    if gpio.input(pin) != gpio.HIGH:    
        edgeDetected = gpio.wait_for_edge(pin, gpio.RISING, timeout=timeout)
        
        if edgeDetected is None:
            print("Timed out before pulse start")
            return READ_PULSE_TIMEOUT
        
    start = time.time_ns()
        
    edgeDetected = gpio.wait_for_edge(pin, gpio.FALLING, timeout=timeout)
    
    if edgeDetected is None:
        print("Timed out before pulse end")
        return READ_PULSE_TIMEOUT
        
    return time.time_ns() - start

MS_FACTOR = 1000.0
NS_FACTOR = 1000000000.0
US_FACTOR = 1000000.0

##################################

ledPin = 11
echoPin = 13
triggerPin = 15

##################################

gpio.setmode(gpio.BOARD)
gpio.setup([ledPin, triggerPin], gpio.OUT)
gpio.setup(echoPin, gpio.IN)

ledPwm = gpio.PWM(ledPin, 1000)
ledPwm.start(0)

gpio.output([ledPin, triggerPin], gpio.LOW)

##################################

try:
    while True:

        # Cause 10us pulse on trigger pin to start read
        gpio.output(triggerPin, gpio.HIGH)
        time.sleep(10 / US_FACTOR)
        gpio.output(triggerPin, gpio.LOW)

        # Determine the length of the pulse returned on the echo pin
        distance = readPulse(echoPin, 1000)
        distance /= (NS_FACTOR / US_FACTOR)
        
        # Normalise into some range
        normalisedDistance = (distance - 200) / 2000
        if normalisedDistance < 0:
            normalisedDistance = 0
        if normalisedDistance > 1:
            normalisedDistance = 1
        
        # Modulate LED duty cycle based on normalised distance
        dutyCycle = 100 * (1 - normalisedDistance)
        ledPwm.ChangeDutyCycle(dutyCycle)
        
        # Wait 50~60 ms to ensure echo signal is low again, per datasheet
        time.sleep(60 / MS_FACTOR)

except KeyboardInterrupt:
    pass

gpio.cleanup()
