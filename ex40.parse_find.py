#!/usr/bin/env python

#
# find interfaces where out_pkts is 0.
#

from pprint import pprint

# import Genie
from genie.testbed import load

testbed = load('lab.yml')

uut = testbed.devices['uut']

# connect
uut.connect(via='console')

# parse
parsed = uut.parse('show interfaces')

# disconnect
if uut.is_connected():
    uut.disconnect()

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

# pyats find
# https://pubhub.devnetcloud.com/media/pyats/docs/utilities/helper_functions.html

from pyats.utils.objects import R, find

# from
# {interface_name: {'counters': {'out_pkts': 0

req = R(['(.*)', 'counters', 'out_pkts', 0])
found = find(parsed, req, filter_=False)
pprint(found)
