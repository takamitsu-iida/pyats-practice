#!/usr/bin/env python

# import Genie
from genie.testbed import load

testbed = load('lab.yml')

uut = testbed.devices['uut']

# connect to the uut
uut.connect(via='console')

#
# configure using Genie Conf Object
#

# 設定できる機能はここで検索
# https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/models
from genie.conf.base import Interface

gig1 = Interface(device=uut, name='Gig1')
gig2 = Interface(device=uut, name='Gig2')
gig3 = Interface(device=uut, name='Gig3')
gig4 = Interface(device=uut, name='Gig4')
gig1.description = "configured by Genie Conf Object"
gig2.description = "configured by Genie Conf Object"
gig3.description = "configured by Genie Conf Object"
gig4.description = "configured by Genie Conf Object"

# verify config
print(gig1.build_config(apply=False))
print(gig2.build_config(apply=False))
print(gig3.build_config(apply=False))
print(gig4.build_config(apply=False))

# apply config
gig1.build_config(apply=True)
gig2.build_config(apply=True)
gig3.build_config(apply=True)
gig4.build_config(apply=True)


つづきはここから
# https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/comparebeforeafter.html