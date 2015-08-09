import paho.mqtt.client as mqtt
from ouimeaux.environment import Environment
from ouimeaux.signals import receiver, statechange

def on_connect(client, userdata, rc):
	print('Connected with result code '+str(rc))
	client.subscribe('lights/#')
	client.subscribe('devices/discover')

def turn_lights_on(client, userdata, rc):
	for (x, value) in enumerate(devices['switches']):
		devices['switches'][x].on()

def turn_lights_off(client, userdata, rc):
	for (x, value) in enumerate(devices['switches']):
		devices['switches'][x].off()

def reply_with_devices(client, userdata, rc):
	print 'Send all devices in response to devices/discover'
	for (x, device) in enumerate(devices['switches']):
		client.publish('devices/new', '{{ "name": "{0}", "type": "light", "subType": "wemo_light", "state": "{1}" }}'.format(device.name,device.get_state()))
	for (x, device) in enumerate(devices['motions']):
		client.publish('devices/new', '{{ "name": "{0}", "type": "sensor", "subType": "motion_sensor", "state": "{1}" }}'.format(device.name,device.get_state()))

def on_switch(switch):
	print "Switch found: ", switch.name
	devices['switches'].append(switch)

def on_motion(motion):
	print "Motion found: ", motion.name
	devices['motions'].append(motion)

client = mqtt.Client("wemo_controller")
client.on_connect = on_connect
client.message_callback_add('lights/on', turn_lights_on)
client.message_callback_add('lights/off', turn_lights_off)
client.message_callback_add('devices/discover', reply_with_devices)

client.connect('192.168.1.74', 1883, 60)

print 'Running WEMO controller - listening for messages on localhost:1883'

devices = { 'switches': [], 'motions': [] }

env = Environment(on_switch, on_motion)
env.start()
env.discover(seconds=3)

switch = env.get_switch('Desk lights')

@receiver(statechange)
def motion(sender, **kwargs):
	print 'A THING HAPPENED'
	print "{} state is {state}".format(sender.name, state="on" if kwargs.get('state') else "off")

client.loop_start()

env.wait()