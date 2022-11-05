# インタフェースを学習してCRCエラーを抽出する

learn('interface')の情報からin_crc_errorsだけを取り出して表にします。

後々のために学習した情報はファイルに残します。

<br>

### 必要な追加モジュール

表形式での表示にtabulateを使います。

```bash
pip install tabulate
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

全て0なのでおもしろくありませんね。
0を超える、つまり1以上だと、そのインタフェースのテストはfailになります。
failになるインタフェースが多すぎる場合は、しきい値thresholdを指定して条件を緩和するとよいでしょう。

```bash
| Device   | Interface        |   IN_CRC_ERRORS | Test   |
|----------+------------------+-----------------+--------|
| r1       | GigabitEthernet1 |               0 | Passed |
| r1       | GigabitEthernet2 |               0 | Passed |
| r1       | GigabitEthernet3 |               0 | Passed |
| r1       | GigabitEthernet4 |               0 | Passed |
| r1       | Loopback0        |               0 | Passed |
| r2       | GigabitEthernet1 |               0 | Passed |
| r2       | GigabitEthernet2 |               0 | Passed |
| r2       | GigabitEthernet3 |               0 | Passed |
| r2       | GigabitEthernet4 |               0 | Passed |
| r2       | Loopback0        |               0 | Passed |
| r3       | GigabitEthernet1 |               0 | Passed |
| r3       | GigabitEthernet2 |               0 | Passed |
| r3       | GigabitEthernet3 |               0 | Passed |
| r3       | GigabitEthernet4 |               0 | Passed |
| r3       | Loopback0        |               0 | Passed |
| r4       | GigabitEthernet1 |               0 | Passed |
| r4       | GigabitEthernet2 |               0 | Passed |
| r4       | GigabitEthernet3 |               0 | Passed |
| r4       | GigabitEthernet4 |               0 | Passed |
| r4       | Loopback0        |               0 | Passed |
| sw1      | Ethernet0/0      |               0 | Passed |
| sw1      | Ethernet0/1      |               0 | Passed |
| sw1      | Ethernet0/2      |               0 | Passed |
| sw1      | Ethernet0/3      |               0 | Passed |
| sw2      | Ethernet0/0      |               0 | Passed |
| sw2      | Ethernet0/1      |               0 | Passed |
| sw2      | Ethernet0/2      |               0 | Passed |
| sw2      | Ethernet0/3      |               0 | Passed |
| sw3      | Ethernet0/0      |               0 | Passed |
| sw3      | Ethernet0/1      |               0 | Passed |
| sw3      | Ethernet0/2      |               0 | Passed |
| sw3      | Ethernet0/3      |               0 | Passed |
| sw4      | Ethernet0/0      |               0 | Passed |
| sw4      | Ethernet0/1      |               0 | Passed |
| sw4      | Ethernet0/2      |               0 | Passed |
| sw4      | Ethernet0/3      |               0 | Passed |
```

全ての装置の全てのインタフェースをテスト対象にしていますので、全てが緑（PASS）になっていることを視覚的にみれるのはありがたいですね。

![実行結果](https://takamitsu-iida.github.io/pyats-practice/job08_crc/img/fig1.PNG "実行結果")

<br>

### ファイル保存

learn('interface')の結果はpklディレクトリにzipでアーカイブして保存されます。

```bash
$ tree pkl/
pkl/
├── 20221029_202019.zip
├── 20221029_202833.zip
├── 20221029_204450.zip
├── 20221029_215834.zip
├── 20221029_220018.zip
├── 20221029_220312.zip
├── 20221029_222819.zip
├── 20221029_234641.zip
└── 20221029_234907.zip
```
