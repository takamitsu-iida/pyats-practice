# ping

テストベッド内の全てのルータに乗り込み、指定された宛先にpingを打ち、応答が100%あればOKとするテストです。

pingの宛先リスト。

```python
ping_list = [
    '192.168.12.1',
    '192.168.12.2',
    '192.168.13.1',
    '192.168.13.3',
    '192.168.24.2',
    '192.168.24.4',
    '192.168.34.3',
    '192.168.34.4',
    '192.168.255.1',
    '192.168.255.2',
    '192.168.255.3',
    '192.168.255.4'
]
```

ここではテスト実行時に引数として渡していますが、YAMLファイルに記述してdatafileとして渡すほうがよいでしょう。
Pythonスクリプトを書き換えるよりも、データファイルを書き換える方が心理的負荷が軽いように思います。

<br>

### リプレイ

```bash
pyats run job ping_job.py --testbed-file ../lab.yml --replay record
```

<br>

### テストスクリプト

セットアップセクションではGenieのpingパーサーを使って上記の宛先にpingして、応答のパーセントを保存します。

テストセクションでは結果を保存したself.ping_resultsを取り出して、
接続したルータでfor文を回し、続いてpingの宛先でfor文を回します。
値が100%ならpassed、それ以外はfailedとします。

```python
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

def get_success_rate(parsed):
    """
    parse('ping x.x.x.x')の結果からsuccess_rateを抽出して返却
    """
    # pingパーサーのスキーマはここにある通り
    # https://github.com/CiscoTestAutomation/genieparser/blob/master/src/genie/libs/parser/iosxe/ping.py#L48
    #
    # {'ping': {'address': '192.168.255.4',
    #           'result_per_line': ['!!!!!'],
    #           'statistics': {'received': 5,
    #                          'round_trip': {'avg_ms': 1, 'max_ms': 2, 'min_ms': 1},
    #                          'send': 5,
    #                          'success_rate_percent': 100.0},　★これだけを返す
    #           'timeout_secs': 2}}
    success_rate = parsed.q.raw('[ping][statistics][success_rate_percent]')
    return success_rate


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
                    parsed = dev.parse(f'ping {ip}')
                    success_rate = get_success_rate(parsed)
                    self.ping_results[name][ip] = success_rate
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
```

実行結果。

```bash
+------------------------------------------------------------------------------+
|                                Easypy Report                                 |
+------------------------------------------------------------------------------+
pyATS Instance   : /home/iida/git/pyats-practice/.venv
Python Version   : cpython-3.8.10 (64bit)
CLI Arguments    : /home/iida/git/pyats-practice/.venv/bin/pyats run job ping_job.py --testbed-file lab.yml
User             : iida
Host Server      : FCCLS0008993-00
Host OS Version  : Ubuntu 20.04 focal (x86_64)

Job Information
    Name         : ping_job
    Start time   : 2022-10-18 14:24:16.096913+09:00
    Stop time    : 2022-10-18 14:24:32.114492+09:00
    Elapsed time : 16.017579
    Archive      : /home/iida/.pyats/archive/22-Oct/ping_job.2022Oct18_14:24:07.762667.zip

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
Ping: ping_test.common_setup                                              PASSED
Ping: ping_test.ping_class                                                PASSED
Ping: ping_test.common_cleanup                                            PASSED

+------------------------------------------------------------------------------+
|                             Task Result Details                              |
+------------------------------------------------------------------------------+
Ping: ping_test
|-- common_setup                                                          PASSED
|   |-- load_testbed                                                      PASSED
|   `-- connect                                                           PASSED
|-- ping_class                                                            PASSED
|   |-- setup                                                             PASSED
|   `-- test                                                              PASSED
|       |-- STEP 1: Looking for ping failures r1                          PASSED
|       |-- STEP 1.1: Checking Ping from r1 to 192.168.12.1               PASSED
|       |-- STEP 1.2: Checking Ping from r1 to 192.168.12.2               PASSED
|       |-- STEP 1.3: Checking Ping from r1 to 192.168.13.1               PASSED
|       |-- STEP 1.4: Checking Ping from r1 to 192.168.13.3               PASSED
|       |-- STEP 1.5: Checking Ping from r1 to 192.168.24.2               PASSED
|       |-- STEP 1.6: Checking Ping from r1 to 192.168.24.4               PASSED
|       |-- STEP 1.7: Checking Ping from r1 to 192.168.34.3               PASSED
|       |-- STEP 1.8: Checking Ping from r1 to 192.168.34.4               PASSED
|       |-- STEP 1.9: Checking Ping from r1 to 192.168.255.1              PASSED
|       |-- STEP 1.10: Checking Ping from r1 to 192.168.255.2             PASSED
|       |-- STEP 1.11: Checking Ping from r1 to 192.168.255.3             PASSED
|       |-- STEP 1.12: Checking Ping from r1 to 192.168.255.4             PASSED
|       |-- STEP 2: Looking for ping failures r2                          PASSED
|       |-- STEP 2.1: Checking Ping from r2 to 192.168.12.1               PASSED
|       |-- STEP 2.2: Checking Ping from r2 to 192.168.12.2               PASSED
|       |-- STEP 2.3: Checking Ping from r2 to 192.168.13.1               PASSED
|       |-- STEP 2.4: Checking Ping from r2 to 192.168.13.3               PASSED
|       |-- STEP 2.5: Checking Ping from r2 to 192.168.24.2               PASSED
|       |-- STEP 2.6: Checking Ping from r2 to 192.168.24.4               PASSED
|       |-- STEP 2.7: Checking Ping from r2 to 192.168.34.3               PASSED
|       |-- STEP 2.8: Checking Ping from r2 to 192.168.34.4               PASSED
|       |-- STEP 2.9: Checking Ping from r2 to 192.168.255.1              PASSED
|       |-- STEP 2.10: Checking Ping from r2 to 192.168.255.2             PASSED
|       |-- STEP 2.11: Checking Ping from r2 to 192.168.255.3             PASSED
|       |-- STEP 2.12: Checking Ping from r2 to 192.168.255.4             PASSED
|       |-- STEP 3: Looking for ping failures r3                          PASSED
|       |-- STEP 3.1: Checking Ping from r3 to 192.168.12.1               PASSED
|       |-- STEP 3.2: Checking Ping from r3 to 192.168.12.2               PASSED
|       |-- STEP 3.3: Checking Ping from r3 to 192.168.13.1               PASSED
|       |-- STEP 3.4: Checking Ping from r3 to 192.168.13.3               PASSED
|       |-- STEP 3.5: Checking Ping from r3 to 192.168.24.2               PASSED
|       |-- STEP 3.6: Checking Ping from r3 to 192.168.24.4               PASSED
|       |-- STEP 3.7: Checking Ping from r3 to 192.168.34.3               PASSED
|       |-- STEP 3.8: Checking Ping from r3 to 192.168.34.4               PASSED
|       |-- STEP 3.9: Checking Ping from r3 to 192.168.255.1              PASSED
|       |-- STEP 3.10: Checking Ping from r3 to 192.168.255.2             PASSED
|       |-- STEP 3.11: Checking Ping from r3 to 192.168.255.3             PASSED
|       |-- STEP 3.12: Checking Ping from r3 to 192.168.255.4             PASSED
|       |-- STEP 4: Looking for ping failures r4                          PASSED
|       |-- STEP 4.1: Checking Ping from r4 to 192.168.12.1               PASSED
|       |-- STEP 4.2: Checking Ping from r4 to 192.168.12.2               PASSED
|       |-- STEP 4.3: Checking Ping from r4 to 192.168.13.1               PASSED
|       |-- STEP 4.4: Checking Ping from r4 to 192.168.13.3               PASSED
|       |-- STEP 4.5: Checking Ping from r4 to 192.168.24.2               PASSED
|       |-- STEP 4.6: Checking Ping from r4 to 192.168.24.4               PASSED
|       |-- STEP 4.7: Checking Ping from r4 to 192.168.34.3               PASSED
|       |-- STEP 4.8: Checking Ping from r4 to 192.168.34.4               PASSED
|       |-- STEP 4.9: Checking Ping from r4 to 192.168.255.1              PASSED
|       |-- STEP 4.10: Checking Ping from r4 to 192.168.255.2             PASSED
|       |-- STEP 4.11: Checking Ping from r4 to 192.168.255.3             PASSED
|       `-- STEP 4.12: Checking Ping from r4 to 192.168.255.4             PASSED
`-- common_cleanup                                                        PASSED
    `-- disconnect                                                        PASSED
```

ブラウザでの確認。

![実行結果](https://takamitsu-iida.github.io/pyats-practice/job01_ping/img/fig1.PNG "実行結果")

![実行結果](https://takamitsu-iida.github.io/pyats-practice/job01_ping/img/fig2.PNG "実行結果")