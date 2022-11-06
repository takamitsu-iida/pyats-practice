#!/usr/bin/env python

import logging

from pyats import aetest
from genie.testbed import load
from unicon.core.errors import TimeoutError, StateMachineError, ConnectionError

logger = logging.getLogger(__name__)

###################################################################
###                  COMMON SETUP SECTION                       ###
###################################################################

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def connect(self, testbed):
        """
        全てのCSR1000vに接続します。

        Args:
            testbed (genie.libs.conf.testbed.Testbed): テストベッド
        """

        # testbedが正しくロードされているか確認する
        assert testbed, 'Testbed is not provided!'

        # CommonSetup内で例外が発生するとテスト自体が停止してしまう
        # testbed.connect()は関心のない装置にまで接続してしまうので、ここではCSR1000vルータに限定して接続する
        for _, dev in testbed.devices.items():
            if dev.platform == 'csr1000v':
                try:
                    dev.connect(via='console')
                except (TimeoutError, StateMachineError, ConnectionError):
                    logger.error('Unable to connect to all devices')

###################################################################
###                     TESTCASES SECTION                       ###
###################################################################

def get_success_rate(parsed):
    """
    parse('ping x.x.x.x')の結果からsuccess_rateを抽出して返却
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


class ping_class(aetest.Testcase):

    @aetest.setup
    def setup(self, testbed, ping_list):
        """_summary_
        ルータに乗り込んでpingを実行して結果をクラス変数に保存します。

        Args:
            testbed (genie.libs.conf.testbed.Testbed): テストベッド
            ping_list (list): スクリプト実行時に渡されるpingの宛先リスト
        """

        # 結果を格納する入れ物をクラス変数に作成
        self.ping_results = {}

        for name, dev in testbed.devices.items():
            # CSR1000vルータに限定
            if dev.platform != 'csr1000v':
                continue

            # 接続済みの装置に限定
            if not dev.is_connected():
                continue

            # この装置の実行結果を保存する入れ物を作成
            self.ping_results[name] = {}

            for ip in ping_list:
                logger.info(f'Pinging {ip} from {name}')
                try:
                    parsed = dev.parse(f'ping {ip}')
                    success_rate = get_success_rate(parsed)
                    self.ping_results[name][ip] = success_rate
                except:
                    self.ping_results[name][ip] = 0

    @aetest.test
    def test(self, steps):
        """
        ping実行結果を検証する
        """
        for device_name, ips in self.ping_results.items():
            # 装置に関してのステップ
            with steps.start(f'Looking for ping failures {device_name}', continue_=True) as device_step:
                for ip in ips:
                    # 宛先IPに関してのステップ
                    with device_step.start(f'Checking Ping from {device_name} to {ip}', continue_=True):
                        reason = f'Device {device_name} had {ips[ip]}% success pinging {ip}'
                        if ips[ip] == 100:
                            # 応答が100%ならpass
                            device_step.passed(reason)
                        else:
                            # それ以外はfail
                            device_step.failed(reason)

#####################################################################
####                       COMMON CLEANUP SECTION                 ###
#####################################################################

class CommonCleanup(aetest.CommonCleanup):
    """CommonCleanup Section"""

    @aetest.subsection
    def disconnect(self, testbed):
        """
        testbed全体を切断します。

        Args:
            testbed (genie.libs.conf.testbed.Testbed): テストベッド
        """
        testbed.disconnect()

#
# スタンドアロンで実行
#
# python ping_test.py --testbed ../lab.yml
#
if __name__ == '__main__':

    import argparse

    from pyats import topology

    ping_list = [
        '192.168.255.1',
        '192.168.255.2'
    ]

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

    aetest.main(testbed=args.testbed, ping_list=ping_list)
