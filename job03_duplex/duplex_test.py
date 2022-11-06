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
        テストベッドのCSR1000vに接続します。

        Args:
            testbed (genie.libs.conf.testbed.Testbed): スクリプト実行時に渡されるテストベッド
        """

        # testbedが正しくロードされているか確認する
        assert testbed, 'Testbed is not provided!'

        # 全てのCSR1000vに接続します
        for _, dev in testbed.devices.items():
            if dev.platform != 'csr1000v':
                continue
            try:
                dev.connect(via='console')
            except (TimeoutError, StateMachineError, ConnectionError):
                logger.error('Unable to connect to all devices')

###################################################################
###                     TESTCASES SECTION                       ###
###################################################################

class interface_duplex(aetest.Testcase):

    @aetest.setup
    def setup(self, testbed):
        """
        ルータのインタフェース情報を学習してクラス変数の保管する

        Args:
            testbed (genie.libs.conf.testbed.Testbed): スクリプト実行時に渡されるテストベッド
        """

        # 結果を保存するクラス変数
        self.learnt_interfaces = {}

        # learn('interface')でインタフェース情報を学習する
        for name, dev in testbed.devices.items():
            if dev.platform != 'csr1000v':
                continue
            if dev.is_connected() is False:
                logger.info(f'{name} connected status: {dev.connected}')
                continue
            logger.info(f'Learning Interfaces for {name}')
            self.learnt_interfaces[name] = dev.learn('interface').info


    @aetest.test
    def test(self, steps):
        """
        学習したインタフェース情報を探索して、全二重になっていないインタフェースを抽出する

        Args:
            steps (_type_): ステップ
        """

        # 学習した情報を取り出す
        # {'装置名', {学習したインタフェース情報}}
        for device_name, interfaces in self.learnt_interfaces.items():

            # 取り出した装置に関してのステップ
            with steps.start(f'Looking for half-duplex Interfaces on {device_name}', continue_=True) as device_step:

                # その装置のインタフェースに関して取り出す
                # {'interface_name': {学習したデータ}}
                for interface_name, interface in interfaces.items():

                    # 各インタフェースに関してのステップ
                    with device_step.start(f'Checking Interface {interface_name}', continue_=True) as interface_step:

                        # データの中に'duplex_mode'があるか確認して
                        if 'duplex_mode' in interface.keys():
                            # それが'half'になっていたらfaildにする
                            if interface['duplex_mode'] == 'half':
                                interface_step.failed(f'Device {device_name} Interface {interface_name} is in half-duplex mode')
                        else:
                            # Loopbackのようなインタフェースは'duplex_mode'を持たないのでスキップ
                            interface_step.skipped(f'Device {device_name} Interface {interface_name} has no duplex')


#####################################################################
####                       COMMON CLEANUP SECTION                 ###
#####################################################################

class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect(self, testbed):
        """
        テストベッド全体を切断します。

        Args:
            testbed (genie.libs.conf.testbed.Testbed): スクリプト実行時に渡されるテストベッド
        """
        testbed.disconnect()


#
# スタンドアロンで実行
#
# python duplex_test.py --testbed ../lab.yml
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
