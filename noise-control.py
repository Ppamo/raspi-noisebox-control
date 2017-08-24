import time
import signal
import subprocess
import rtmidi_python as rtmidi

map = {
	'LPD8': ['/opt/noisebox/noisebox','1'],
	'nanoKEY2': ['/usr/bin/python','/opt/samplerbox/samplerbox.py', '1', '/opt/debian/opt/samplerbox/samples']
}
midi_in = [rtmidi.MidiIn()]
attached = set()
attached.add(midi_in[0].ports[0])
p = None

def exec_cmd(device):
	global p
	device_name = device.split(' ')[0]
	if device_name in map:
		print map[device_name]
		p = subprocess.Popen(args = map[device_name])

def kill_cmd(device):
	global p
	print 'killing something'
	if not p is None and p.poll() is None:
		p.terminate()
		p.poll()
		if p.returncode is None:
			p.kill()

def attach_device(port):
	print 'attaching ' + port
	attached.add(port)
	exec_cmd(port)

def dettach_device(port):
	print 'dettaching ' + port
	kill_cmd(port)
	attached.remove(port)

while True:
	# if there is a difference
	if len(set(midi_in[0].ports) ^ attached) > 0:
		ports = set(midi_in[0].ports)
		# attach if there is new elements
		for i in ports - attached:
			attach_device(i)
		# detach if necesary
		for i in attached - ports:
			dettach_device(i)
	time.sleep(2)

