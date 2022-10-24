# ex30

ex30.learn.py用のモックデバイスです。

```bash
ex30/mock
└── r1
    └── mock_device.yaml
```

```bash
$ mock_device_cli --os iosxe --mock_data_dir ex30/mock/r1 --state connect
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
$ ./ex30.learn.py --testbed ex30/lab.yml
```
