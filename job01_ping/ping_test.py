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
    def load_testbed(self, testbed):
        # Convert pyATS testbed to Genie Testbed
        logger.info('Converting pyATS testbed to Genie Testbed to support pyATS Library features')
        testbed = load(testbed)
        self.parent.parameters.update(testbed=testbed)

    @aetest.subsection
    def connect(self, testbed):
        """connect to all testbed devices"""

        # make sure testbed is provided
        assert testbed, 'Testbed is not provided!'

        # CommonSetup内で例外が発生するとテスト自体が停止してしまう
        # 単純にtestbed.connect()してもよいが、ここではCSR1000vルータにだけ接続する
        for _, dev in testbed.devices.items():
            if dev.platform == 'CSR1000v':
                try:
                    dev.connect(via='console')
                except (TimeoutError, StateMachineError, ConnectionError):
                    logger.error('Unable to connect to all devices')

###################################################################
###                     TESTCASES SECTION                       ###
###################################################################

class ping_class(aetest.Testcase):

    @aetest.setup
    def setup(self, testbed, ping_list):
        """ ルータに乗り込んでpingを実行して結果をクラス変数に保存する """

        self.ping_results = {}

        for name, dev in testbed.devices.items():
            # CSR1000vルータにのみ接続してある
            if dev.platform != 'CSR1000v':
                continue

            logger.info(f'{name} connected status: {dev.connected}')
            self.ping_results[name] = {}
            for ip in ping_list:
                logger.info(f'Pinging {ip} from {name}')
                try:
                    ping = dev.ping(ip)
                    pingSuccessRate = ping[(ping.find('percent')-4):ping.find('percent')].strip()
                    try:
                        self.ping_results[name][ip] = int(pingSuccessRate)
                    except:
                        self.ping_results[name][ip] = 0
                except:
                    self.ping_results[name][ip] = 0

    @aetest.test
    def test(self, steps):
        """ ping実行結果を検証する """
        for device_name, ips in self.ping_results.items():
            with steps.start(f'Looking for ping failures {device_name}', continue_=True) as device_step:
                for ip in ips:
                    with device_step.start(f'Checking Ping from {device_name} to {ip}', continue_=True):
                        reason = f'Device {device_name} had {ips[ip]}% success pinging {ip}'
                        if ips[ip] == 100:
                            device_step.passed(reason)
                        else:
                            device_step.failed(reason)

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

    # python ping_test.py --testbed ../lab.yml

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
