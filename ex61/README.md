# ex61

**このモックは動作しません**

ex61.diff.py用のモックデバイスです。

```bash
ex61/mock
└── r1
    └── mock_device.yaml
```

```bash
$ mock_device_cli --os iosxe --mock_data_dir ex61/mock/r1 --state connect
Trying mock_device ...
Connected to mock_device.
Escape character is '^]'.

r1#?
% Invalid command '?'
Valid commands:
 config term
 config-transaction
 show ip ospf
 show ip ospf database external
 show ip ospf database network
 show ip ospf database opaque-area
 show ip ospf database router
 show ip ospf database summary
 show ip ospf interface
 show ip ospf interface GigabitEthernet1
 show ip ospf interface GigabitEthernet2
 show ip ospf mpls ldp interface
 show ip ospf mpls traffic-eng link
 show ip ospf neighbor detail
 show ip ospf sham-links
 show ip ospf virtual-links
 show ip protocols
 show running-config | section router ospf 1
 show version
 term length 0
 term width 0
r1#
```

pyATSスクリプトは以下のコマンドで実行します。

```bash
$ ./ex61.diff.py --testbed ex61/lab.yml
```
