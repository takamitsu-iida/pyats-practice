#!/usr/bin/env python

# import Genie
from genie.testbed import load

testbed = load('lab.yml')

uut = testbed.devices['uut']

# connect to the uut
uut.connect(via='console')

#
# execute command
#
output = uut.execute('show version')

from pprint import pprint
pprint(output)
