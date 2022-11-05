# モックデバイスの作成

参照 https://pubhub.devnetcloud.com/media/unicon/docs/playback/index.html

モックデバイスは決まったコマンドに決まった応答を返すだけの装置。

実際の機器がなくてもデモができる。

show techを採取するのとあわせて、learn('all')を記録してモックデバイス化しておいたほうが役に立つかもしれない。


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
r1#?
% Invalid command '?'
Valid commands:
 config term
 config-transaction
 dir
 show access-lists
 show bgp all
 show bgp all cluster-ids
 show bgp all detail
 show bgp all neighbors
 show bgp all summary
 show bootvar
 show cdp neighbors detail
 show dot1x all count
 show dot1x all details
 show dot1x all statistics
 show dot1x all summary
 show env all
 show errdisable recovery
 show etherchannel summary
 show interfaces
 show interfaces accounting
 show inventory
 show inventory raw
 show ip arp
 show ip arp summary
 show ip bgp all dampening parameters
 show ip bgp template peer-policy
 show ip bgp template peer-session
 show ip eigrp neighbors detail
 show ip igmp groups detail
 show ip igmp interface
 show ip interface
 show ip mroute
 show ip mroute static
 show ip msdp peer
 show ip msdp sa-cache
 show ip multicast
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
 show ip pim bsr-router
 show ip pim interface
 show ip pim interface detail
 show ip pim interface df
 show ip pim neighbor
 show ip pim rp mapping
 show ip prefix-list detail
 show ip protocols
 show ip protocols | sec rip
 show ip rip database
 show ip route
 show ip static route
 show ip traffic
 show ipv6 eigrp neighbors detail
 show ipv6 interface
 show ipv6 mroute
 show ipv6 neighbors
 show ipv6 pim bsr candidate-rp
 show ipv6 pim bsr election
 show ipv6 pim interface
 show ipv6 pim neighbor detail
 show ipv6 prefix-list detail
 show ipv6 protocols | sec rip
 show ipv6 route
 show ipv6 static detail
 show issu rollback-timer
 show issu state detail
 show lacp counters
 show lacp neighbor
 show lacp sys-id
 show lisp service ethernet
 show lisp service ethernet summary
 show lisp service ipv4
 show lisp service ipv4 summary
 show lisp service ipv6
 show lisp service ipv6 summary
 show lldp
 show lldp entry *
 show lldp interface
 show lldp neighbors detail
 show lldp traffic
 show mac address-table
 show mac address-table aging-time
 show mac address-table learning
 show ntp associations
 show ntp config
 show ntp status
 show nve vni
 show pagp counters
 show pagp internal
 show pagp neighbor
 show platform
 show power inline
 show redundancy
 show route-map all
 show run | sec isis
 show running-config
 show running-config | section router ospf 1
 show spanning-tree
 show spanning-tree detail
 show spanning-tree mst configuration
 show spanning-tree mst detail
 show spanning-tree summary
 show standby all
 show standby delay
 show version
 show vlan
 show vrf
 show vrf detail
 show vrf detail | inc \(VRF
 term length 0
 term width 0
r1#
```

モックを対象に何かテストを行いたいときには、testbedにこのように記載する。

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
        command: mock_device_cli --os iosxe --mock_data_dir mock/r1 --state connect
        protocol: unknown
        arguments:
          init_exec_commands:
            - term length 0
            - term width 0
          init_config_commands: []
```
