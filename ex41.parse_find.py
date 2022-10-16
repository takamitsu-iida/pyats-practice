#!/usr/bin/env python

#
# find interfaces where out_pkts is 0.
#

from pprint import pprint

# import Genie
from genie.testbed import load

testbed = load('lab.yml')

uut = testbed.devices['uut']

uut.connect(via='console')

parsed = uut.parse('show interfaces')

# display parsed data
for name, data in parsed.items():
    pprint(data)

# find 力技で見つける
for name, data in parsed.items():
    if 'counters' in data:
       if 'out_pkts' in data['counters']:
           if parsed[name]['counters']['out_pkts'] == 0 :
                print(f"{name} is not used.")
                # uut.configure('int {}\n shutdown'.format(name))

# pyatsのfindを使う
# https://pubhub.devnetcloud.com/media/pyats/docs/utilities/helper_functions.html
# 学習結果の辞書型はこうなっている
# intf_name: {'counters': {'out_pkts': 0 }}
from pyats.utils.objects import R, find
req = R(['(.*)', 'counters', 'out_pkts', 0])
intf0 = find(parsed, req, filter_=False)
pprint(intf0)
