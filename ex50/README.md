# ex50

**このモックデバイスはコンフィグを投げ込みますが、反映はされません**

ex50.configure.py用のモックデバイスです。

```bash
ex50/mock
└── r1
    └── mock_device.yaml
```

```bash
$ mock_device_cli --os iosxe --mock_data_dir ex50/mock/r1 --state connect
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
```

pyATSスクリプトは以下のコマンドで実行します。

```bash
$ ./ex50.configure.py --testbed ex50/lab.yml
```
