#!/usr/bin/env python

import logging
import os
import pickle

from pyats import aetest
from genie.testbed import load
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
        self.parent.parameters.update(testbed=testbed)

    @aetest.subsection
    def connect(self, testbed):
        """
        テストベッド内のすべてのCSR1000vに接続
        """
        for name, dev in testbed.devices.items():
            if dev.platform != 'CSR1000v':
                continue

            # connect
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
        1. 事前に保存しておいたルーティング情報を一つの辞書型に格納する
        2. テストベッド内のすべてのCSR1000vからルーティングテーブルを学習して一つの辞書型に格納する
        """
        self.before_routes = {}
        self.after_routes = {}

        for name, dev in testbed.devices.items():
            if dev.platform != 'CSR1000v':
                continue

            # load learnt routing table
            log_path = os.path.join(pkl_dir, f'routing.{name}.pickle')
            with open(log_path, 'rb') as f:
                loaded = pickle.load(f)
                self.before_routes[name] = loaded

            logger.info(f'{name} connected status: {dev.connected}')
            if not dev.is_connected():
                continue

            # learn routing table
            self.after_routes[name] = dev.learn('routing')

    @aetest.test
    def test(self, steps, testbed):
        """
        ルーティングテーブルをbefore/afterで検証する
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
        # testbedそのものから切断
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
