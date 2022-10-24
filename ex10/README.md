# ex10

ex10.execute.py用のモックデバイスです。

```bash
$ mock_device_cli --os iosxe --mock_data_dir ex10/mock/r1 --state connect
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
r1#
```

上記の通り、このモックはshow versionしか応答できません。

pyATSスクリプトは以下のコマンドで実行します。

```bash
$ ./ex10.execute.py --testbed ex10/lab.yml
```
