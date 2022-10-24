# ex53

**このモックは動作しません**

ex53.configure.py用のモックデバイスです。

```bash
ex53/mock
└── r1
    └── mock_device.yaml
```

```bash
$ mock_device_cli --os iosxe --mock_data_dir ex53/mock/r1 --state connect
Trying mock_device ...
Connected to mock_device.
Escape character is '^]'.

r1#?
% Invalid command '?'
Valid commands:
 config term
 config-transaction
 show version
 term length 0
 term width 0
r1#
```

pyATSスクリプトは以下のコマンドで実行します。

```bash
$ ./ex53.configure.py --testbed ex53/lab.yml
```
