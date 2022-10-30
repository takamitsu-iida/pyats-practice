# 連続pingの欠損数を計測する

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
- r2を取り出す
    - GigabitEthernet1を閉塞させる
        - pingの欠けを数える
        - GigabitEthernet1の閉塞を解除する
        - OSPFのネイバーが確立するまで待機
    - GigabitEthernet2を閉塞させる
        - pingの欠けを数える
        - GigabitEthernet2の閉塞を解除する
        - OSPFのネイバーが確立するまで待機

- r4を取り出す
    - GigabitEthernet1を閉塞させる
        - pingの欠けを数える
        - GigabitEthernet1の閉塞を解除する
        - OSPFのネイバーが確立するまで待機
```

というテストを実施します。

<br>

### 連続pingの起動と停止

連続pingはいつ完了するかわかりません。

一定期間（上記の例では60秒）経過したらCtrl-Shift-6と同じコードを送り込んで連続pingを強制停止します。
その後、下記のようなテキスト出力をパースして、何個欠けたかを集計します。

```bash
Success rate is 99 percent (32805/32806), round-trip min/avg/max = 1/1/46 ms
r1#
```

> 参照
> https://github.com/takamitsu-iida/pyats-practice/blob/main/ex91.ping.py

<br>

### インタフェースの閉塞

pyATSのpcall()を使って、pingを実行する関数と、インタフェースを閉塞する関数、２つをパラレルに実行します。

ただし、連続pingの実行を開始して1秒後にインタフェースが閉塞されるように1秒のスリープを入れています。

<br>

### 実行結果

このテストは382秒、つまり6分以上の時間を要しています。
長い時間かかっていますが、もしこれを手作業でやっていたら、もっとかかると思います。

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
    Start time   : 2022-10-28 16:42:17.822398+09:00
    Stop time    : 2022-10-28 16:48:39.830329+09:00
    Elapsed time : 382.007931
    Archive      : /home/iida/.pyats/archive/22-Oct/ping_loss_job.2022Oct28_16:42:08.211185.zip

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
|   `-- test                                                              PASSED
|       |-- STEP 1: r2                                                    PASSED
|       |-- STEP 1.1: GigabitEthernet1                                    PASSED
|       |-- STEP 1.1.1: GigabitEthernet1 down                             PASSED
|       |-- STEP 1.1.2: GigabitEthernet1 up                               PASSED
|       |-- STEP 1.2: GigabitEthernet2                                    PASSED
|       |-- STEP 1.2.1: GigabitEthernet2 down                             PASSED
|       |-- STEP 1.2.2: GigabitEthernet2 up                               PASSED
|       |-- STEP 2: r4                                                    PASSED
|       |-- STEP 2.1: GigabitEthernet1                                    PASSED
|       |-- STEP 2.1.1: GigabitEthernet1 down                             PASSED
|       `-- STEP 2.1.2: GigabitEthernet1 up                               PASSED
`-- common_cleanup                                                        PASSED
    |-- disconnect                                                        PASSED
    `-- dump_result                                                       PASSED
```

試験が終わるとresult.txtが生成されます。

```bash
2022年10月28日 18:03:26
--  ----------------  ----  -
r2  GigabitEthernet1  down  1
r2  GigabitEthernet1  up    1
r2  GigabitEthernet2  down  1
r2  GigabitEthernet2  up    1
r4  GigabitEthernet1  down  0
r4  GigabitEthernet1  up    0
--  ----------------  ----  -
```

pingの欠けは高々1個で冗長経路に切り替わっていることがわかります。

インタフェースの閉塞を解除したときも欠けていますが、行きと帰りの両方のルーティング情報が収束する必要があるので、このくらいは許容範囲でしょう。

この試験では欠けたpingの数を集計するのが目的でしたので、異常な状態にならない限り試験はFAILEDになりません。
pingの欠けが10個を超えたらエラーにする、というロジックをいれてもいいかもしれません。
