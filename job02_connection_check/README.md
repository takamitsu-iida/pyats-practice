# connection check

テストベッド内のルータr1とr2の間で疎通できるか、確認する例です。

デコレータ`@aetest.loop(device=('ios1', 'ios2'))`を付与することで、装置に対してループさせます。

デコレータ`@aetest.test.loop(destination=('192.168.255.1', '192.168.255.2'))`を付与することで、pingの宛先に対してループさせています。

```python
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

    @aetest.subsection
    def establish_connections(self, steps, ios1, ios2):
        with steps.start('Connecting to %s' % ios1.name):
            ios1.connect(via='console')
        with steps.start('Connecting to %s' % ios2.name):
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
```

実行結果。

```bash
+------------------------------------------------------------------------------+
|                                Easypy Report                                 |
+------------------------------------------------------------------------------+
pyATS Instance   : /home/iida/git/pyats-practice/.venv
Python Version   : cpython-3.8.10 (64bit)
CLI Arguments    : /home/iida/git/pyats-practice/.venv/bin/pyats run job conn_check_job.py --testbed-file lab.yml
User             : iida
Host Server      : FCCLS0008993-00
Host OS Version  : Ubuntu 20.04 focal (x86_64)

Job Information
    Name         : conn_check_job
    Start time   : 2022-10-18 14:29:25.368682+09:00
    Stop time    : 2022-10-18 14:29:32.936579+09:00
    Elapsed time : 7.567897
    Archive      : /home/iida/.pyats/archive/22-Oct/conn_check_job.2022Oct18_14:29:15.473917.zip

Total Tasks    : 1

Overall Stats
    Passed     : 4
    Passx      : 0
    Failed     : 0
    Aborted    : 0
    Blocked    : 0
    Skipped    : 0
    Errored    : 0

    TOTAL      : 4

Success Rate   : 100.00 %

+------------------------------------------------------------------------------+
|                             Task Result Summary                              |
+------------------------------------------------------------------------------+
conn_check: conn_check_test.common_setup                                  PASSED
conn_check: conn_check_test.PingTestcase[device=ios1]                     PASSED
conn_check: conn_check_test.PingTestcase[device=ios2]                     PASSED
conn_check: conn_check_test.common_cleanup                                PASSED

+------------------------------------------------------------------------------+
|                             Task Result Details                              |
+------------------------------------------------------------------------------+
conn_check: conn_check_test
|-- common_setup                                                          PASSED
|   |-- check_topology                                                    PASSED
|   `-- establish_connections                                             PASSED
|       |-- STEP 1: Connecting to r1                                      PASSED
|       `-- STEP 2: Connecting to r2                                      PASSED
|-- PingTestcase[device=ios1]                                             PASSED
|   |-- ping[destination=192.168.255.1]                                   PASSED
|   `-- ping[destination=192.168.255.2]                                   PASSED
|-- PingTestcase[device=ios2]                                             PASSED
|   |-- ping[destination=192.168.255.1]                                   PASSED
|   `-- ping[destination=192.168.255.2]                                   PASSED
`-- common_cleanup                                                        PASSED
    `-- disconnect                                                        PASSED
        |-- STEP 1: Disconnecting from r1                                 PASSED
        `-- STEP 2: Disconnecting from r2                                 PASSED
```

ブラウザでの確認。

![実行結果](https://takamitsu-iida.github.io/pyats-practice/job02_duplex/img/fig1.PNG "実行結果")
