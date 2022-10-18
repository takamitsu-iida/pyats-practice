#!/usr/bin/env python

#
# configure directly
#

# import Genie
from genie.testbed import load

testbed = load('lab.yml')

uut = testbed.devices['uut']

# connect to the uut
uut.connect(via='console')

# configure
output = uut.configure('''
interface Gig1
description "configured by pyats"
exit
interface Gig2
description "configured by pyats"
exit
''')

# disconnect
if uut.is_connected():
    uut.disconnect()

from pprint import pprint
pprint(output)
