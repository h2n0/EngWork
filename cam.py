from LCD import *
import RPi.GPIO as GPIO
import time as t
import subprocess as sub

version = "0.3A"
lcd = LCD()
h = GPIO.HIGH
l = GPIO.LOW
delay = 0.4
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
totalFrames = 0
currentFrame = 0

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

def getCurrentTime():
	return t.time()
	
def init():
	lcd.message("Timelaspe\nCommand V{}".format(version))
	t.sleep(3)
	wipe()
	draw()

def moveLeft(d):
	global motorL
	GPIO.output(motorL,GPIO.HIGH)
	t.sleep(d)
	GPIO.output(motorL,GPIO.LOW)

def revolveMotorLeft(r):
	delta = r * 30
	moveLeft(delta)

def moveRight(d):
	global morotR
	GPIO.output(motorR,GPIO.HIGH)
	t.sleep(d)
	GPIO.output(motorR,GPIO.LOW)

def revolveMotorRight(r):
	delta = r * 30
	moveRight(delta)

def updateEncoder(c):
	global encoderA, encoderB, lastencoded, encoderVal
	rota = 0
	rotb = 0
	if(GPIO.input(encoderA)):
		rota = 1

	if(GPIO.input(encoderB)):
		rotb = 1

	dec = 2	
	rotc = rota ^ rotb
	encoded = rota * 4 + rotb * 2 + rotc * 1
	delta = (encoded - lastencoded)
	if(delta == 1):
		encoderVal = encoderVal + dec
	elif(delta == 3):
		encoderVal = encoderVal - dec

	lastencoded = encoded

def button(c):
	global FPH,H,stage,encoderVal,setup, totalFrames
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
			totalFrames = FPH * H
			print("FPH: {}, H: {}, TF: {}".format(FPH,H,totalFrames))
			setup = False
			stage = 0
			encoderVal = 0
		else:
			stage = 1
			encoderVal = 0

def getStringPercent(f,t):
	res = " [            ] "
	p = ((f/t) * 12)
	while p > 0:
		res[1+p] = "="
	return res

def compile():
	lcd.message("Comliling video")
	sub.call("ls -v *.png > stills.txt")
	try:
		sub.call("mencoder -nosound -ovc lavc -lavcopts vcodec=mpeg4:aspect=16/9:vbitrate=8000000 -vf scale=1920:1080 -o timelapse.avi -mf type=jpeg:fps=24 mf://@stills.txt")
	except:
		lcd.message("Failed to \ncompile video")
		return
	lcd.messgae("Video compiled:\nSucessfully")


def draw():
	global encoderVal,encoderA,encoderB, stage, FPH, H, setup,delay,currentFrame,totalFrames
	sub.call("rm Pic*.png",shell=True)
	GPIO.add_event_detect(encoderA,GPIO.BOTH,callback=updateEncoder)
	GPIO.add_event_detect(encoderB,GPIO.BOTH,callback=updateEncoder)
	GPIO.add_event_detect(encoderButton,GPIO.FALLING,callback=button,bouncetime=300)
	try:
		while True:
			wipe()
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
				## 24(Pi) = 75mm
				## 75mm = 7.5cm
				## 7.5cm = motorRight(60)
				## 1cm = motorRight(60/7.5)
				## (60/7.5)/ totalFrames 
				## Time delay =  60/FPH
				framesLeft = "Pics left: {}".format(totalFrames - currentFrame)
				lcd.message(framesLeft)#+ "\n"+getStringPercent(currentFrame,totalFrames))
				start = t.time()
				cf = "-o Pic{}.png".format(currentFrame)
				sub.call("raspistill -hf " + cf,shell=True)
				d = (75/2) / totalFrames
				revolveMotorLeft(d)
				t.sleep((60 * 60)/FPH - ((t.time() - start)))
				currentFrame = currentFrame + 1
				if currentFrame > totalFrames:
					break
	
			t.sleep(delay)
		compile()
	finally:
		GPIO.cleanup()


init()
