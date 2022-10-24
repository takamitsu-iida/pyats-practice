# ex42

ex42.learn_find.py用のモックデバイスです。

```bash
ex42/mock
├── sw1
│   └── mock_device.yaml
├── sw2
│   └── mock_device.yaml
├── sw3
│   └── mock_device.yaml
└── sw4
    └── mock_device.yaml
```

```bash
$ mock_device_cli --os iosxe --mock_data_dir ex42/mock/sw1 --state connect
Trying mock_device ...
Connected to mock_device.
Escape character is '^]'.

sw1#?
% Invalid command '?'
Valid commands:
 config term
 config-transaction
 show errdisable recovery
 show spanning-tree
 show spanning-tree detail
 show spanning-tree mst configuration
 show spanning-tree mst detail
 show spanning-tree summary
 show version
 term length 0
 term width 0
sw1#
```

pyATSスクリプトは以下のコマンドで実行します。

```bash
$ ./ex42.learn_find.py --testbed ex42/lab.yml
```
