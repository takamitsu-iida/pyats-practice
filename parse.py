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

from pyats.async_ import pcall

import time
from pprint import pprint

def send_ctrl_shift_6(uut):
    time.sleep(1)
    uut.transmit("\036")

def ping(uut):
    #parsed = uut.parse('ping 192.168.255.4 source loopback0 repeat 100000')
    #return parsed
    uut.sendline('ping 192.168.255.4 source loopback0 repeat 100000')
    uut.receive(r'nopattern^', timeout=10)
    return uut.receive_buffer()

def ping2(uut):
    expect = r'Success +rate +is +(?P<success_percent>\d+) +percent +\((?P<received>\d+)\/(?P<sent>\d+)\)'

    uut.sendline('ping 192.168.255.4 source loopback0 repeat 100000')

    # receive() does not raise exception, just block until timeout
    finished = uut.receive(expect, timeout=180) #, search_size=0)
    if finished:
        return uut.receive_buffer()

    # send ctrl-shift-6
    uut.transmit("\036")

    # expect stop
    uut.receive(expect, timeout=5) #, search_size=0)

    return uut.receive_buffer()


def run_ping(uut):
    (_, ping_result) = pcall([send_ctrl_shift_6, ping], iargs=[[uut], [uut]])
    pprint(ping_result)


# connect
uut.connect(via='console')

#parsed = uut.parse('show ip route')
#outgoing_intf = parsed.q.contains('192.168.255.4/32').get_values('outgoing_interface')[0]
#pprint(outgoing_intf)

#learnt = uut.learn('routing')
#pprint(learnt.info)

# parsed = uut.parse('ping 192.168.255.4 source loopback0 repeat 100', timeout=60)
# pprint(parsed)

# run_ping(uut)
output = ping2(uut)

print('='*30)
pprint(output)
print('='*30)


#uut.transmit("\036")

# disconnect
if uut.is_connected():
    uut.disconnect()
