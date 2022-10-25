# ex12

ex12.execute.py用のモックデバイスです。

```bash
./mock
└── r1
    └── mock_device.yaml
```

```bash
$ mock_device_cli --os iosxe --mock_data_dir ex12/mock/r1 --state connect
Trying mock_device ...
Connected to mock_device.
Escape character is '^]'.

r1#?
% Invalid command '?'
Valid commands:
 config term
 config-transaction
 show running-config
 show version
 term length 0
 term width 0
```

pyATSスクリプトは以下のコマンドで実行します。

```bash
$ ./ex12.execute.py --testbed ex12/lab.yml
```
