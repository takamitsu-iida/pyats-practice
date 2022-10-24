# ex62

**このモックは動作しません**

ex62.diff.py用のモックデバイスです。

```bash
ex62/mock
└── r1
    └── mock_device.yaml
```

```bash
$ mock_device_cli --os iosxe --mock_data_dir ex62/mock/r1 --state connect
Trying mock_device ...
Connected to mock_device.
Escape character is '^]'.

r1#?
% Invalid command '?'
Valid commands:
 config term
 config-transaction
 show ip route
 show ipv6 route
 show version
 show vrf detail
 term length 0
 term width 0
r1#
```

pyATSスクリプトは以下のコマンドで実行します。

```bash
$ ./ex62.diff.py --testbed ex62/lab.yml
```
