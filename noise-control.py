BLINKING_RATE_READY = 1.5
BLINKING_RATE_WAITING = 0.1
BLINKING_RATE_LOADING = 0.3
PIN_BUTTON=3
PIN_BLUE=23
PIN_RED=24

import os,sys,time,signal,subprocess,json
import rtmidi_python as rtmidi
import RPi.GPIO as GPIO

midi_in = [rtmidi.MidiIn()]
attached = set()
attached.add(midi_in[0].ports[0])
p = None

with open('noise-control.json') as map_file:
	map = json.load(map_file)

def button_callback(channel):
	kill_cmd(None)
	GPIO.cleanup()
	log('shutdown now!')
	os.system("shutdown now -h")

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_RED, GPIO.OUT)
GPIO.setup(PIN_BLUE, GPIO.OUT)
GPIO.setup(PIN_BUTTON, GPIO.IN, GPIO.PUD_UP)
GPIO.add_event_detect(PIN_BUTTON, GPIO.FALLING, callback=button_callback,bouncetime=500)

def set_led_status(status):
	GPIO.output(PIN_RED, status)
	GPIO.output(PIN_BLUE, not status)
	return not status

def log(message):
	print message
		
def signal_handler(signum, frame):
	global blinking_rate
	if signum == signal.SIGUSR1:
		log ('Child ready')
		blinking_rate = BLINKING_RATE_READY
	elif signum == signal.SIGUSR2:
		log ('Child busy')
		blinking_rate = BLINKING_RATE_WAITING
	elif signum == signal.SIGINT or signum == signal.SIGQUIT:
		log ('good bye!')
		GPIO.cleanup()
		sys.exit(0)

def exec_cmd(device):
	global p
	device_name = device.split(' ')[0]
	if device_name in map:
		p = subprocess.Popen(args = map[device_name])

def kill_cmd(device):
	global p
	log('killing %d' % p.pid)
	if not p is None and p.poll() is None:
		p.send_signal(signal.SIGINT)
		time.sleep(0.5)

def attach_device(port):
	log('attaching ' + port)
	global blinking_rate
	blinking_rate = BLINKING_RATE_LOADING
	attached.add(port)
	exec_cmd(port)

def dettach_device(port):
	log('dettaching ' + port)
	global blinking_rate
	blinking_rate = BLINKING_RATE_LOADING
	log('loading')
	kill_cmd(port)
	attached.remove(port)


log('loading')
blinking_rate = BLINKING_RATE_LOADING
blinking = False

signal.signal(signal.SIGUSR1, signal_handler) 
signal.signal(signal.SIGUSR2, signal_handler) 
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGQUIT, signal_handler)

while True:
	# if something has changed in midi ports
	if len(set(midi_in[0].ports) ^ attached) > 0:
		ports = set(midi_in[0].ports)
		# attach if there is new elements
		for i in ports - attached:
			attach_device(i)
		# dettach if necessary
		for i in attached - ports:
			dettach_device(i)

	blinking = set_led_status(blinking)
	time.sleep(blinking_rate)

