#!/usr/bin/env python

#
# 雑多なお試し用
#

import argparse

from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument('--testbed', dest='testbed', help='testbed YAML file', type=str, default='lab.yml')
args, _ = parser.parse_known_args()

#
# tinydb
#
import datetime
from tinydb import TinyDB, Query

db = TinyDB('log/db.json')

#
# pyATS
#

# import Genie
from genie.testbed import load

testbed = load(args.testbed)

uut = testbed.devices['uut']

# connect
# uut.connect(via='console')
uut.connect()

learnt = uut.learn('interface')

#parsed = uut.parse('show ip route')
#outgoing_intf = parsed.q.contains('192.168.255.4/32').get_values('outgoing_interface')[0]
#pprint(outgoing_intf)

#learnt = uut.learn('routing')
#pprint(learnt.info)

# parsed = uut.parse('ping 192.168.255.4 source loopback0 repeat 100', timeout=60)
# pprint(parsed)

parsed = uut.parse('show ip ospf neighbor')
pprint(parsed)
print('='*10 + '\n')

print('Gig1')
filtered = parsed.q.contains('GigabitEthernet1').reconstruct()
if not filtered:
    print('not found')
else:
    pprint(filtered)

print('Gig3')
filtered = parsed.q.contains('GigabitEthernet3').reconstruct()
if not filtered:
    print('not found')
else:
    pprint(filtered)


# disconnect
if uut.is_connected():
    uut.disconnect()
