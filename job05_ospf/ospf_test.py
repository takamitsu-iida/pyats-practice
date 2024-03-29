#!/usr/bin/env python

import logging

from pprint import pformat

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
        r1とr4に接続します。

        Args:
            testbed (genie.libs.conf.testbed.Testbed): スクリプト実行時に渡されるテストベッド
        """

        # testbedが正しくロードされているか確認する
        assert testbed, 'Testbed is not provided!'

        routers = ('r1', 'r4')

        for router in routers:
            r = testbed.devices[router]
            try:
                r.connect()
            except (TimeoutError, StateMachineError, ConnectionError):
                logger.error(f'Unable to connect to {router}')


###################################################################
###                     TESTCASES SECTION                       ###
###################################################################

class ospf_class(aetest.Testcase):

    @aetest.setup
    def setup(self, testbed):
        """
        r1とr4に関してparse('show ip ospf neighbor')します。

        Args:
            testbed (genie.libs.conf.testbed.Testbed): スクリプト実行時に渡されるテストベッド
        """
        routers = ('r1', 'r4')

        self.parsed = {}
        for router in routers:
            r = testbed.devices[router]
            self.parsed[router] = r.parse('show ip ospf neighbor')


    @aetest.test
    def test(self, steps):
        """
        ネイバー状態が期待通りか検証する
        """

        # show ip ospf neighborのスキーマ
        # https://github.com/CiscoTestAutomation/genieparser/blob/master/src/genie/libs/parser/iosxe/show_ospf.py#L8691

        # schema = {
        #     'interfaces':
        #         { Any():
        #             {'neighbors':
        #                 { Any():
        #                     {'priority': int,
        #                      'state':str,
        #                      'dead_time':str,
        #                      'address':str,
        #                 },
        #             },
        #         },
        #     },
        # }

        # {'interfaces': {'GigabitEthernet1': {'neighbors': {'192.168.255.2': {'address': '192.168.12.2',
        #                                                                     'dead_time': '00:00:37',
        #                                                                     'priority': 0,
        #                                                                     'state': 'FULL/  '
        #                                                                             '-'}}},
        #                 'GigabitEthernet2': {'neighbors': {'192.168.255.3': {'address': '192.168.13.3',
        #                                                                     'dead_time': '00:00:39',
        #                                                                     'priority': 0,
        #                                                                     'state': 'FULL/  '
        #                                                                             '-'}}}}}

        # r1に関してのステップ
        with steps.start('Looking for ospf neighbor on r1', continue_=True) as r1_step:
            # parse()した結果を取り出す
            parsed = self.parsed['r1']

            # 期待値はこれ
            # r1#show ip os neighbor
            # Neighbor ID     Pri   State           Dead Time   Address         Interface
            # 192.168.255.3     0   FULL/  -        00:00:31    192.168.13.3    GigabitEthernet2
            # 192.168.255.2     0   FULL/  -        00:00:37    192.168.12.2    GigabitEthernet1

            # Gig1の先に192.168.255.2がいるか確認
            with r1_step.start('Looking for neighbor on Gig1', continue_=True) as gig1_step:
                nbr = parsed.q.contains('GigabitEthernet1').contains('192.168.255.2').reconstruct()
                if nbr:
                    logger.info(pformat(nbr))
                else:
                    gig1_step.failed('expected neighbor 192.168.255.2 not found.')

            # Gig2の先に192.168.255.3がいるか確認
            with r1_step.start('Looking for neighbor on Gig2', continue_=True) as gig2_step:
                nbr = parsed.q.contains('GigabitEthernet2').contains('192.168.255.3').reconstruct()
                if nbr:
                    logger.info(pformat(nbr))
                else:
                    gig2_step.failed('expected neighbor 192.168.255.3 not found.')

        # r4に関してのステップ
        with steps.start('Looking for ospf neighbor on r4', continue_=True) as r4_step:
            # parse()した結果を取り出す
            parsed = self.parsed['r4']

            # 期待値はこれ
            # r4#show ip os ne
            #
            # Neighbor ID     Pri   State           Dead Time   Address         Interface
            # 192.168.255.3     0   FULL/  -        00:00:31    192.168.34.3    GigabitEthernet1
            # 192.168.255.2     0   FULL/  -        00:00:34    192.168.24.2    GigabitEthernet2

            # Gig1の先に192.168.255.3がいるか確認
            with r4_step.start('Looking for neighbor on Gig1', continue_=True) as gig1_step:
                nbr = parsed.q.contains('GigabitEthernet1').contains('192.168.255.3').reconstruct()
                if nbr:
                    logger.info(pformat(nbr))
                else:
                    gig1_step.failed('expected neighbor 192.168.255.3 not found.')

            # Gig2の先に192.168.255.2がいるか確認
            with r4_step.start('Looking for neighbor on Gig2', continue_=True) as gig2_step:
                nbr = parsed.q.contains('GigabitEthernet2').contains('192.168.255.2').reconstruct()
                if nbr:
                    logger.info(pformat(nbr))
                else:
                    gig2_step.failed('expected neighbor 192.168.255.2 not found.')


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
# スタンドアロンで実行
#
# python ospf_test.py --testbed ../lab.yml
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
