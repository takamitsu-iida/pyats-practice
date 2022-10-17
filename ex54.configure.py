#!/usr/bin/env python

#
# configure r1 in lab
#

from pprint import pprint

# import Genie
from genie.testbed import load
testbed = load('lab.yml')

uut = testbed.devices['uut']

# connect to the uut
uut.connect(via='console')

from genie.libs.conf.vrf import Vrf
from genie.libs.conf.interface import Interface
from genie.libs.conf.ospf import Ospf
from genie.libs.conf.ospf.areanetwork import AreaNetwork

# CDPはモデルが存在しないのでコマンドを打ち込む
output = uut.configure('''
cdp run
interface Gig1
cdp enable
exit
interface Gig2
cdp enable
exit
''')

pprint(output)

# interface
# see
# https://github.com/CiscoTestAutomation/genielibs/blob/master/pkgs/conf-pkg/src/genie/libs/conf/interface/iosxe/tests/test_interface.py

# create Interface object
lo0 = Interface(device=uut, name='Loopback0')
gig1 = Interface(device=uut, name='GigabitEthernet1')
gig2 = Interface(device=uut, name='GigabitEthernet2')

gig1.enabled = True
gig1.description = 'to r2'
gig1.ipv4 = '192.168.12.1/24'
gig1.mtu = 9000

gig2.enabled = True
gig2.description = 'to r3'
gig2.ipv4 = '192.168.13.1/24'
gig2.mtu = 9000

lo0.enabled = True
lo0.ipv4 = '192.168.255.1/32'

# apply config
lo0.build_config(apply=True)
gig1.build_config(apply=True)
gig2.build_config(apply=True)

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

# add area network configuration to OSPF
area_lo0 = AreaNetwork(device=uut)
area_lo0.area_network = '192.168.255.1'
area_lo0.area_network_wildcard = '0.0.0.0'
ospf1.device_attr[uut].vrf_attr[vrf0].area_attr['0'].add_areanetwork_key(area_lo0)

area_gig1 = AreaNetwork(device=uut)
area_gig1.area_network = '192.168.12.1'
area_gig1.area_network_wildcard = '0.0.0.0'
ospf1.device_attr[uut].vrf_attr[vrf0].area_attr['0'].add_areanetwork_key(area_gig1)

area_gig2 = AreaNetwork(device=uut)
area_gig2.area_network = '192.168.13.1'
area_gig2.area_network_wildcard = '0.0.0.0'
ospf1.device_attr[uut].vrf_attr[vrf0].area_attr['0'].add_areanetwork_key(area_gig2)

# int gig1
ospf1.device_attr[uut].vrf_attr[vrf0].area_attr['0'].interface_attr[gig1].if_cost = 100
ospf1.device_attr[uut].vrf_attr[vrf0].area_attr['0'].interface_attr[gig1].if_type = 'point-to-point'

# int gig2
ospf1.device_attr[uut].vrf_attr[vrf0].area_attr['0'].interface_attr[gig2].if_cost = 100
ospf1.device_attr[uut].vrf_attr[vrf0].area_attr['0'].interface_attr[gig2].if_type = 'point-to-point'

# Add OSPF to the device
uut.add_feature(ospf1)

# {r1: {}}
cfgs = ospf1.build_config(apply=False)
pprint(str(cfgs[uut.name]))

# apply
ospf1.build_config(apply=True)

# disconnect
if uut.is_connected():
    uut.settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0
    uut.settings.POST_DISCONNECT_WAIT_SEC = 0
    uut.disconnect()
