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

セットアップセクションではuniconのping()を使って上記の宛先にpingして、応答のパーセントを保存します。

テストセクションでは結果を保存したself.ping_resultsを取り出して、
接続したルータでfor文を回し、続いてpingの宛先でfor文を回します。
値が100%ならpassed、それ以外はfailedとします。

```python
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