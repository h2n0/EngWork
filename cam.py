from LCD import *
import RPi.GPIO as GPIO
import time as t

version = "0.1"
lcd = LCD()
h = GPIO.HIGH
l = GPIO.LOW

encoderA = 16
encoderB = 21
encoderButton = 20
encoderVal = 0
encoderValLast = 0
encoderALast = l
n = l

stage = 1
setup = True

FPH = 0
H = 0

#Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(encoderA,GPIO.IN)
GPIO.setup(encoderB,GPIO.IN)
GPIO.setup(encoderButton,GPIO.IN)

def wipe():
	lcd.clear()
	lcd.home()

def init():
	lcd.message("Timelaspe\nCommand v{}".format(version))
	t.sleep(3)
	wipe()
	draw()

def draw():
	global encoderVal, encoderValLast, stage, FPH, H, encoderButton, encoderA, encoderB, encoderVal, setup
	while True:
		button = GPIO.input(encoderButton)
		n = GPIO.input(encoderA)
		if ((encoderValLast == GPIO.LOW) and (n == GPIO.HIGH)):
			if (GPIO.input(encoderB) == GPIO.LOW):
				encoderVal = encoderVal - 1
			else:
				encoderVal = encoderVal + 1
		encoderValLast = n
		if setup:
			if not (encoderVal == encoderValLast):
				wipe()
				if stage == 1:#FPH setup
					FPH = encoderVal
					lcd.message("FPH: {}".format(FPH))
				
				elif stage == 2:#Hours setup
					H = encoderVal
					lcd.message("Hours: {}\nFPH: {}".format(H,FPH))

				elif stage == 3:#Confirmation
					sec = encoderVal % 2
					if sec == 0:
						lcd.message("Are you sure?\n [Yes]  No ")
						if button:
							setup = False
					else:
						lcd.message("Are you Sure?\n  Yes  [No]")
						if button:
							setup = True
							stage = 1
							FPH = 0
							H = 0
		else:
			print("Running")
			
			
	
init()
