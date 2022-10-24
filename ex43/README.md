# ex43

ex43.learn_poll.py用のモックデバイスです。

```bash
ex43/mock
└── r1
    └── mock_device.yaml
```

```bash
$ mock_device_cli --os iosxe --mock_data_dir ex43/mock/r1 --state connect
Trying mock_device ...
Connected to mock_device.
Escape character is '^]'.

r1#?
% Invalid command '?'
Valid commands:
 config term
 config-transaction
 show interfaces
 show interfaces accounting
 show ip interface
 show ipv6 interface
 show version
 show vrf
 term length 0
 term width 0
r1#
```

pyATSスクリプトは以下のコマンドで実行します。

```bash
$ ./ex43.learn_poll.py --testbed ex43/lab.yml
```
