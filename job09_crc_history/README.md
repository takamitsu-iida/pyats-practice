# CRCエラーを過去データから探索

インタフェースを学習してデータベース（tinydb）の中に格納します。

過去のデータを探索して、CRCエラーの増分がしきい値を超えたらエラーとします。

<br>

### 必要な追加モジュール

表形式での表示にtabulateを使います。

```bash
pip install tabulate
```

データベースに格納するためにtinydbを使います。

```bash
pip install tinydb
```

<br>

### datafile

テストに使うパラメータは`datafile.yml`に記述します。

> 参考
> https://pubhub.devnetcloud.com/media/pyats/docs/aetest/datafile.html


```YAML
---

# モジュールレベルのパラメータ
# これらはグローバル変数として利用できる
# module_var_a: some string value
# module_var_b: 99999

# スクリプトパラメータ
# これらは関数の引数として受け取ることができる
parameters:

  max_history: 3

  crc_threshold: 0

  targets:
    r1:
    r2:
    r3:
    r4:
    sw1:
    sw2:
    sw3:
    sw4:

```

<br>

### テストのシナリオ

datafile.ymlで指定されたtargetsに順番に接続してlearn('interface')します。

そのなかからin_crc_errorsを取り出して、その値がthresholdを超えたらテストはfailedします。

<br>

### 実行例

このようにまとめて表示されます。

ここではmax_historyを3に設定していますので、過去3回分の履歴を表示しています。

```bash
| device   | intf             |   2022-10-31 14:55:07 |   2022-10-31 14:59:01 |   2022-10-31 15:04:48 | test   |
|----------+------------------+-----------------------+-----------------------+-----------------------+--------|
| r1       | GigabitEthernet1 |                     0 |                     0 |                     0 | Passed |
| r1       | GigabitEthernet2 |                     0 |                     0 |                     0 | Passed |
| r1       | GigabitEthernet3 |                     0 |                     0 |                     0 | Passed |
| r1       | GigabitEthernet4 |                     0 |                     0 |                     0 | Passed |
| r1       | Loopback0        |                     0 |                     0 |                     0 | Passed |

| device   | intf             |   2022-10-31 14:55:07 |   2022-10-31 14:59:01 |   2022-10-31 15:04:48 | test   |
|----------+------------------+-----------------------+-----------------------+-----------------------+--------|
| r2       | GigabitEthernet1 |                     0 |                     0 |                     0 | Passed |
| r2       | GigabitEthernet2 |                     0 |                     0 |                     0 | Passed |
| r2       | GigabitEthernet3 |                     0 |                     0 |                     0 | Passed |
| r2       | GigabitEthernet4 |                     0 |                     0 |                     0 | Passed |
| r2       | Loopback0        |                     0 |                     0 |                     0 | Passed |

| device   | intf             |   2022-10-31 14:55:07 |   2022-10-31 14:59:01 |   2022-10-31 15:04:48 | test   |
|----------+------------------+-----------------------+-----------------------+-----------------------+--------|
| r3       | GigabitEthernet1 |                     0 |                     0 |                     0 | Passed |
| r3       | GigabitEthernet2 |                     0 |                     0 |                     0 | Passed |
| r3       | GigabitEthernet3 |                     0 |                     0 |                     0 | Passed |
| r3       | GigabitEthernet4 |                     0 |                     0 |                     0 | Passed |
| r3       | Loopback0        |                     0 |                     0 |                     0 | Passed |

| device   | intf             |   2022-10-31 14:55:07 |   2022-10-31 14:59:01 |   2022-10-31 15:04:48 | test   |
|----------+------------------+-----------------------+-----------------------+-----------------------+--------|
| r4       | GigabitEthernet1 |                     0 |                     0 |                     0 | Passed |
| r4       | GigabitEthernet2 |                     0 |                     0 |                     0 | Passed |
| r4       | GigabitEthernet3 |                     0 |                     0 |                     0 | Passed |
| r4       | GigabitEthernet4 |                     0 |                     0 |                     0 | Passed |
| r4       | Loopback0        |                     0 |                     0 |                     0 | Passed |

| device   | intf        |   2022-10-31 14:55:07 |   2022-10-31 14:59:01 |   2022-10-31 15:04:48 | test   |
|----------+-------------+-----------------------+-----------------------+-----------------------+--------|
| sw1      | Ethernet0/0 |                     0 |                     0 |                     0 | Passed |
| sw1      | Ethernet0/1 |                     0 |                     0 |                     0 | Passed |
| sw1      | Ethernet0/2 |                     0 |                     0 |                     0 | Passed |
| sw1      | Ethernet0/3 |                     0 |                     0 |                     0 | Passed |

| device   | intf        |   2022-10-31 14:55:07 |   2022-10-31 14:59:01 |   2022-10-31 15:04:48 | test   |
|----------+-------------+-----------------------+-----------------------+-----------------------+--------|
| sw2      | Ethernet0/0 |                     0 |                     0 |                     0 | Passed |
| sw2      | Ethernet0/1 |                     0 |                     0 |                     0 | Passed |
| sw2      | Ethernet0/2 |                     0 |                     0 |                     0 | Passed |
| sw2      | Ethernet0/3 |                     0 |                     0 |                     0 | Passed |

| device   | intf        |   2022-10-31 14:55:07 |   2022-10-31 14:59:01 |   2022-10-31 15:04:48 | test   |
|----------+-------------+-----------------------+-----------------------+-----------------------+--------|
| sw3      | Ethernet0/0 |                     0 |                     0 |                     0 | Passed |
| sw3      | Ethernet0/1 |                     0 |                     0 |                     0 | Passed |
| sw3      | Ethernet0/2 |                     0 |                     0 |                     0 | Passed |
| sw3      | Ethernet0/3 |                     0 |                     0 |                     0 | Passed |

| device   | intf        |   2022-10-31 14:55:07 |   2022-10-31 14:59:01 |   2022-10-31 15:04:48 | test   |
|----------+-------------+-----------------------+-----------------------+-----------------------+--------|
| sw4      | Ethernet0/0 |                     0 |                     0 |                     0 | Passed |
| sw4      | Ethernet0/1 |                     0 |                     0 |                     0 | Passed |
| sw4      | Ethernet0/2 |                     0 |                     0 |                     0 | Passed |
| sw4      | Ethernet0/3 |                     0 |                     0 |                     0 | Passed |
```

![実行例](https://takamitsu-iida.github.io/pyats-practice/job09_crc_history/img/fig1.PNG "実行例")