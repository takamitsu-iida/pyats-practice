#!/usr/bin/env python

# conn_check_test.py --testbed lab.yml

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
        links = ios1.find_links(ios2)

        assert len(links) >= 1, 'require one link between ios1 and ios2'

    @aetest.subsection
    def establish_connections(self, steps, ios1, ios2):
        with steps.start('Connecting to %s' % ios1.name):
            ios1.connect()

        with steps.start('Connecting to %s' % ios2.name):
            ios2.connect()


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
        with steps.start('Disconnecting from %s' % ios1.name):
            ios1.settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0
            ios1.settings.POST_DISCONNECT_WAIT_SEC = 0
            ios1.disconnect()

        with steps.start('Disconnecting from %s' % ios2.name):
            ios2.settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0
            ios2.settings.POST_DISCONNECT_WAIT_SEC = 0
            ios2.disconnect()


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

    # parse command line arguments only we know
    args, _ = parser.parse_known_args()

    aetest.main(testbed=args.testbed)
