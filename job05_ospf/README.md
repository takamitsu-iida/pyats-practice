# OSPFのネイバー状態の判定テスト

OSPFネイバーが期待通りかを判定します。

<br>


### リプレイ

```bash
pyats run job ospf_job.py --testbed-file ../lab.yml --replay record
```

<br>

### テストスクリプト

スクリプトは長めですが、やっていることは単純です。

ループも使わず、ストレートフォワードな実装です。
テストスクリプトはこんなんでいいんじゃないかと思います。

```python
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
        r1とr4に接続する
        """
        routers = ('r1', 'r4')

        for router in routers:
            r = testbed.devices[router]
            try:
                r.connect(via='console')
            except (TimeoutError, StateMachineError, ConnectionError):
                logger.error(f'Unable to connect to {router}')


###################################################################
###                     TESTCASES SECTION                       ###
###################################################################

class ospf_class(aetest.Testcase):

    @aetest.setup
    def setup(self, testbed):
        """
        r1とr4に関してparse('show ip ospf neighbor')する
        """
        routers = ('r1', 'r4')

        self.parsed = {}
        for router in routers:
            r = testbed.devices[router]
            self.parsed[router] = r.parse('show ip ospf neighbor')


    @aetest.test
    def test(self, steps, testbed):
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
        # testbedそのものから切断
        testbed.disconnect()

#
# stand-alone test
#
if __name__ == "__main__":

    # python ospf_test.py --testbed ../lab.yml

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
```

<br>

### 実行結果

```bash
+------------------------------------------------------------------------------+
|                                Easypy Report                                 |
+------------------------------------------------------------------------------+
pyATS Instance   : /home/iida/git/pyats-practice/.venv
Python Version   : cpython-3.8.10 (64bit)
CLI Arguments    : /home/iida/git/pyats-practice/.venv/bin/pyats run job ospf_job.py --testbed-file ../lab.yml
User             : iida
Host Server      : FCCLS0008993-00
Host OS Version  : Ubuntu 20.04 focal (x86_64)

Job Information
    Name         : ospf_job
    Start time   : 2022-10-25 12:02:05.759684+09:00
    Stop time    : 2022-10-25 12:02:23.717775+09:00
    Elapsed time : 17.958091
    Archive      : /home/iida/.pyats/archive/22-Oct/ospf_job.2022Oct25_12:01:55.985110.zip

Total Tasks    : 1

Overall Stats
    Passed     : 3
    Passx      : 0
    Failed     : 0
    Aborted    : 0
    Blocked    : 0
    Skipped    : 0
    Errored    : 0

    TOTAL      : 3

Success Rate   : 100.00 %

+------------------------------------------------------------------------------+
|                             Task Result Summary                              |
+------------------------------------------------------------------------------+
OspfNeighbor: ospf_test.common_setup                                      PASSED
OspfNeighbor: ospf_test.ospf_class                                        PASSED
OspfNeighbor: ospf_test.common_cleanup                                    PASSED

+------------------------------------------------------------------------------+
|                             Task Result Details                              |
+------------------------------------------------------------------------------+
OspfNeighbor: ospf_test
|-- common_setup                                                          PASSED
|   |-- load_testbed                                                      PASSED
|   `-- connect                                                           PASSED
|-- ospf_class                                                            PASSED
|   |-- setup                                                             PASSED
|   `-- test                                                              PASSED
|       |-- STEP 1: Looking for ospf neighbor on r1                       PASSED
|       |-- STEP 1.1: Looking for neighbor on Gig1                        PASSED
|       |-- STEP 1.2: Looking for neighbor on Gig2                        PASSED
|       |-- STEP 2: Looking for ospf neighbor on r4                       PASSED
|       |-- STEP 2.1: Looking for neighbor on Gig1                        PASSED
|       `-- STEP 2.2: Looking for neighbor on Gig2                        PASSED
`-- common_cleanup                                                        PASSED
    `-- disconnect                                                        PASSED
```

ブラウザでの確認。

![実行結果](https://takamitsu-iida.github.io/pyats-practice/job05_ospf/img/fig1.PNG "実行結果")
