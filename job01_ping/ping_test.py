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

        # connect to all testbed devices
        #   By default ANY error in the CommonSetup will fail the entire test run
        #   Here we catch common exceptions if a device is unavailable to allow test to continue
        try:
            testbed.connect()
        except (TimeoutError, StateMachineError, ConnectionError):
            logger.error('Unable to connect to all devices')


###################################################################
###                     TESTCASES SECTION                       ###
###################################################################

class ping_class(aetest.Testcase):

    @aetest.setup
    def setup(self, testbed, ping_list):
        """ Make sure devices can ping a list of addresses. """

        # Create an array of destination IPs from our argparse
        ping_list = ping_list.split()

        # 実行結果をクラス内変数に保管しておく
        self.ping_results = {}

        for device_name, device in testbed.devices.items():
            # Only attempt to ping on supported network operation systems
            if device.os in ('ios', 'iosxe', 'iosxr', 'nxos'):
                logger.info(f'{device_name} connected status: {device.connected}')
                self.ping_results[device_name] = {}
                for ip in ping_list:
                    logger.info(f'Pinging {ip} from {device_name}')
                    try:
                        ping = device.ping(ip)
                        pingSuccessRate = ping[(ping.find('percent')-4):ping.find('percent')].strip()
                        try:
                            self.ping_results[device_name][ip] = int(pingSuccessRate)
                        except:
                            self.ping_results[device_name][ip] = 0
                    except:
                        self.ping_results[device_name][ip] = 0

    @aetest.test
    def test(self, steps):
        # Loop over every ping result
        for device_name, ips in self.ping_results.items():
            with steps.start(f'Looking for ping failures {device_name}', continue_=True) as device_step:
                # Loop over every ping result
                for ip in ips:
                    with device_step.start(f'Checking Ping from {device_name} to {ip}', continue_=True) as ping_step:
                        if ips[ip] < 100:
                            device_step.failed(f'Device {device_name} had {ips[ip]}% success pinging {ip}')

#####################################################################
####                       COMMON CLEANUP SECTION                 ###
#####################################################################

class CommonCleanup(aetest.CommonCleanup):
    """CommonCleanup Section"""

    # @aetest.subsection
    # def subsection_cleanup_one(self):
    #     pass

    @aetest.subsection
    def disconnect(self, testbed):
        testbed.disconnect()

#
# stand-alone test
#
if __name__ == "__main__":
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

    parser.add_argument(
        '--dest',
        dest = 'ping_list',
        type=str,
        default = '192.168.255.1 192.168.255.2',
        help = 'space delimted list of IP address(es) to test connectivity'
    )

    # parse command line arguments only we know
    args, _ = parser.parse_known_args()

    aetest.main(testbed=args.testbed, ping_list=args.ping_list)
