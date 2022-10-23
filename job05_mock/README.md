# モックデバイスの作成

参照 https://pubhub.devnetcloud.com/media/unicon/docs/playback/index.html

モックデバイスは決まったコマンドに決まった応答を返すだけの装置。

実際の機器がなくてもデモができる。

show techを採取するのとあわせて、learn('all')を記録してモックデバイス化しておいたほうが約に立つかもしれない。


## 学習

```bash
./run
```

もしくは

```bash
pyats run job mock_job.py --testbed-file ../lab.yml --record record
```

この処理はlearn('all')しているので長い時間かかる。

recordディレクトリにデバイスごとにファイルが残る。

```bash
$ tree record
record/
├── r1
├── r2
├── r3
└── r4
```

この場合のサイズは100KB弱だが、ルーティングテーブルが大きければ当然ファイルサイズも大きくなる。

```bash
$ ls -l record
total 352
-rw-r--r-- 1 iida 89165 Oct 23 23:41 r1
-rw-r--r-- 1 iida 87212 Oct 23 23:41 r2
-rw-r--r-- 1 iida 87290 Oct 23 23:41 r3
-rw-r--r-- 1 iida 87285 Oct 23 23:41 r4
```

## モック用YAMLデータ作成

複数台あると面倒なので、シェルスクリプトを走らせる。

```bash
./create
```

## モックデバイスに接続

`--os`指定は必須。`--mock_data_dir`でどのモック装置に繋ぐか指定する。

```bash
mock_device_cli --os iosxe --state connect --mock_data_dir mock/r1
```

実行例。

```bash
$ mock_device_cli --os iosxe --state connect --mock_data_dir mock/r1
Trying mock_device ...
Connected to mock_device.
Escape character is '^]'.

r1#
r1#
r1#
r1#show version
Cisco IOS XE Software, Version 17.03.04a
Cisco IOS Software [Amsterdam], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 17.3.4a, RELEASE SOFTWARE (fc3)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2021 by Cisco Systems, Inc.
Compiled Tue 20-Jul-21 04:59 by mcpre


Cisco IOS-XE software, Copyright (c) 2005-2021 by cisco Systems, Inc.
All rights reserved.  Certain components of Cisco IOS-XE software are
licensed under the GNU General Public License ("GPL") Version 2.0.  The
software code licensed under GPL Version 2.0 is free software that comes
with ABSOLUTELY NO WARRANTY.  You can redistribute and/or modify such
GPL code under the terms of GPL Version 2.0.  For more details, see the
documentation or "License Notice" file accompanying the IOS-XE software,
or the applicable URL provided on the flyer accompanying the IOS-XE
software.


ROM: IOS-XE ROMMON

r1 uptime is 1 week, 2 days, 5 hours, 15 minutes
Uptime for this control processor is 1 week, 2 days, 5 hours, 17 minutes
System returned to ROM by reload
System image file is "bootflash:packages.conf"
Last reload reason: reload



This product contains cryptographic features and is subject to United
States and local country laws governing import, export, transfer and
use. Delivery of Cisco cryptographic products does not imply
third-party authority to import, export, distribute or use encryption.
Importers, exporters, distributors and users are responsible for
compliance with U.S. and local country laws. By using this product you
agree to comply with applicable laws and regulations. If you are unable
to comply with U.S. and local laws, return this product immediately.

A summary of U.S. laws governing Cisco cryptographic products may be found at:
http://www.cisco.com/wwl/export/crypto/tool/stqrg.html

If you require further assistance please contact us by sending email to
export@cisco.com.

License Level: ax
License Type: N/A(Smart License Enabled)
Next reload license Level: ax

The current throughput level is 1000 kbps


Smart Licensing Status: UNREGISTERED/No Licenses in Use

cisco CSR1000V (VXE) processor (revision VXE) with 1105173K/3075K bytes of memory.
Processor board ID 934T7HPFN7R
Router operating mode: Autonomous
4 Gigabit Ethernet interfaces
32768K bytes of non-volatile configuration memory.
3012228K bytes of physical memory.
6188032K bytes of virtual hard disk at bootflash:.

Configuration register is 0x2102
r1#
```

testbedはこのように記載する。

init_exec_commandsとinit_config_commandsはモックを作成したときと同じ指定にしておかないとエラーになる。

```yaml
devices:

  r1:
    alias: 'uut'

    os: iosxe
    platform: CSR1000v
    type: router

    connections:
      defaults:
        class: 'unicon.Unicon'
      console:
      a:
        command: mock_device_cli --os iosxe --mock_data_dir mock/r1 --state connect
        protocol: unknown
        arguments:
          init_exec_commands:
            - term length 0
            - term width 0
          init_config_commands: []
```