# インタフェース状態の判定テスト

テストベッド内の全装置に乗り込み、インタフェースの状態を学習。duplexがfullであればOKとして判定します。

<br>

### リプレイ

```bash
pyats run job duplex_job.py --testbed-file ../lab.yml --replay record
```

<br>

### テストスクリプト

インタフェースが何個あるかわからないので、学習させた情報にもとづいてループさせています。

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
    def connect(self, testbed):
        """
        テストベッドのCSR1000vに接続します。

        Args:
            testbed (_type_): 実行時に渡されるテストベッドです
        """

        # testbedが正しくロードされているか確認する(YAMLの書式エラーで失敗しているケースもある)
        assert testbed, 'Testbed is not provided!'

        # 全てのCSR1000vに接続します
        for _, dev in testbed.devices.items():
            if dev.platform != 'CSR1000v':
                continue
            try:
                dev.connect(via='console')
            except (TimeoutError, StateMachineError, ConnectionError):
                logger.error('Unable to connect to all devices')

###################################################################
###                     TESTCASES SECTION                       ###
###################################################################

class interface_duplex(aetest.Testcase):

    @aetest.setup
    def setup(self, testbed):
        """
        ルータのインタフェース情報を学習してクラス変数の保管する

        Args:
            testbed (_type_): テストベッド
        """

        # 結果を保存するクラス変数
        self.learnt_interfaces = {}

        # learn('interface')でインタフェース情報を学習する
        for name, dev in testbed.devices.items():
            if dev.platform != 'CSR1000v':
                continue
            if dev.is_connected() is False:
                logger.info(f'{name} connected status: {dev.connected}')
                continue
            logger.info(f'Learning Interfaces for {name}')
            self.learnt_interfaces[name] = dev.learn('interface').info


    @aetest.test
    def test(self, steps):
        """
        学習したインタフェース情報を探索して、全二重になっていないインタフェースを抽出する

        Args:
            steps (_type_): ステップ
        """

        # 学習した情報を取り出す
        # {'装置名', {学習したインタフェース情報}}
        for device_name, interfaces in self.learnt_interfaces.items():

            # 取り出した装置に関してのステップ
            with steps.start(f'Looking for half-duplex Interfaces on {device_name}', continue_=True) as device_step:

                # その装置のインタフェースに関して取り出す
                # {'interface_name': {学習したデータ}}
                for interface_name, interface in interfaces.items():

                    # 各インタフェースに関してのステップ
                    with device_step.start(f'Checking Interface {interface_name}', continue_=True) as interface_step:

                        # データの中に'duplex_mode'があるか確認して
                        if 'duplex_mode' in interface.keys():
                            # それが'half'になっていたらfaildにする
                            if interface['duplex_mode'] == 'half':
                                interface_step.failed(f'Device {device_name} Interface {interface_name} is in half-duplex mode')
                        else:
                            # Loopbackのようなインタフェースは'duplex_mode'を持たないのでスキップ
                            interface_step.skipped(f'Device {device_name} Interface {interface_name} has no duplex')


#####################################################################
####                       COMMON CLEANUP SECTION                 ###
#####################################################################

class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect(self, testbed):
        testbed.disconnect()


#
# スタンドアロンで実行
#
# python duplex_test.py --testbed ../lab.yml
#
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

```

実行結果。

```bash
+------------------------------------------------------------------------------+
|                                Easypy Report                                 |
+------------------------------------------------------------------------------+
pyATS Instance   : /home/iida/git/pyats-practice/.venv
Python Version   : cpython-3.8.10 (64bit)
CLI Arguments    : /home/iida/git/pyats-practice/.venv/bin/pyats run job duplex_job.py --testbed-file lab.yml
User             : iida
Host Server      : FCCLS0008993-00
Host OS Version  : Ubuntu 20.04 focal (x86_64)

Job Information
    Name         : duplex_job
    Start time   : 2022-10-18 15:12:05.790453+09:00
    Stop time    : 2022-10-18 15:12:25.795050+09:00
    Elapsed time : 20.004597
    Archive      : /home/iida/.pyats/archive/22-Oct/duplex_job.2022Oct18_15:11:56.372156.zip

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
Duplex: duplex_test.common_setup                                          PASSED
Duplex: duplex_test.interface_duplex                                      PASSED
Duplex: duplex_test.common_cleanup                                        PASSED

+------------------------------------------------------------------------------+
|                             Task Result Details                              |
+------------------------------------------------------------------------------+
Duplex: duplex_test
|-- common_setup                                                          PASSED
|   |-- load_testbed                                                      PASSED
|   `-- connect                                                           PASSED
|-- interface_duplex                                                      PASSED
|   |-- setup                                                             PASSED
|   `-- test                                                              PASSED
|       |-- STEP 1: Looking for half-duplex Interfaces on r1              PASSED
|       |-- STEP 1.1: Checking Interface GigabitEthernet4                 PASSED
|       |-- STEP 1.2: Checking Interface GigabitEthernet3                 PASSED
|       |-- STEP 1.3: Checking Interface GigabitEthernet2                 PASSED
|       |-- STEP 1.4: Checking Interface GigabitEthernet1                 PASSED
|       |-- STEP 1.5: Checking Interface Loopback0                       SKIPPED
|       |-- STEP 2: Looking for half-duplex Interfaces on r2              PASSED
|       |-- STEP 2.1: Checking Interface Loopback0                       SKIPPED
|       |-- STEP 2.2: Checking Interface GigabitEthernet4                 PASSED
|       |-- STEP 2.3: Checking Interface GigabitEthernet3                 PASSED
|       |-- STEP 2.4: Checking Interface GigabitEthernet2                 PASSED
|       |-- STEP 2.5: Checking Interface GigabitEthernet1                 PASSED
|       |-- STEP 3: Looking for half-duplex Interfaces on r3              PASSED
|       |-- STEP 3.1: Checking Interface Loopback0                       SKIPPED
|       |-- STEP 3.2: Checking Interface GigabitEthernet4                 PASSED
|       |-- STEP 3.3: Checking Interface GigabitEthernet3                 PASSED
|       |-- STEP 3.4: Checking Interface GigabitEthernet2                 PASSED
|       |-- STEP 3.5: Checking Interface GigabitEthernet1                 PASSED
|       |-- STEP 4: Looking for half-duplex Interfaces on r4              PASSED
|       |-- STEP 4.1: Checking Interface Loopback0                       SKIPPED
|       |-- STEP 4.2: Checking Interface GigabitEthernet4                 PASSED
|       |-- STEP 4.3: Checking Interface GigabitEthernet3                 PASSED
|       |-- STEP 4.4: Checking Interface GigabitEthernet2                 PASSED
|       `-- STEP 4.5: Checking Interface GigabitEthernet1                 PASSED
`-- common_cleanup                                                        PASSED
    `-- disconnect                                                        PASSED
```

ブラウザでの確認。

![実行結果](https://takamitsu-iida.github.io/pyats-practice/job03_duplex/img/fig1.PNG "実行結果")
