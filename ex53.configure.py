#!/usr/bin/env python

#
# configure ospf
#

# ドキュメントがないので使い方はソースコードを参照
# https://github.com/CiscoTestAutomation/genielibs/blob/master/pkgs/conf-pkg/src/genie/libs/conf/ospf/iosxe/tests/test_ospf.py

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

# create Vrf objects
vrf0 = Vrf('default')

# create Interface object
gig1 = Interface(name='GigabitEthernet1')

# create Ospf object
ospf1 = Ospf()

# add configurations to vrf default
ospf1.device_attr[uut].vrf_attr[vrf0].instance = '1'
ospf1.device_attr[uut].vrf_attr[vrf0].router_id = '192.168.255.1'
ospf1.device_attr[uut].vrf_attr[vrf0].area_attr['0'].interface_attr[gig1].if_cost = 10
ospf1.device_attr[uut].vrf_attr[vrf0].area_attr['0'].interface_attr[gig1].if_type = 'point-to-point'

cfgs = ospf1.build_config(apply=False)

# cfgs = {r1: {...}}
pprint(str(cfgs[uut.name]))

# add feature to the device
uut.add_feature(ospf1)

# apply
ospf1.build_config(apply=True)

# 注意！
# 引数なしでunconfigするとospfの設定がまるごと消える
# ospf1.build_unconfig(apply=True)

# disconnect
if uut.is_connected():
    uut.settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0
    uut.settings.POST_DISCONNECT_WAIT_SEC = 0
    uut.disconnect()
