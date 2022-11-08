#!/usr/bin/env python

#
# configure r1 in lab
#

import argparse

from pprint import pprint

# import Genie
from genie.testbed import load

# script args
parser = argparse.ArgumentParser()
parser.add_argument('--testbed', dest='testbed', help='testbed YAML file', type=str, default='../lab.yml')
args, _ = parser.parse_known_args()

#
# pyATS
#

testbed = load(args.testbed)

uut = testbed.devices['uut']

# connect to the uut
uut.connect()

from genie.libs.conf.vrf import Vrf
from genie.libs.conf.interface import Interface
from genie.libs.conf.ospf import Ospf
from genie.libs.conf.ospf.areanetwork import AreaNetwork


# interface
# see
# https://github.com/CiscoTestAutomation/genielibs/blob/master/pkgs/conf-pkg/src/genie/libs/conf/interface/iosxe/tests/test_interface.py

# create Interface object
lo0 = Interface(device=uut, name='Loopback0')
gig1 = Interface(device=uut, name='GigabitEthernet1')
gig1.enabled = True

# apply config
gig1.build_config(apply=True)

# OSPF
# see
# https://github.com/CiscoTestAutomation/genielibs/blob/master/pkgs/conf-pkg/src/genie/libs/conf/ospf/iosxe/tests/test_ospf.py

# create Vrf objects
vrf0 = Vrf('default')

# create Ospf object
ospf1 = Ospf()

# add configurations to vrf default
ospf1.device_attr[uut].vrf_attr[vrf0].instance = '1'
ospf1.device_attr[uut].vrf_attr[vrf0].router_id = '192.168.255.1'

# int gig1
ospf1.device_attr[uut].vrf_attr[vrf0].area_attr['0'].interface_attr[gig1].if_cost = 10
ospf1.device_attr[uut].vrf_attr[vrf0].area_attr['0'].interface_attr[gig1].if_type = 'point-to-point'

# Add OSPF to the device
uut.add_feature(ospf1)

# apply
ospf1.build_config(apply=True)

# disconnect
if uut.is_connected():
    uut.disconnect()
