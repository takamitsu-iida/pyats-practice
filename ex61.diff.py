#!/usr/bin/env python

# compare two ops objects
# https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/comparebeforeafter.html

import os
from pdb import post_mortem
import sys

#
# overwrite standard telnetlib
#
def here(path=''):
  return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

if not here('./lib') in sys.path:
  sys.path.insert(0, here('./lib'))

import telnetlib
if telnetlib.MODIFIED_BY:
    print('modified telnetlib is loaded.')

from pprint import pprint

# import Genie
from genie.testbed import load
from genie.utils.diff import Diff

testbed = load('lab.yml')

uut = testbed.devices['uut']

uut.connect(via='console')

# learn ospf state
pre_ospf = uut.learn('ospf')

# change ospf config
# cost 100 -> 10
uut.configure('''
interface Gig1
ip ospf cost 10
exit
''')

# learn current config
post_ospf = uut.learn('ospf')

# revert ospf config
uut.configure('''
interface Gig1
ip ospf cost 100
exit
''')

# diff = Diff(pre_ospf, post_ospf)
# diff.findDiff()
# print(diff)

diff = post_ospf.diff(pre_ospf)
diff.findDiff()
print(diff)