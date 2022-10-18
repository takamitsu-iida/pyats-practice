#!/usr/bin/env python

#
# configure static route
#

# ドキュメントがないので使い方はソースコードを参照
# https://github.com/CiscoTestAutomation/genielibs/blob/master/pkgs/conf-pkg/src/genie/libs/conf/static_routing/iosxe/tests/test_static_routing.py

from pprint import pprint

# import Genie
from genie.testbed import load

testbed = load('lab.yml')

uut = testbed.devices['uut']

# connect to the uut
uut.connect(via='console')

from genie.libs.conf.static_routing.static_routing import StaticRouting

static_routing = StaticRouting()

static_routing.device_attr[uut].vrf_attr['default'].address_family_attr['ipv4'].route_attr['10.10.10.0/24'].interface_attr['GigabitEthernet1'].if_nexthop = '192.168.12.2'

# これは必須
uut.add_feature(static_routing)

# ここで作ったコンフィグは辞書型
# {r1: {}}
cfgs = static_routing.build_config(apply=False)
pprint(str(cfgs[uut.name]))

# add static route
static_routing.build_config(apply=True)

# delete static route
# static_routing.build_unconfig(apply=True)

# disconnect
if uut.is_connected():
    uut.disconnect()
