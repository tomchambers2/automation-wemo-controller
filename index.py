import paho.mqtt.client as mqtt
from ouimeaux.environment import Environment
from ouimeaux.signals import receiver, statechange

def on_connect(client, userdata, rc):
	print('Connected with result code '+str(rc))
	client.subscribe('lights/#')

def turn_lights_on(client, userdata, rc):
	for (x, value) in enumerate(devices['switches']):
		devices['switches'][x].on()

def turn_lights_off(client, userdata, rc):
	for (x, value) in enumerate(devices['switches']):
		devices['switches'][x].off()

def reply_with_devices(client, userdata, rc):
	for (x, value) in enumerate(devices['switches']):
		client.publish('devices/new', '{{ "name": "{0}", "type": "light", "subType": "wemo_light" "state": "{1}" }}'.format(switches[x],switches[x].get_state())
	for (x, value) in enumerate(devices['motions']):
		client.publish('devices/new', '{{ "name": "{0}", "type": "sensor", "subType": "motion_sensor" "state": "{1}" }}'.format(motions[x],motions[x].get_state())

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

client.connect('localhost', 1883, 60)

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

env.wait()

client.loop_forever()