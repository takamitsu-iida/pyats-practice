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

class interface_duplex(aetest.Testcase):
    @aetest.setup
    def setup(self, testbed):
        """Learn and save the interface details from the testbed devices."""

        # 実行結果をクラス変数に保管しておく
        self.learnt_interfaces = {}

        for device_name, device in testbed.devices.items():
            # Only attempt to learn details on supported network operation systems
            if device.os in ('ios', 'iosxe', 'iosxr', 'nxos'):
                logger.info(f'{device_name} connected status: {device.connected}')
                logger.info(f'Learning Interfaces for {device_name}')
                self.learnt_interfaces[device_name] = device.learn('interface').info

    @aetest.test
    def test(self, steps):
        # Loop over every device with learnt interfaces
        for device_name, interfaces in self.learnt_interfaces.items():
            with steps.start(f'Looking for half-duplex Interfaces on {device_name}', continue_=True) as device_step:

                # Loop over every interface that was learnt
                for interface_name, interface in interfaces.items():
                    with device_step.start(f'Checking Interface {interface_name}', continue_=True) as interface_step:

                        # Verify that this interface has 'duplex_mode
                        if 'duplex_mode' in interface.keys():
                            if interface['duplex_mode'] == 'half':
                                interface_step.failed(f'Device {device_name} Interface {interface_name} is in half-duplex mode')
                        else:
                            # If the interface has no duplex, mark as skipped
                            interface_step.skipped(f'Device {device_name} Interface {interface_name} has no duplex')
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
