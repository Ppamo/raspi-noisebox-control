import time
import rtmidi_python as rtmidi

midi_in = [rtmidi.MidiIn()]
attached = set()
attached.add(midi_in[0].ports[0])

def attach_device(port):
	print '==> attaching ' + port
	attached.add(port)

def dettach_device(port):
	print '==> dettaching ' + port
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

time.sleep(3)
