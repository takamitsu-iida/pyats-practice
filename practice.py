#!/usr/bin/env python

from pprint import pprint

# import Genie
from genie.testbed import load

testbed = load('lab.yml')

uut = testbed.devices['uut']

uut.connect(via='console')

#
# コマンドを打ち込む
#
if False:
    output = uut.execute('show clock')
    pprint(output)

    output = uut.execute('show version')
    pprint(output)


#
# 差分を表示する
#
if False:

    output1 = uut.parse('show version')

    # 重たい処理をする
    output = uut.learn('ospf')
    # pprint(output)

    output2 = uut.parse('show version')

    from genie.utils.diff import Diff

    diff = Diff(output1, output2)
    diff.findDiff()
    print(diff)

#
# インタフェース状態を学習
#
if False:
    from genie.libs.ops.interface.iosxe.interface import Interface
    intf = Interface(device=uut)
    intf.learn()
    # インタフェースの名前一覧
    intf.info.keys()
    pprint(intf.info['GigabitEthernet1'])


#
# 全ての機能を学習
#
if False:
    output = uut.learn('all')
    pprint(output)

#
# インタフェースがアップしているかどうかを確かめる
#
if False:
    from genie.libs.ops.interface.iosxe.interface import Interface

    def verify_interface_status(obj):
        # Interface object that was learnt
        # Let's verify that at least one interface is up
        for intf in obj.info:
            if obj.info[intf].get('oper_status', None) and obj.info[intf]['oper_status'] == 'up':
                return
        # If no interface was found to have an up oper_status, then
        # raise an exception
        raise Exception("Could not find any up interface")

    # Learn all interface which has duplex mode as a key
    interface = Interface(device=uut)

    # Try to verify up to 6 times that at least one interface is up
    # with sleep of 5 seconds between each attempt
    interface.learn_poll(verify=verify_interface_status, sleep=5, attempt=6)

#
# 学習状態のDiffを取る
#
if False:
    from genie.libs.ops.interface.iosxe.interface import Interface

    interface = Interface(device=uut, attributes=['info[Loopback0]'])
    interface.learn()

    uut.configure('''
    interface loopback0
    shutdown
    ''')

    # take a snapshot now and compare
    interface_after = Interface(device=uut, attributes=['info[Loopback0]'])
    interface_after.learn()

    uut.configure('''
    interface loopback0
    no shutdown
    ''')

    diff = interface_after.diff(interface)
    print(diff)


#
# 必要な情報を探す
#
if True:
    from genie.libs.ops.interface.iosxe.interface import Interface
    from pyats.utils.objects import R, find

    interface = Interface(device=uut)
    interface.learn()

    # upしているインタフェース全て
    req1 = R(['info', '(.*)', 'oper_status', 'up'])
    output = find(interface, req1, filter_=False)
    pprint(output)
    # [('up', ['info', 'GigabitEthernet4', 'oper_status']),
    #  ('up', ['info', 'Loopback0', 'oper_status'])]

    # duplexがfullのインタフェース全て
    req2 = R(['info', '(.*)', 'duplex_mode', 'full'])
    output = find(interface, req2, filter_=False)
    pprint(output)
    # [('full', ['info', 'GigabitEthernet4', 'duplex_mode']),
    # ('full', ['info', 'GigabitEthernet3', 'duplex_mode']),
    # ('full', ['info', 'GigabitEthernet2', 'duplex_mode']),
    # ('full', ['info', 'GigabitEthernet1', 'duplex_mode'])]

    # 両方の条件
    req3 = [
        R(['info', '(?P<interface>.*)', 'oper_status', 'up']),
        R(['info', '(?P<interface>.*)', 'duplex_mode', 'full'])
    ]
    output = find(interface, *req3, filter_=False)
    pprint(output)