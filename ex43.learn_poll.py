#!/usr/bin/env python

#
# poll interface status
#
# see
# https://pubhub.devnetcloud.com/media/genie-docs/docs/userguide/Ops/user/ops.html

# usage: ex43.learn_poll.py [-h] [--testbed TESTBED]
#
# optional arguments:
#   -h, --help         show this help message and exit
#   --testbed TESTBED  testbed YAML file

import argparse

# script args
parser = argparse.ArgumentParser()
parser.add_argument('--testbed', dest='testbed', help='testbed YAML file', type=str, default='lab.yml')
args, _ = parser.parse_known_args()

#
# pyATS
#

# import Genie
from genie.testbed import load

# 機種固有のInterfaceをインポートする場合
# from genie.libs.ops.interface.ios.interface import Interface
# from genie.libs.ops.interface.iosxr.interface import Interface
# from genie.libs.ops.interface.iosxe.interface import Interface

# 装置情報から自動で機種にあったInterfaceをロードする場合
from genie.ops.utils import get_ops

# verify at least one interface is up, or raise Exception
def verify_interface_status(obj):
    # make sure interface has learnt
    assert obj.info

    for name in obj.info.keys():
        oper_status = obj.info[name].get('oper_status', None)
        if oper_status == 'up':
            print("verified successfully")
            return

    raise Exception("Could not find any up interface")

testbed = load(args.testbed)

uut = testbed.devices['uut']

# connect
uut.connect()

# 機種にあったInterfaceクラスをロードする
Interface = get_ops('interface', uut)

intf = Interface(device=uut)

# try to verify up to 3 times with sleep of 5 seconds between each attempt
# until at least one interface is up
try:
    intf.learn_poll(verify=verify_interface_status, sleep=5, attempt=3)
except StopIteration as e:
    print(e)

# disconnect
if uut.is_connected():
    uut.disconnect()
