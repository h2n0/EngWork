from LCD import *
import RPi.GPIO as GPIO
import time as t

version = "0.2"
lcd = LCD()
h = GPIO.HIGH
l = GPIO.LOW

encoderA = 16
encoderB = 21
encoderButton = 20
encoderVal = 0
lastencoded = 0
stage = 1
setup = True

motorL = 19
motorR = 26

FPH = 0
H = 0

#Setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(encoderA,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(encoderB,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(encoderButton,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(motorL,GPIO.OUT)
GPIO.setup(motorR,GPIO.OUT)
GPIO.output(motorL,l)
GPIO.output(motorR,l)
def wipe():
	lcd.clear()
	lcd.home()

def init():
	lcd.message("Timelaspe\nCommand v{}".format(version))
	t.sleep(3)
	wipe()
	draw()

def moveLeft(d):
	global motorL
	print("Motor Left")
	GPIO.output(motorL,GPIO.HIGH)
	t.sleep(d)
	GPIO.output(motorL,GPIO.LOW)

def moveRight(d):
	global morotR
	print("Motor Right")
	GPIO.output(motorR,GPIO.HIGH)
	t.sleep(d)
	GPIO.output(motorR,GPIO.LOW)

def updateEncoder(c):
	global encoderA, encoderB, lastencoded, encoderVal
	rota = 0
	rotb = 0
	if(GPIO.input(encoderA)):
		rota = 1

	if(GPIO.input(encoderB)):
		rotb = 1
	
	rotc = rota ^ rotb
	encoded = rota * 4 + rotb * 2 + rotc * 1
	delta = (encoded - lastencoded)
	if(delta == 1):
		encoderVal = encoderVal + 1
	elif(delta == 3):
		encoderVal = encoderVal - 1

	lastencoded = encoded

def button(c):
	global FPH,H,stage,encoderVal,setup
	if(stage == 1):
		FPH = encoderVal
		stage = stage + 1
		encoderVal = 0
	elif(stage == 2):
		H = encoderVal
		stage = stage + 1
		encoderVal = 0
	elif(stage == 3):
		op = encoderVal % 2
		if(op == 0):
			setup = False
			stage = 0
			encoderVal = 0
		else:
			stage = 1
			encoderVal = 0

def draw():
	global encoderVal,encoderA,encoderB, stage, FPH, H, encoderButton, setup, re
	GPIO.add_event_detect(encoderA,GPIO.BOTH,callback=updateEncoder)
	GPIO.add_event_detect(encoderB,GPIO.BOTH,callback=updateEncoder)
	GPIO.add_event_detect(encoderButton,GPIO.FALLING,callback=button,bouncetime=3)
	try:
		while True:
			wipe()
			#button = GPIO.input(encoderButton)
			if setup:
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
					else:
						lcd.message("Are you sure?\n  Yes  [No]")
			else:
				print("Running")
				moveRight(10)
				moveLeft(10)

			t.sleep(0.3)
	finally:
		GPIO.cleanup()
			
	
init()
print("Test")
