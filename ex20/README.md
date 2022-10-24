# ex20

ex20.parse.py用のモックデバイスです。

```bash
mock
└── r1
    └── mock_device.yaml
```

```bash
$ mock_device_cli --os iosxe --mock_data_dir mock/r1 --state connect
Trying mock_device ...
Connected to mock_device.
Escape character is '^]'.

r1#
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
$ ./ex20.parse.py --testbed ex20/lab.yml
```
