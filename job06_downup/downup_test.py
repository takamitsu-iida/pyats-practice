#!/usr/bin/env python

#
# このテストで想定している構成図
# https://github.com/takamitsu-iida/pyats-practice/blob/main/img/fig1.PNG
#
# r1-+-(gig1)-r2-r4
#    +-(gig2)-r3-r4
#
# r1からr4への到達経路は2経路
# gig1経由が優先。
# 1. gig1をダウンさせて経路がgig2経由でr4に到達できることを確認する
# 2. gig2をダウンさせて経路がgig2経由でr4に到達できることを確認する

import logging
import os
import time

from pyats import aetest
from genie.testbed import load
from genie.utils.timeout import Timeout
from unicon.core.errors import TimeoutError, StateMachineError, ConnectionError

logger = logging.getLogger(__name__)

# 状態データを保存するディレクトリ
# pickle形式で保存するので、ここでは'pkl'という名前にする
pkl_dir = os.path.join(os.path.dirname(__file__), 'pkl')

###################################################################
###                  COMMON SETUP SECTION                       ###
###################################################################

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def create_directory(self):
        """
        保存先のディレクトリ pkl_dir を作る
        """
        os.makedirs(pkl_dir, exist_ok=True)

    @aetest.subsection
    def connect(self, testbed):
        """
        r1, r2, r3, r4に接続します。

        Args:
            testbed (genie.libs.conf.testbed.Testbed): スクリプト実行時に渡されるテストベッド
        """

        # testbedが正しくロードされているか確認する
        assert testbed, 'Testbed is not provided!'

        routers = ['r1', 'r2', 'r3', 'r4']

        devices = []
        for router in routers:
            r = testbed.devices[router]
            try:
                r.connect()
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
        r1からr4に向けての経路がGig1を向いているか確認します。

        Args:
            testbed (genie.libs.conf.testbed.Testbed): スクリプト実行時に渡されるテストベッド
            devices (list): セットアップで作成したデバイスのリストです
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
        r1のGig1をshutdownして経路の切り替わりを検証します。

        Args:
            steps (_type_): ステップ
            testbed (genie.libs.conf.testbed.Testbed): スクリプト実行時に渡されるテストベッド
            devices (list): セットアップで作成したデバイスのリスト
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
        """
        テストベッド全体を切断します。

        Args:
            testbed (genie.libs.conf.testbed.Testbed): スクリプト実行時に渡されるテストベッド
        """
        testbed.disconnect()


#
# スタンドアロンで実行する場合
#
# python downup_test.py --testbed ../lab.yml
#
if __name__ == '__main__':

    import argparse

    from pyats import topology

    # set logger level
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--testbed',
        dest='testbed',
        help='testbed YAML file',
        type=topology.loader.load,
        default=None,
    )
    args, _ = parser.parse_known_args()

    aetest.main(testbed=args.testbed)
