#!/usr/bin/env python

#
# 単体のコマンドをパースしてダンプする
#

import argparse
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument('--testbed', dest='testbed', help='testbed YAML file', type=str, default='lab.yml')
args, _ = parser.parse_known_args()

#
# pyATS
#

# import Genie
from genie.testbed import load

testbed = load(args.testbed)

uut = testbed.devices['uut']

# connect
uut.connect(via='console')

parsed = uut.parse('show ip route')
learnt = uut.learn('routing')

# disconnect
if uut.is_connected():
    uut.disconnect()

outgoing_intf = parsed.q.contains('192.168.255.4/32').get_values('outgoing_interface')[0]
pprint(outgoing_intf)

pprint(learnt.info)