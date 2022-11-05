# ヘルスチェック

pyatsではジョブを実行した後、装置のヘルスチェックを実行できます。

参照 https://pubhub.devnetcloud.com/media/genie-docs/docs/health/index.html


項目は、

- cpu CPU負荷率が90%でfail
- memory 使用率90%でfail
- logging トレースバックが出ていたらfail
- core コアファイルが生成されていたらfail

```bash
pyats run job <job file> --testbed-file /path/to/testbed.yaml --health-checks cpu memory logging core
```

任意のジョブにヘルスチェックを付与できます。

<br>

### 実行例

何もしない、空のジョブを実行してみた結果です。

```bash
+------------------------------------------------------------------------------+
|                                Easypy Report                                 |
+------------------------------------------------------------------------------+
pyATS Instance   : /home/iida/git/pyats-practice/.venv
Python Version   : cpython-3.8.10 (64bit)
CLI Arguments    : /home/iida/git/pyats-practice/.venv/bin/pyats run job health_check_job.py --testbed-file ../lab.yml --health-checks cpu memory logging core
User             : iida
Host Server      : FCCLS0008993-00
Host OS Version  : Ubuntu 20.04 focal (x86_64)

Job Information
    Name         : health_check_job
    Start time   : 2022-10-31 18:56:04.328090+09:00
    Stop time    : 2022-10-31 18:56:53.643037+09:00
    Elapsed time : 49.314947
    Archive      : /home/iida/.pyats/archive/22-Oct/health_check_job.2022Oct31_18:55:55.934119.zip

Total Tasks    : 1

Overall Stats
    Passed     : 2
    Passx      : 0
    Failed     : 1
    Aborted    : 0
    Blocked    : 0
    Skipped    : 0
    Errored    : 0

    TOTAL      : 3

Success Rate   : 66.67 %

+------------------------------------------------------------------------------+
|                             Task Result Summary                              |
+------------------------------------------------------------------------------+
Health_Check: health_check_test.common_setup                              PASSED
Health_Check: health_check_test.collect_all                               FAILED
Health_Check: health_check_test.common_cleanup                            PASSED

+------------------------------------------------------------------------------+
|                             Task Result Details                              |
+------------------------------------------------------------------------------+
Health_Check: health_check_test
|-- common_setup                                                          PASSED
|   `-- connect                                                           PASSED
|-- collect_all                                                           FAILED
|   |-- dummy                                                             PASSED
|   |   |-- STEP 1: Learn all about r1                                    PASSED
|   |   |-- STEP 2: Learn all about r2                                    PASSED
|   |   |-- STEP 3: Learn all about r3                                    PASSED
|   |   `-- STEP 4: Learn all about r4                                    PASSED
|   |-- PostContextProcessor-3                                            PASSED
|   |-- PostContextProcessor-4                                            PASSED
|   |-- PostContextProcessor-5                                            FAILED
|   `-- PostContextProcessor-6                                            PASSED
`-- common_cleanup                                                        PASSED
    `-- disconnect                                                        PASSED
```

![実行結果](https://takamitsu-iida.github.io/pyats-practice/job00_health_check/img/fig1.PNG "実行結果")

テストが一つFAILEDになっています。

ログをみるとこのようになっています。

```bash
0: 2022-10-31T18:56:40:  >>>> Begin child log /home/iida/.pyats/runinfo/health_check_job.2022Oct31_18:55:55.934119/TaskLog.Health_Check:pid-16789
1: 2022-10-31T18:56:40:  +..............................................................................+
2: 2022-10-31T18:56:40:  :             Starting STEP 1: Starting action api on device 'r4'              :
3: 2022-10-31T18:56:40:  +..............................................................................+
4: 2022-10-31T18:56:40:  +..............................................................................+
5: 2022-10-31T18:56:40:  :           Starting STEP 1.1: Calling API 'health_logging' on 'r4'            :
6: 2022-10-31T18:56:40:  +..............................................................................+
7: 2022-10-31T18:56:40:  +++ r4 with via 'console': executing command 'show logging | include traceback|Traceback|TRACEBACK' +++
show logging | include traceback|Traceback|TRACEBACK
*Oct 15 05:23:26.282: %EVENTLIB-3-CPUHOG: R0/0: fman_fp_image: undefined: 1875ms, Traceback=1#d44f3a43c524a06dabe3dc9d590930c1   c:7FF6BB2BE000+37370 :564E44CAD000+576320 evlib:7FF6C4C6C000+9145 evlib:7FF6C4C6C000+9A9C orchestrator_lib:7FF6BD898000+CE31 orchestrator_lib:7FF6BD898000+CDB4 luajit:7FF6BBC26000+7C696 luajit:7FF6BBC26000+35C44 luajit:7FF6BBC26000+BFF9 luajit:7FF6BBC26000+7A6F7 luajit:7FF6BBC26000+1CD5A
*Oct 15 05:23:26.288: %EVENTLIB-3-CPUHOG: R0/0: fman_fp_image: undefined: 2021ms, Traceback=1#d44f3a43c524a06dabe3dc9d590930c1   c:7FF6BB2BE000+37370 :564E44CAD000+576320 evlib:7FF6C4C6C000+9145 evlib:7FF6C4C6C000+9A9C orchestrator_lib:7FF6BD898000+CE31 orchestrator_lib:7FF6BD898000+CDB4 luajit:7FF6BBC26000+7C696 luajit:7FF6BBC26000+35C44 luajit:7FF6BBC26000+BFF9 luajit:7FF6BBC26000+7A6F7 luajit:7FF6BBC26000+1CD5A
r4#
10: 2022-10-31T18:56:40:  +..............................................................................+
11: 2022-10-31T18:56:40:  :    Starting STEP 1.1.1: Verify that 'value_operator('num_of_logs', '==',     :
12: 2022-10-31T18:56:40:  :                        0)' is included in the output                         :
13: 2022-10-31T18:56:40:  +..............................................................................+
14: 2022-10-31T18:56:40:  Failed reason: 'include' criteria is not satisfied.
15: 2022-10-31T18:56:40:  The result of STEP 1.1.1: Verify that 'value_operator('num_of_logs', '==', 0)' is included in the output is => FAILED
16: 2022-10-31T18:56:40:  The result of STEP 1.1: Calling API 'health_logging' on 'r4' is => FAILED
17: 2022-10-31T18:56:40:  The result of STEP 1: Starting action api on device 'r4' is => FAILED
18: 2022-10-31T18:56:40:  <<<< End child log /home/iida/.pyats/runinfo/health_check_job.2022Oct31_18:55:55.934119/TaskLog.Health_Check:pid-16789
440: 2022-10-31T18:56:41:  Applied filter: get_values('logs') to the action api output
```

r4に対するshow loggingの出力でFAILEDになっています。
これはshow loggingのなかにトレースバックが出力されているためです。

このように、装置そのものの健全性は自分でスクリプトを書くまでもなく、任意のジョブを実行するついでに確認することができます。
