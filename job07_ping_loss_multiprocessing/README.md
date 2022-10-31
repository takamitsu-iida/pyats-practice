# 連続pingの欠損数を計測する

> このスクリプトではOSPFネイバーの状態をみて経路が切り替わったことを確認してから連続pingを停止します。

インタフェースをダウンさせたときに連続pingが何個欠けるかを数えます。

<br>

### 必要な追加モジュール

表形式での表示にtabulateを使います。

```bash
pip install tabulate
```

<br>

### datafile

実行時にYAML形式で記述したdatafileを指定するとテストスクリプト内でそのデータを利用できます。
これを使うことで、制御対象装置の情報をスクリプトに埋め込まなくてすみます。
datafileを書き換えることでテストする対象を切り替えられるようになります。

> 参考
> https://pubhub.devnetcloud.com/media/pyats/docs/aetest/datafile.html


ここでは`datafile.yml`というファイルを使います。

```YAML
---

# スクリプトパラメータ
# これらは関数の引数として受け取ることができる
parameters:

  pinger:
    from: r1
    to: 192.168.255.4
    # repeat: 10
    repeat: 100000
    duration: 60

  targets:
    r2:
      interfaces:
        - GigabitEthernet1
        - GigabitEthernet2

    r4:
      interfaces:
        - GigabitEthernet1
```

pingerはpingを打ち込むデバイスです。

targetsはインタフェースを閉塞するデバイスです。

> 重要
> pingを打ち込むデバイスとインタフェースを閉塞するデバイスを同一にはできません。
> 複数のコネクションを張るようにする工夫が必要です。


<br>

### テストのシナリオ

r1からr4に向けての通信経路は２つあります。

- r1-r2-r4
- r1-r3-r4

![構成図](https://takamitsu-iida.github.io/pyats-practice/img/fig1.PNG "構成図")

現用系の経路はr1-r2-r4です。

現用系の通信が通るインタフェースを閉塞すると迂回路に通信を迂回するわけですが、
迂回するまでに欠損するpingの数をカウントします。

上記のdatafile.ymlの指定では、

```YAML
- STEP 1 r2を取り出す
    STEP 1.1
        STEP 1.1.1
            - pingを実行
            - GigabitEthernet1を**閉塞**
            - OSPFのネイバーが確立するまで待機
            - pingを停止
            - pingの欠けを数える

        STEP 1.1.2
            - pingを実行
            - GigabitEthernet1の**閉塞を解除**
            - OSPFのネイバーが確立するまで待機
            - pingを停止
            - pingの欠けを数える

    STEP 1.2
        STEP 1.2.1
            - pingを実行
            - GigabitEthernet2を**閉塞**
            - OSPFのネイバーが確立するまで待機
            - pingを停止
            - pingの欠けを数える

        STEP 1.2.2
            - pingを実行
            - GigabitEthernet2の**閉塞を解除**
            - OSPFのネイバーが確立するまで待機
            - pingを停止
            - pingの欠けを数える

- STEP 2 r4を取り出す
    STEP 2.1
        STEP 2.1.1
            - pingを実行
            - GigabitEthernet1を**閉塞**
            - OSPFのネイバーが確立するまで待機
            - pingを停止
            - pingの欠けを数える

        STEP 2.1.2
            - pingを実行
            - GigabitEthernet1の**閉塞を解除する**
            - OSPFのネイバーが確立するまで待機
            - pingを停止
            - pingの欠けを数える
```

というテストを実施します。

<br>

### 連続pingの起動と停止

連続pingは十分長い期間実施するようにrepeatを指定します。

ターゲット装置でインタフェースを閉塞（もしくは解除）した際に、OSPFネイバーの状態を確認して経路の切り替わりを確認したら、Ctrl-Shift-6と同じコードを送り込んで連続pingを強制停止します。
その後、下記のようなテキスト出力をパースして、何個欠けたかを集計します。

```bash
Success rate is 99 percent (32805/32806), round-trip min/avg/max = 1/1/46 ms
r1#
```

> 参照
> https://github.com/takamitsu-iida/pyats-practice/blob/main/ex92.ping.py


> jobを実行する際、連続pingの応答（!!!!）は画面に表示されませんが、ログには残っています。

<br>

### 同時実行の仕組み

multiprocessing.Process()を使って別プロセスで連続pingを走らせます。

同時にメインプロセスではターゲット装置のインタフェースを閉塞（もしくは解除）します。

pingプロセスには、Pipe()を使って連続pingの停止を指示します。

<br>

### 実行結果

このテストは127秒、約2分の時間を要しています。

もしこの試験を手作業でやっていたら、もっとかかると思います。

```bash
+------------------------------------------------------------------------------+
|                                Easypy Report                                 |
+------------------------------------------------------------------------------+
pyATS Instance   : /home/iida/git/pyats-practice/.venv
Python Version   : cpython-3.8.10 (64bit)
CLI Arguments    : /home/iida/git/pyats-practice/.venv/bin/pyats run job ping_loss_job.py --testbed-file ../lab.yml
User             : iida
Host Server      : FCCLS0008993-00
Host OS Version  : Ubuntu 20.04 focal (x86_64)

Job Information
    Name         : ping_loss_job
    Start time   : 2022-10-31 13:57:05.338028+09:00
    Stop time    : 2022-10-31 13:59:13.204917+09:00
    Elapsed time : 127.866889
    Archive      : /home/iida/.pyats/archive/22-Oct/ping_loss_job.2022Oct31_13:56:44.698732.zip

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
ping_loss: ping_loss_test.common_setup                                    PASSED
ping_loss: ping_loss_test.ping_loss_test_class                            PASSED
ping_loss: ping_loss_test.common_cleanup                                  PASSED

+------------------------------------------------------------------------------+
|                             Task Result Details                              |
+------------------------------------------------------------------------------+
ping_loss: ping_loss_test
|-- common_setup                                                          PASSED
|   |-- assert_datafile                                                   PASSED
|   `-- connect                                                           PASSED
|-- ping_loss_test_class                                                  PASSED
|   |-- test                                                              PASSED
|   |   |-- STEP 1: r2                                                    PASSED
|   |   |-- STEP 1.1: GigabitEthernet1                                    PASSED
|   |   |-- STEP 1.1.1: GigabitEthernet1 down                             PASSED
|   |   |-- STEP 1.1.2: GigabitEthernet1 up                               PASSED
|   |   |-- STEP 1.2: GigabitEthernet2                                    PASSED
|   |   |-- STEP 1.2.1: GigabitEthernet2 down                             PASSED
|   |   |-- STEP 1.2.2: GigabitEthernet2 up                               PASSED
|   |   |-- STEP 2: r4                                                    PASSED
|   |   |-- STEP 2.1: GigabitEthernet1                                    PASSED
|   |   |-- STEP 2.1.1: GigabitEthernet1 down                             PASSED
|   |   `-- STEP 2.1.2: GigabitEthernet1 up                               PASSED
|   `-- dump_result                                                       PASSED
`-- common_cleanup                                                        PASSED
    `-- disconnect                                                        PASSED
```

試験が終わるとresult.txtが生成されます。

```bash
2022年10月31日 13:40:56
--  ----------------  ----  -
r2  GigabitEthernet1  down  1
r2  GigabitEthernet1  up    0
r2  GigabitEthernet2  down  1
r2  GigabitEthernet2  up    0
r4  GigabitEthernet1  down  0
r4  GigabitEthernet1  up    0
--  ----------------  ----  -
```

pingの欠けは高々1個で冗長経路に切り替わっていることがわかります。

この試験では欠けたpingの数を集計するのが目的でしたので、異常な状態にならない限り試験はFAILEDになりません。
pingの欠けがしきい値を超えたらエラーにする、というロジックをいれてもいいかもしれません。
