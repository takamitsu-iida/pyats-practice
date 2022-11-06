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
    def connect(self, testbed):
        """
        テストベッド内のすべてのCSR1000vに接続
        """
        for name, dev in testbed.devices.items():
            if dev.platform != 'csr1000v':
                continue

            try:
                dev.connect(via='console')
            except (TimeoutError, StateMachineError, ConnectionError):
                logger.error(f'Unable to connect to {name}')


###################################################################
###                     TESTCASES SECTION                       ###
###################################################################

class collect_all(aetest.Testcase):

    @aetest.test
    def dummy(self, steps, testbed):
        """
        すべてのCSR1000vを訪問する
        """
        for name, dev in testbed.devices.items():
            if dev.platform != 'csr1000v':
                continue

            with steps.start(f'Learn all about {name}', continue_=True) as dev_step:
                dev_step.passed()


#####################################################################
####                       COMMON CLEANUP SECTION                 ###
#####################################################################

class CommonCleanup(aetest.CommonCleanup):
    """CommonCleanup Section"""

    @aetest.subsection
    def disconnect(self, testbed):
        testbed.disconnect()


if __name__ == '__main__':

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
    args, _ = parser.parse_known_args()

    aetest.main(testbed=args.testbed)
