#!/usr/bin/env python

#
# connect to the uut and execute commnad
#

# import Genie
from genie.testbed import load

# load mock
testbed = load('mock.yml')

uut = testbed.devices['uut']

# connect to the uut
uut.connect(via='console')

# execute command
output = uut.execute('show version')

# print output
from pprint import pprint
pprint(output)
