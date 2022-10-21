# モックデバイスの作成

参照 https://pubhub.devnetcloud.com/media/unicon/docs/playback/index.html

モックデバイスは決まったコマンドに決まった応答を返すだけの装置。

実際の機器がなくてもデモができる。

show techを採取するのとあわせて、learn('all')を記録してモックデバイス化しておいたほうが約に立つかもしれない。


## 学習

```bash
./run
```

もしくは

```bash
pyats run job mock_job.py --testbed-file ../lab.yml --record recorded
```

recordedディレクトリにデバイスごとにファイルが残る。

```bash
recorded/
├── r1
├── r2
├── r3
└── r4
```

## モック用YAMLデータ作成

```bash
./create
```

もしくは

```bash
/usr/bin/env python -m unicon.playback.mock --recorded-data recorded/r1 --output r1/mock_device.yaml
/usr/bin/env python -m unicon.playback.mock --recorded-data recorded/r2 --output r2/mock_device.yaml
/usr/bin/env python -m unicon.playback.mock --recorded-data recorded/r3 --output r3/mock_device.yaml
/usr/bin/env python -m unicon.playback.mock --recorded-data recorded/r4 --output r4/mock_device.yaml
```

## モックデバイスに接続

```bash
mock_device_cli --os iosxe --state connect --mock_data_dir r1
```

なぜかホスト名の指定は効かず、プロンプトがswitchになってしまう。
