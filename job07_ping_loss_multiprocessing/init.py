#!/usr/bin/env python

#
# configure r2 and r3 in lab
#

import argparse

# import Genie
from genie.testbed import load
from genie.libs.conf.interface import Interface

# script args
parser = argparse.ArgumentParser()
parser.add_argument('--testbed', dest='testbed', help='testbed YAML file', type=str, default='../lab.yml')
args, _ = parser.parse_known_args()

#
# pyATS
#

testbed = load(args.testbed)

for router in ['r2', 'r3']:
    uut = testbed.devices[router]

    # connect to the uut
    uut.connect(via='console')

    for intf in ['GigabitEthernet1', 'GigabitEthernet2']:
        gig = Interface(device=uut, name=intf)
        gig.enabled = True
        gig.build_config(apply=True)

    # disconnect
    if uut.is_connected():
        uut.disconnect()
