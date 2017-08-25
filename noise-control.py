BLINKING_RATE_READY = 2
BLINKING_RATE_WAITING = 0.25
BLINKING_RATE_LOADING = 0.5

import os,time,signal,subprocess,json
import rtmidi_python as rtmidi

midi_in = [rtmidi.MidiIn()]
attached = set()
attached.add(midi_in[0].ports[0])
p = None

with open('noise-control.json') as map_file:
	map = json.load(map_file)

def set_led_status(status):
	if status:
		log('led ON')
		pass
	else:
		log('led OFF')
		pass
	return not status

def log(message):
	with open('/tmp/testeeste.log', 'a') as f:
		f.write(message)
		f.write('\n')
		f.close()
		
def signal_handler(signum, frame):
	global blinking_rate
	if signum == signal.SIGUSR1:
		log ('Child ready')
		blinking_rate = BLINKING_RATE_READY
	else:
		log ('Child busy')
		blinking_rate = BLINKING_RATE_WAITING

def exec_cmd(device):
	global p
	device_name = device.split(' ')[0]
	if device_name in map:
		p = subprocess.Popen(args = map[device_name])

def kill_cmd(device):
	global p
	print 'killing something'
	if not p is None and p.poll() is None:
		p.send_signal(signal.SIGINT)
		time.sleep(0.1)
		if p.poll() is None:
			p.terminate()

def attach_device(port):
	print 'attaching ' + port
	global blinking_rate
	blinking_rate = BLINKING_RATE_LOADING
	attached.add(port)
	exec_cmd(port)

def dettach_device(port):
	print 'dettaching ' + port
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

