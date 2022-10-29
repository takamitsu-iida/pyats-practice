#!/usr/bin/env python

import logging
import os
import pickle

from pyats import aetest
from genie.testbed import load
from unicon.core.errors import TimeoutError, StateMachineError, ConnectionError

logger = logging.getLogger(__name__)

# pickle directory
pkl_dir = os.path.join(os.path.dirname(__file__), 'pkl')

###################################################################
###                  COMMON SETUP SECTION                       ###
###################################################################

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def connect(self, testbed):
        """
        テストベッド内のすべてのCSR1000vに接続します。

        Args:
            testbed (genie.libs.conf.testbed.Testbed): スクリプト実行時に渡されるテストベッド
        """

        # testbedが正しくロードされているか確認する
        assert testbed, 'Testbed is not provided!'

        # 全てのCSR1000vに接続
        for name, dev in testbed.devices.items():
            if dev.platform != 'CSR1000v':
                continue

            try:
                dev.connect(via='console')
            except (TimeoutError, StateMachineError, ConnectionError):
                logger.error(f'Unable to connect to {name}')


###################################################################
###                     TESTCASES SECTION                       ###
###################################################################

class routing_class(aetest.Testcase):

    @aetest.setup
    def setup(self, testbed):
        """
        比較対象となる２つのルーティングテーブルを採取します。
            1. 事前にファイルに保存しておいたルーティング情報を一つの辞書型に格納する
            2. テストベッド内のすべてのCSR1000vからルーティングテーブルを学習して一つの辞書型に格納する

        Args:
            testbed (genie.libs.conf.testbed.Testbed): スクリプト実行時に渡されるテストベッド
        """

        self.before_routes = {}
        self.after_routes = {}

        for name, dev in testbed.devices.items():
            if dev.platform != 'CSR1000v':
                continue

            # ファイルからルーティングテーブルを読む
            log_path = os.path.join(pkl_dir, f'routing.{name}.pickle')
            with open(log_path, 'rb') as f:
                loaded = pickle.load(f)
                self.before_routes[name] = loaded

            logger.info(f'{name} connected status: {dev.connected}')
            if not dev.is_connected():
                continue

            # ルーティングテーブルを学習する
            self.after_routes[name] = dev.learn('routing')

    @aetest.test
    def test(self, steps, testbed):
        """
        ルーティングテーブルをbeforeとafterで検証します。

        Args:
            steps (_type_): ステップ
            testbed (genie.libs.conf.testbed.Testbed): スクリプト実行時に渡されるテストベッド
        """

        for name, dev in testbed.devices.items():
            if dev.platform != 'CSR1000v':
                continue

            # 装置に関してのステップ
            with steps.start(f'Looking for routing table change {name}', continue_=True) as device_step:
                before = self.before_routes.get(name, None)
                if before is None:
                    device_step.failed(f'Before data for device {name} not found')

                after = self.after_routes.get(name, None)
                if after is None:
                    device_step.failed(f'After data for device {name} not found')

                # diffをとる
                diff = after.diff(before, exclude=['updated'])
                diff.findDiff()

                # 差分があればfailed
                if str(diff):
                    device_step.failed(str(diff))


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
# stand-alone test
#
if __name__ == "__main__":

    # python route_test.py --testbed ../lab.yml

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
