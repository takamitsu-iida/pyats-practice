# ex13

ex13.execute.py用のモックデバイスです。

```bash
$ tree mock
mock
├── r1
│   └── mock_device.yaml
├── r2
│   └── mock_device.yaml
├── r3
│   └── mock_device.yaml
└── r4
    └── mock_device.yaml
```

r1からr4まで、4台のモックがあります。

```bash
$ mock_device_cli --os iosxe --mock_data_dir ex13/mock/r1 --state connect
Trying mock_device ...
Connected to mock_device.
Escape character is '^]'.

r1#
r1#
r1#?
% Invalid command '?'
Valid commands:
 config term
 config-transaction
 show cdp neighbors
 show ip ospf neighbor
 show ip route
 show version
 term length 0
 term width 0
r1#
```

このモックはex13.execute.pyで打ち込んだ4個のshowコマンドに対応しています。

pyATSスクリプトは以下のコマンドで実行します。

```bash
$ ./ex13.execute.py --testbed ex13/lab.yml
```
