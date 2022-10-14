# pyats-practice

https://developer.cisco.com/pyats/ にあるIntroduction to pyATSが秀逸。
ブラウザの中に説明とターミナルとエディタがあり、ページ内で実行して結果を確認できる

- learnを実行してログを収集

```bash
pyats learn interface ospf platform --testbed-file working-tb.yaml --output working_snapshot
```

- 再びlearnを実行してログを収集

```bash
pyats learn interface ospf platform --testbed-file broken-tb.yaml --output broken_snapshot
```

- 収集したログのdiffを取る

```bash
pyats diff working_snapshot broken_snapshot --output diff_snapshot
```

上記を実行するだけでも使う価値があると思わせる内容になっている。

<br><br>

## ドキュメント

https://pubhub.devnetcloud.com/media/pyats/docs/index.html

https://developer.cisco.com/pyats/

https://developer.cisco.com/docs/pyats/

https://developer.cisco.com/docs/genie-docs/

https://github.com/CiscoTestAutomation/examples

https://github.com/CiscoTestAutomation/solutions_examples


<br><br>

## install

venvでpython環境を作る。

```bash
$ python3 -m venv .venv
```

direnvを設定してディレクトリに入ったら自動でactivateする。

```bash
echo 'source .venv/bin/activate' > .envrc
echo 'unset PS1' >> .envrc
direnv allow
```

pyatsに関連したモジュールを全てインストールする。

```bash
pip install pyats[full]
pip install rest.connector
pip install yang.connector
```

<br><br>

## testbed

インベントリをtestbedと呼ぶ。testbedはYAML形式で記述する。

装置に関する情報だけでなく、どのように接続しているか、も記述する。

プロンプトの処理や、接続時にデフォルトで打ち込まれるコマンドなど、独特な動きをする。
装置への接続に関してはマニュアルに目を通した方が結果的に近道。

https://pubhub.devnetcloud.com/media/unicon/docs/user_guide/connection.html


```yml
---

#
# testbed file for lab
#

testbed:
  name: eve-ng
  credentials:
    default:
      username: cisco
      password: cisco
    enable:
      password: cisco

devices:

  # 踏み台サーバ
  fumidai:
    os: linux
    type: linux
    credentials:
      # sshコマンドでログインするが、~/.ssh/configは読まないのでユーザ名はここで指定する
      default:
        username: bastion
    connections:
      vty:
        protocol: ssh
        ip: 10.38.220.46

  # must be hostname, same as prompt
  R1:
    os: iosxe
    type: router
    platform: csr1000v
    connections:
      vty:
        proxy: fumidai
        protocol: ssh -oKexAlgorithms=+diffie-hellman-group14-sha1,diffie-hellman-group-exchange-sha1
        ip: 192.168.0.11
        port: -p 22

  R2:
    os: iosxe
    type: router
    platform: csr1000v
    connections:
      vty:
        proxy: fumidai
        protocol: ssh -oKexAlgorithms=+diffie-hellman-group14-sha1,diffie-hellman-group-exchange-sha1
        ip: 192.168.0.12
        port: -p 22

topology:
  R1:
    interfaces:
      GigabitEthernet4:
        ipv4: 192.168.0.11/24
        link: link-1
        type: ethernet
      Loopback0:
        ipv4: 192.168.255.1/32
        link: R1_Loopback0
        type: loopback

  R2:
    interfaces:
      GigabitEthernet4:
        ipv4: 192.168.0.12/24
        link: link-1
        type: ethernet
      Loopback0:
        ipv4: 192.168.255.2/32
        link: R2_Loopback0
        type: loopback
```


<br><br>

## job

```bash
pyats run job job.py --testbed-file lab-testbed.yml --html-logs
```

<br><br>

### basic

`pyats run job --testbed-file ~/lab-testbed.yml basic/basic_example_job.py`

```bash
iida@FCCLS0008993-00:~/pyats/examples/basic$ pyats run job --testbed-file ~/lab-testbed.yml basic/basic_example_job.py
2022-01-08T16:58:08: %EASYPY-INFO: Starting job run: basic_example_job
2022-01-08T16:58:08: %EASYPY-INFO: Runinfo directory: /home/iida/.pyats/runinfo/basic_example_job.2022Jan08_16:58:07.895112
2022-01-08T16:58:08: %EASYPY-INFO: --------------------------------------------------------------------------------
2022-01-08T16:58:08: %EASYPY-INFO: Testbed file /home/iida/lab-testbed.yml exists and is readable.
2022-01-08T16:58:11: %ATS-INFO: Checking all devices are up and ready is disabled, '--check-all-devices-up' must be set to True in case of pyats runs or '-check_all_devices_up' set to True in case of legacy easypy runs
2022-01-08T16:58:11: %EASYPY-INFO: Starting task execution: Task-1
2022-01-08T16:58:11: %EASYPY-INFO:     test harness = pyats.aetest
2022-01-08T16:58:11: %EASYPY-INFO:     testscript   = /home/iida/pyats/examples/basic/basic_example_script.py
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %AETEST-INFO: |                            Starting common setup                             |
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %AETEST-INFO: |                   Starting subsection sample_subsection_1                    |
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %SCRIPT-INFO: Aetest Common Setup
2022-01-08T16:58:11: %AETEST-INFO: The result of subsection sample_subsection_1 is => PASSED
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %AETEST-INFO: |                   Starting subsection sample_subsection_2                    |
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %SCRIPT-INFO: Inside subsection sample_subsection_2
2022-01-08T16:58:11: %SCRIPT-INFO: Inside class common_setup
2022-01-08T16:58:11: %AETEST-INFO: The result of subsection sample_subsection_2 is => PASSED
2022-01-08T16:58:11: %AETEST-INFO: The result of common setup is => PASSED
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %AETEST-INFO: |                           Starting testcase tc_one                           |
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %AETEST-INFO: |                      Starting section prepare_testcase                       |
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %SCRIPT-INFO: Preparing the test
2022-01-08T16:58:11: %SCRIPT-INFO: section prepare_testcase
2022-01-08T16:58:11: %AETEST-INFO: The result of section prepare_testcase is => PASSED
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %AETEST-INFO: |                        Starting section simple_test_1                        |
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %SCRIPT-INFO: First test section
2022-01-08T16:58:11: %AETEST-INFO: The result of section simple_test_1 is => PASSED
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %AETEST-INFO: |                        Starting section simple_test_2                        |
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %SCRIPT-INFO: Second test section
2022-01-08T16:58:11: %AETEST-INFO: The result of section simple_test_2 is => PASSED
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %AETEST-INFO: |                       Starting section clean_testcase                        |
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %SCRIPT-INFO: Pass testcase cleanup
2022-01-08T16:58:11: %AETEST-INFO: The result of section clean_testcase is => PASSED
2022-01-08T16:58:11: %AETEST-INFO: The result of testcase tc_one is => PASSED
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %AETEST-INFO: |                           Starting testcase tc_two                           |
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %AETEST-INFO: |                        Starting section simple_test_1                        |
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %SCRIPT-INFO: First test section
2022-01-08T16:58:11: %AETEST-ERROR: Failed reason: This is an intentional failure
2022-01-08T16:58:11: %AETEST-INFO: The result of section simple_test_1 is => FAILED
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %AETEST-INFO: |                        Starting section simple_test_2                        |
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %SCRIPT-INFO: Second test section
2022-01-08T16:58:11: %AETEST-INFO: The result of section simple_test_2 is => PASSED
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %AETEST-INFO: |                       Starting section clean_testcase                        |
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %SCRIPT-INFO: Pass testcase cleanup
2022-01-08T16:58:11: %AETEST-INFO: The result of section clean_testcase is => PASSED
2022-01-08T16:58:11: %AETEST-INFO: The result of testcase tc_two is => FAILED
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %AETEST-INFO: |                           Starting common cleanup                            |
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %AETEST-INFO: |                     Starting subsection clean_everything                     |
2022-01-08T16:58:11: %AETEST-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:11: %SCRIPT-INFO: Aetest Common Cleanup
2022-01-08T16:58:11: %AETEST-INFO: The result of subsection clean_everything is => PASSED
2022-01-08T16:58:11: %AETEST-INFO: The result of common cleanup is => PASSED
2022-01-08T16:58:11: %CONTRIB-INFO: WebEx Token not given as argument or in config. No WebEx notification will be sent
2022-01-08T16:58:11: %EASYPY-INFO: --------------------------------------------------------------------------------
2022-01-08T16:58:11: %EASYPY-INFO: Job finished. Wrapping up...
2022-01-08T16:58:12: %EASYPY-INFO: Creating archive file: /home/iida/.pyats/archive/22-Jan/basic_example_job.2022Jan08_16:58:07.895112.zip
2022-01-08T16:58:13: %EASYPY-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:13: %EASYPY-INFO: |                                Easypy Report                                 |
2022-01-08T16:58:13: %EASYPY-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:13: %EASYPY-INFO: pyATS Instance   : /usr
2022-01-08T16:58:13: %EASYPY-INFO: Python Version   : cpython-3.8.5 (64bit)
2022-01-08T16:58:13: %EASYPY-INFO: CLI Arguments    : /home/iida/.local/bin/pyats run job basic_example_job.py --testbed-file /home/iida/lab-testbed.yml
2022-01-08T16:58:13: %EASYPY-INFO: User             : iida
2022-01-08T16:58:13: %EASYPY-INFO: Host Server      : FCCLS0008993-00
2022-01-08T16:58:13: %EASYPY-INFO: Host OS Version  : Ubuntu 20.04 focal (x86_64)
2022-01-08T16:58:13: %EASYPY-INFO:
2022-01-08T16:58:13: %EASYPY-INFO: Job Information
2022-01-08T16:58:13: %EASYPY-INFO:     Name         : basic_example_job
2022-01-08T16:58:13: %EASYPY-INFO:     Start time   : 2022-01-08 16:58:11.640604
2022-01-08T16:58:13: %EASYPY-INFO:     Stop time    : 2022-01-08 16:58:11.887459
2022-01-08T16:58:13: %EASYPY-INFO:     Elapsed time : 0.246855
2022-01-08T16:58:13: %EASYPY-INFO:     Archive      : /home/iida/.pyats/archive/22-Jan/basic_example_job.2022Jan08_16:58:07.895112.zip
2022-01-08T16:58:13: %EASYPY-INFO:
2022-01-08T16:58:13: %EASYPY-INFO: Total Tasks    : 1
2022-01-08T16:58:13: %EASYPY-INFO:
2022-01-08T16:58:13: %EASYPY-INFO: Overall Stats
2022-01-08T16:58:13: %EASYPY-INFO:     Passed     : 3
2022-01-08T16:58:13: %EASYPY-INFO:     Passx      : 0
2022-01-08T16:58:13: %EASYPY-INFO:     Failed     : 1
2022-01-08T16:58:13: %EASYPY-INFO:     Aborted    : 0
2022-01-08T16:58:13: %EASYPY-INFO:     Blocked    : 0
2022-01-08T16:58:13: %EASYPY-INFO:     Skipped    : 0
2022-01-08T16:58:13: %EASYPY-INFO:     Errored    : 0
2022-01-08T16:58:13: %EASYPY-INFO:
2022-01-08T16:58:13: %EASYPY-INFO:     TOTAL      : 4
2022-01-08T16:58:13: %EASYPY-INFO:
2022-01-08T16:58:13: %EASYPY-INFO: Success Rate   : 75.00 %
2022-01-08T16:58:13: %EASYPY-INFO:
2022-01-08T16:58:13: %EASYPY-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:13: %EASYPY-INFO: |                             Task Result Summary                              |
2022-01-08T16:58:13: %EASYPY-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:13: %EASYPY-INFO: Task-1: basic_example_script.common_setup                                 PASSED
2022-01-08T16:58:13: %EASYPY-INFO: Task-1: basic_example_script.tc_one                                       PASSED
2022-01-08T16:58:13: %EASYPY-INFO: Task-1: basic_example_script.tc_two                                       FAILED
2022-01-08T16:58:13: %EASYPY-INFO: Task-1: basic_example_script.common_cleanup                               PASSED
2022-01-08T16:58:13: %EASYPY-INFO:
2022-01-08T16:58:13: %EASYPY-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:13: %EASYPY-INFO: |                             Task Result Details                              |
2022-01-08T16:58:13: %EASYPY-INFO: +------------------------------------------------------------------------------+
2022-01-08T16:58:13: %EASYPY-INFO: Task-1: basic_example_script
2022-01-08T16:58:13: %EASYPY-INFO: |-- common_setup                                                          PASSED
2022-01-08T16:58:13: %EASYPY-INFO: |   |-- sample_subsection_1                                               PASSED
2022-01-08T16:58:13: %EASYPY-INFO: |   `-- sample_subsection_2                                               PASSED
2022-01-08T16:58:13: %EASYPY-INFO: |-- tc_one                                                                PASSED
2022-01-08T16:58:13: %EASYPY-INFO: |   |-- prepare_testcase                                                  PASSED
2022-01-08T16:58:13: %EASYPY-INFO: |   |-- simple_test_1                                                     PASSED
2022-01-08T16:58:13: %EASYPY-INFO: |   |-- simple_test_2                                                     PASSED
2022-01-08T16:58:13: %EASYPY-INFO: |   `-- clean_testcase                                                    PASSED
2022-01-08T16:58:13: %EASYPY-INFO: |-- tc_two                                                                FAILED
2022-01-08T16:58:13: %EASYPY-INFO: |   |-- simple_test_1                                                     FAILED
2022-01-08T16:58:13: %EASYPY-INFO: |   |-- simple_test_2                                                     PASSED
2022-01-08T16:58:13: %EASYPY-INFO: |   `-- clean_testcase                                                    PASSED
2022-01-08T16:58:13: %EASYPY-INFO: `-- common_cleanup                                                        PASSED
2022-01-08T16:58:13: %EASYPY-INFO:     `-- clean_everything                                                  PASSED
2022-01-08T16:58:13: %EASYPY-INFO: Sending report email...
2022-01-08T16:58:13: %EASYPY-INFO: Missing SMTP server configuration, or failed to reach/authenticate/send mail. Result notification email failed to send.
2022-01-08T16:58:13: %EASYPY-INFO: Done!

Pro Tip
-------
   Try the following command to view your logs:
       pyats logs view

iida@FCCLS0008993-00:~/pyats/examples/basic$
```


## pyats create project

テンプレートファイルが作られるので大変便利。

`pyats create project`

```bash
$ pyats create project
Project Name: test_pj
Testcase names [enter to finish]:
  1. testcase_one
  2. testcase_two
  3.
Will you be using testcase datafiles [Y/n]: y
Generating your project...


$ tree test_pj
test_pj
├── test_pj.py
├── test_pj_data.yaml
└── test_pj_job.py

0 directories, 3 files
```

```bash
'''
test_pj.py

'''
# see https://pubhub.devnetcloud.com/media/pyats/docs/aetest/index.html
# for documentation on pyATS test scripts

# optional author information
# (update below with your contact information if needed)
__author__ = 'Cisco Systems Inc.'
__copyright__ = 'Copyright (c) 2019, Cisco Systems Inc.'
__contact__ = ['pyats-support-ext@cisco.com']
__credits__ = ['list', 'of', 'credit']
__version__ = 1.0

import logging

from pyats import aetest

# create a logger for this module
logger = logging.getLogger(__name__)

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def connect(self, testbed):
        '''
        establishes connection to all your testbed devices.
        '''
        # make sure testbed is provided
        assert testbed, 'Testbed is not provided!'

        # connect to all testbed devices
        testbed.connect()


class testcase_one(aetest.Testcase):
    '''testcase_one

    < docstring description of this testcase >

    '''

    # testcase groups (uncomment to use)
    # groups = []

    @aetest.setup
    def setup(self):
        pass

    # you may have N tests within each testcase
    # as long as each bears a unique method name
    # this is just an example
    @aetest.test
    def test(self):
        pass

    @aetest.cleanup
    def cleanup(self):
        pass


class testcase_two(aetest.Testcase):
    '''testcase_two

    < docstring description of this testcase >

    '''

    # testcase groups (uncomment to use)
    # groups = []

    @aetest.setup
    def setup(self):
        pass

    # you may have N tests within each testcase
    # as long as each bears a unique method name
    # this is just an example
    @aetest.test
    def test(self):
        pass

    @aetest.cleanup
    def cleanup(self):
        pass



class CommonCleanup(aetest.CommonCleanup):
    '''CommonCleanup Section

    < common cleanup docstring >

    '''

    # uncomment to add new subsections
    # @aetest.subsection
    # def subsection_cleanup_one(self):
    #     pass

if __name__ == '__main__':
    # for stand-alone execution
    import argparse
    from pyats import topology

    parser = argparse.ArgumentParser(description = "standalone parser")
    parser.add_argument('--testbed', dest = 'testbed',
                        help = 'testbed YAML file',
                        type = topology.loader.load,
                        default = None)

    # do the parsing
    args = parser.parse_known_args()[0]

    aetest.main(testbed = args.testbed)

```


<br><br><br>

# Genie

pyatsの例の中にGenieも含まれている。

https://github.com/CiscoTestAutomation/examples/tree/master/libraries

https://developer.cisco.com/docs/genie-docs/
