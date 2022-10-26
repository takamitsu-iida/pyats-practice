# インタフェース閉塞に伴う経路情報の判定テスト

インタフェースを閉塞して、期待通りの経路に切り替わるか、ping疎通がとれるかを確認します。

![構成図](https://takamitsu-iida.github.io/pyats-practice/img/fig1.PNG "構成図")

手順１．

1. r1, r2, r3, r4に接続します
1. r1からr4に向けた経路がGig1を向いているかを確認します
1. 全ルータのルーティングテーブルを学習してファイルに保存します

手順２．

1. r1のGig1を閉塞します
1. r1からr4へのpingが通るまで待機します
1. r1の経路情報を採取して、r4向けの経路がGig2を向いているかを確認します
1. 全ルータのルーティングテーブルを学習してファイルに保存します

手順３．

1. r1のGig1の閉塞を解除します
1. r1の経路情報を採取して、r4向けの経路がGig1に戻っているかを確認します
1. 全ルータのルーティングテーブルを学習してファイルに保存します


<br>

### リプレイ

```bash
pyats run job downup_job.py --testbed-file ../lab.yml --replay record
```

<br>

### テストスクリプト

長いです。

なるべくテストの流れが読みやすくなるようにヘルパー関数を作っています。

```python
#!/usr/bin/env python

#
# このテストで想定している構成図
# https://github.com/takamitsu-iida/pyats-practice/blob/main/img/fig1.PNG
#
# r1-+-(gig1)-r2-r4
#    +-(gig2)-r3-r4
#
# r1からr4への到達経路は2個
# gig1が優先。gig1をダウンさせて経路がgig2経由でr4に到達できることを確認する
#

import logging
import os
import time

from pprint import pformat

from pyats import aetest
from genie.testbed import load
from genie.utils.timeout import Timeout
from unicon.core.errors import TimeoutError, StateMachineError, ConnectionError

logger = logging.getLogger(__name__)

def here(path=''):
  return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

# pickle directory
pkl_dir = os.path.join(here('.'), 'pkl')

###################################################################
###                  COMMON SETUP SECTION                       ###
###################################################################

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def load_testbed(self, testbed):
        """
        testbedの形式を変換
        """
        assert testbed, 'Testbed is not provided!'
        logger.info('Converting pyATS testbed to Genie Testbed to support pyATS Library features')
        testbed = load(testbed)

        # 親クラスにtestbedを格納（上書き）
        self.parent.parameters.update(testbed=testbed)

    @aetest.subsection
    def create_directory(self):
        # create pkl_dir
        os.makedirs(pkl_dir, exist_ok=True)

    @aetest.subsection
    def connect(self, testbed):
        """
        r1, r2, r3, r4に接続する
        """
        routers = ['r1', 'r2', 'r3', 'r4']
        devices = []

        for router in routers:
            r = testbed.devices[router]
            try:
                r.connect(via='console')
                devices.append(r)
            except (TimeoutError, StateMachineError, ConnectionError):
                logger.error(f'Unable to connect to {router}')

        # 親クラスにdevicesを格納して後続のテストで利用できるようにする
        self.parent.parameters.update(devices=devices)


###################################################################
###                     TESTCASES SECTION                       ###
###################################################################

COMMAND_GIG1_DOWN = '''
interface Gig1
shutdown
'''

COMMAND_GIG1_UP = '''
interface Gig1
no shutdown
'''

def get_success_rate(parsed):
    """
    parse('ping 192.168.255.4')の結果からsuccess_rateを抽出して返却
    """
    # pingパーサーのスキーマはここにある通り
    # https://github.com/CiscoTestAutomation/genieparser/blob/master/src/genie/libs/parser/iosxe/ping.py#L48
    #
    # {'ping': {'address': '192.168.255.4',
    #           'result_per_line': ['!!!!!'],
    #           'statistics': {'received': 5,
    #                          'round_trip': {'avg_ms': 1, 'max_ms': 2, 'min_ms': 1},
    #                          'send': 5,
    #                          'success_rate_percent': 100.0},　★これだけを返す
    #           'timeout_secs': 2}}
    success_rate = parsed.q.raw('[ping][statistics][success_rate_percent]')
    return success_rate


def get_oper_status(parsed):
    """
    parse('show interface Gigabitethernet1')の結果から'oper_statu'を抽出して返却する
    """
    # show interface {interface name}パーサーのスキーマはここにある通り
    # https://github.com/CiscoTestAutomation/genieparser/blob/master/src/genie/libs/parser/iosxe/show_interface.py#L222
    #
    # {'GigabitEthernet1': {'arp_timeout': '04:00:00',
    #                     'bandwidth': 1000000,
    #                     'oper_status': 'up', ★これだけを抽出
    oper_status = parsed.q.get_values('oper_status', 0)
    return oper_status


def get_outgoing_interface(parsed, prefix):
    """
    parse('show ip route')の結果から'outgoing_interface'を抽出して返却する
    """
    # show ip routeパーサーのスキーマはここを参照
    # https://github.com/CiscoTestAutomation/genieparser/blob/master/src/genie/libs/parser/iosxe/show_routing.py#L15
    #
    # {'vrf': {'default': {'address_family': {'ipv4': {'routes': {'192.168.12.0/24': {'active': True,
    #                                                                                 'metric': 310,
    #                                                                                 'next_hop': {'next_hop_list': {1: {'index': 1,
    #                                                                                                                    'next_hop': '192.168.13.3',
    #                                                                                                                    'outgoing_interface': 'GigabitEthernet2',
    #                                                                                                                    'updated': '00:05:23'}}},
    #                                                                                 'route': '192.168.12.0/24',
    #                                                                                 'route_preference': 110,
    #                                                                                 'source_protocol': 'ospf',
    #                                                                                 'source_protocol_codes': 'O'},
    outgoing_intf = parsed.q.contains(prefix).get_values('outgoing_interface', 0)
    return outgoing_intf


def save_route(learnt, path):
    """
    dev.learn()の結果をpathで示すファイルに保存する
    """
    if os.path.exists(path):
        os.remove(path)
    with open(path, 'wb') as f:
        f.write(learnt.pickle(learnt))


def get_file_path(hostname, status):
    return os.path.join(pkl_dir, f'routing_{hostname}_r1gig1_{status}.pickle')


class down_up_test_class(aetest.Testcase):

    @aetest.setup
    def setup(self, testbed, devices):
        """
        r1からr4に向けての経路がGig1を向いているか確認する
        """
        r1 = testbed.devices['r1']
        parsed = r1.parse('show ip route')
        next_hop = get_outgoing_interface(parsed, '192.168.255.4/32')
        if next_hop != 'GigabitEthernet1':
            self.failed(f'nexthop to r4 is not expected: {next_hop}')

        # 作業前のルーティングテーブルを学習して保存
        for dev in devices:
            learnt = dev.learn('routing')
            path = get_file_path(dev.name, 'before')
            save_route(learnt, path)


    @aetest.test
    def test(self, steps, testbed, devices):
        """
        r1のGig1をshutdownして経路の切り替わりを検証する
        """

        r1 = testbed.devices['r1']

        # r1に関して
        with steps.start('r1', continue_=True) as r1_step:

            # Gig1を閉塞する
            with r1_step.start('Gig1 down', continue_=True) as gig1_down_step:
                # Gig1にshowdownを投入
                r1.configure(COMMAND_GIG1_DOWN)

                # 実際にインタフェースダウンを検知するまで時間がかかるのでここでは3秒待つ
                time.sleep(3)

                # r4にpingが届くまで待機

                # 上限120秒、10秒待機、タイムアウトを画面表示
                timeout = Timeout(max_time = 120, interval = 10, disable_log = False)
                try:
                    while timeout.iterate():
                        parsed = r1.parse('ping 192.168.255.4')
                        success_rate = get_success_rate(parsed)
                        logger.info(f'ping from r1 to r4 success_rate: {success_rate}%')
                        if success_rate == 100:
                            break
                        timeout.sleep()

                    # r4にpingが届いた

                    # r1のルーティングテーブルを採取
                    parsed = r1.parse('show ip route')

                    # r4のLoopbackアドレス192.168.255.4/32向けのネクストホップを確認
                    next_hop_to_r4 = get_outgoing_interface(parsed, '192.168.255.4/32')
                    logger.info(f'nexthop from r1 to r4 is {next_hop_to_r4}')

                    # Gig2を向いているか確認
                    if next_hop_to_r4 != 'GigabitEthernet2':
                        gig1_down_step.failed(f'nexthop to r4 is not expected: {next_hop_to_r4}')

                    # ログ目的でr1, r2, r3, r4のルーティングテーブルを学習して保存
                    for dev in devices:
                        learnt = dev.learn('routing')
                        path = get_file_path(dev.name, 'down')
                        save_route(learnt, path)

                except TimeoutError:
                    gig1_down_step.failed('ping from r1 to r4 failed.')


            # Gig1の閉塞を解除
            with r1_step.start('Gig1 up', continue_=True) as gig1_up_step:
                # no showdownで元に戻す
                r1.configure(COMMAND_GIG1_UP)

                # r4への経路がGig1に向くまで待機
                # 上限120秒、10秒待機、タイムアウトを画面表示
                timeout = Timeout(max_time = 120, interval = 10, disable_log = False)
                try:
                    while timeout.iterate():
                        # r1のルーティングテーブルを採取
                        parsed = r1.parse('show ip route')

                        # r4のLoopbackアドレス192.168.255.4/32向けのネクストホップを確認
                        next_hop_to_r4 = get_outgoing_interface(parsed, '192.168.255.4/32')
                        logger.info(f'nexthop from r1 to r4 is {next_hop_to_r4}')

                        if next_hop_to_r4 == 'GigabitEthernet1':
                            break
                        timeout.sleep()

                    # r4への経路がGig1経由に戻った

                    # ログ目的でr1, r2, r3, r4のルーティングテーブルを学習して保存
                    for dev in devices:
                        learnt = dev.learn('routing')
                        path = get_file_path(dev.name, 'up')
                        save_route(learnt, path)

                    # 無事テスト完了
                    gig1_up_step.passed('route from r1 to r4 reverted successfuly.')

                except TimeoutError:
                    gig1_up_step.failed('route from r1 to r4 wrong.')

#####################################################################
####                       COMMON CLEANUP SECTION                 ###
#####################################################################

class CommonCleanup(aetest.CommonCleanup):
    """CommonCleanup Section"""

    @aetest.subsection
    def disconnect(self, testbed):
        # testbedそのものから切断
        testbed.disconnect()

#
# stand-alone test
#
if __name__ == "__main__":

    # python ospf_test.py --testbed ../lab.yml

    import argparse
    from pyats import topology

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--testbed',
        dest='testbed',
        help='testbed YAML file',
        type=topology.loader.load,
        default=None,
    )

    # parse command line arguments only we know
    args, _ = parser.parse_known_args()

    aetest.main(testbed=args.testbed)
```

## 実行後の確認

テストを実行すると、各ステップで学習したルーティングテーブルがファイルとして残ります。

```bash
$ tree pkl
pkl
├── routing_r1_r1gig1_before.pickle
├── routing_r1_r1gig1_down.pickle
├── routing_r1_r1gig1_up.pickle
├── routing_r2_r1gig1_before.pickle
├── routing_r2_r1gig1_down.pickle
├── routing_r2_r1gig1_up.pickle
├── routing_r3_r1gig1_before.pickle
├── routing_r3_r1gig1_down.pickle
├── routing_r3_r1gig1_up.pickle
├── routing_r4_r1gig1_before.pickle
├── routing_r4_r1gig1_down.pickle
└── routing_r4_r1gig1_up.pickle
```

これらファイルの中身を確認するにはroute.pyを使います。

```bash
$ ./route.py --help
usage: route.py [-h] {show,diff}

positional arguments:
  {show,diff}  show or diff

optional arguments:
  -h, --help   show this help message and exit
```
