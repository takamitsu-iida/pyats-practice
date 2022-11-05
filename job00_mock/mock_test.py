#!/usr/bin/env python

import logging
import os
import sys

from pyats import aetest
from genie.testbed import load
from unicon.core.errors import TimeoutError, StateMachineError, ConnectionError
from unicon.core.errors import SubCommandFailure

logger = logging.getLogger(__name__)

def here(path=''):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

###################################################################
###                  COMMON SETUP SECTION                       ###
###################################################################

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def load_telnetlib(self):
        """
        改変したtelnetlibをロードする
        前提条件： telnetlib.pyの置き場所は../lib
        """
        if not here('../lib') in sys.path:
            sys.path.insert(0, here('../lib'))

        import telnetlib
        if telnetlib.MODIFIED_BY:
            logger.info('modified telnetlib is loaded')


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

class collect_all(aetest.Testcase):

    @aetest.setup
    def setup(self):
        """ nothing needed
        """
        pass

    @aetest.test
    def learn_all(self, steps, testbed):
        """
        情報を収集する
        1. すべてのCSR1000vでlearn(all)
        """
        for name, dev in testbed.devices.items():
            if dev.platform != 'CSR1000v':
                continue

            # 装置に関してステップ
            with steps.start(f'Learn all about {name}', continue_=True) as dev_step:
                try:
                    learnt = dev.learn('all')
                except (TimeoutError, SubCommandFailure) as e:
                    dev_step.failed('Could not learn all collectly \n{}'.format(str(e)))


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

    # python mock_test.py --testbed ../lab.yml

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
