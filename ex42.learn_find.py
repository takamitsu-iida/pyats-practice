#!/usr/bin/env python

#
# find stp block port
#

from pprint import pprint

# import Genie
from genie.testbed import load

testbed = load('lab.yml')

learnt = {}
for name, dev in testbed.devices.items():
    if dev.type == 'switch':
        # connect
        dev.connect(via='console')

        # learn
        learnt[name] = dev.learn('stp')

        # disconnect
        dev.disconnect()


for name, stp in learnt.items():
    print(name)
    pprint(stp.info)

# pyats find
# https://pubhub.devnetcloud.com/media/pyats/docs/utilities/helper_functions.html

# learnt shoud be like
# {device_name:{'info: {'pvst': {'default': {'vlans': {'1': {'interfaces': {'Ethernet0/0': {'port_state': 'blocking'}

from pyats.utils.objects import R, find
req = R(['(.*)', 'info', 'pvst', 'default', 'vlans', '(.*)', 'interfaces', '(.*)', 'port_state', 'blocking'])
found = find(learnt, req, filter_=False)

# pprint(found) shows these output
#[('blocking', ['sw3', 'info', 'pvst', 'default', 'vlans', 1, 'interfaces', 'Ethernet0/2', 'port_state']),
# ('blocking', ['sw4', 'info', 'pvst', 'default', 'vlans', 1, 'interfaces', 'Ethernet0/1', 'port_state']),
# ('blocking', ['sw4', 'info', 'pvst', 'default', 'vlans', 1, 'interfaces', 'Ethernet0/0', 'port_state'])]

if found:
    print('found blocking port')
    for item in found:
        print(item[1][0], item[1][7])
else:
    print('block port not found')
