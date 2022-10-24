# ex22

ex22.parse_html.py用のモックデバイスです。

```bash
ex22/mock
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
$ mock_device_cli --os iosxe --mock_data_dir ex22/mock/sw1 --state connect
Trying mock_device ...
Connected to mock_device.
Escape character is '^]'.

sw1#help
% Invalid command 'help'
Valid commands:
 config term
 config-transaction
 show interfaces status
 show version
 term length 0
 term width 0
sw1#
```

pyATSスクリプトは以下のコマンドで実行します。

```bash
$ ./ex22.parse_html.py --testbed ex22/lab.yml
```
