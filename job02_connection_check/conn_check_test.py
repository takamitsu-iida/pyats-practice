#!/usr/bin/env python

import logging
import re

from pyats import aetest

logger = logging.getLogger(__name__)

###################################################################
###                  COMMON SETUP SECTION                       ###
###################################################################

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def check_topology(self,
                       testbed,
                       ios1_name='r1',
                       ios2_name='r2'):

        ios1 = testbed.devices[ios1_name]
        ios2 = testbed.devices[ios2_name]

        # add them to testscript parameters
        self.parent.parameters.update(ios1=ios1, ios2=ios2)

        # get corresponding links
        # links = ios1.find_links(ios2)
        # assert len(links) >= 1, 'require one link between ios1 and ios2'

    @aetest.subsection
    def establish_connections(self, steps, ios1, ios2):
        with steps.start(f'Connecting to {ios1.name}'):
            ios1.connect(via='console')

        with steps.start(f'Connecting to {ios2.name}'):
            ios2.connect(via='console')

###################################################################
###                     TESTCASES SECTION                       ###
###################################################################

@aetest.loop(device=('ios1', 'ios2'))
class PingTestcase(aetest.Testcase):

    @aetest.test.loop(destination=('192.168.255.1', '192.168.255.2'))
    def ping(self, device, destination):
        try:
            result = self.parameters[device].ping(destination)
        except Exception as e:
            message = 'Ping {} from device {} failed with error: {}'.format(destination, device, str(e))
            self.failed(message, goto=['exit'])
        else:
            match = re.search(r'Success rate is (?P<rate>\d+) percent', result)
            success_rate = match.group('rate')
            message = 'Ping {} with success rate of {}%'.format(destination, success_rate)
            logger.info(message)

#####################################################################
####                       COMMON CLEANUP SECTION                 ###
#####################################################################

class CommonCleanup(aetest.CommonCleanup):

    @aetest.subsection
    def disconnect(self, steps, ios1, ios2):
        with steps.start(f'Disconnecting from {ios1.name}'):
            ios1.disconnect()

        with steps.start('Disconnecting from {ios2.name}'):
            ios2.disconnect()


if __name__ == '__main__':

    # python conn_check_test.py --testbed ../lab.yml

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
