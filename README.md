# pyats-practice

https://developer.cisco.com/pyats/ にあるIntroduction to pyATSが秀逸。
ブラウザの中に説明とターミナルとエディタがあり、ページ内で実行して結果を確認できる

- learnを実行してログを収集

```bash
pyats learn interface ospf platform --testbed-file working-tb.yaml --output working_snapshot
```

- 再びlearnを実行してログを収集

```bash
pyats learn interface ospf platform --testbed-file broken-tb.yaml --output broken_snapshot
```

- 収集したログのdiffを取る

```bash
pyats diff working_snapshot broken_snapshot --output diff_snapshot
```

上記を実行するだけでも使う価値があると思わせる内容になっている。

<br><br>

## ドキュメント

https://pubhub.devnetcloud.com/media/pyats/docs/index.html

https://developer.cisco.com/pyats/

https://developer.cisco.com/docs/pyats/

https://developer.cisco.com/docs/genie-docs/

https://github.com/CiscoTestAutomation/examples

https://github.com/CiscoTestAutomation/solutions_examples


<br><br>

## install

venvでpython環境を作る。

```bash
$ python3 -m venv .venv
```

direnvを設定してディレクトリに入ったら自動でactivateする。

```bash
echo 'source .venv/bin/activate' > .envrc
echo 'unset PS1' >> .envrc
direnv allow
```

pyatsに関連したモジュールを全てインストールする。

```bash
pip install pyats[full]
pip install rest.connector
pip install yang.connector
```

<br><br>

## testbed

インベントリをtestbedと呼ぶ。testbedはYAML形式で記述する。

装置に関する情報だけでなく、どのように接続しているか、も記述する。

接続に関連した項目はtestbedに記述できるので、マニュアルに目を通した方が結果的に近道。

https://pubhub.devnetcloud.com/media/unicon/docs/user_guide/connection.html

記述したtestbedがおかしくないか検証できる。

```bash
pyats validate testbed [testbed yaml file]
```

実行例。

```bash
$ pyats validate testbed lab.yml
Loading testbed file: lab.yml
--------------------------------------------------------------------------------

Testbed Name:
    iida-pyats on eve-ng

Testbed Devices:
.
|-- fumidai [linux/linux]
|   `-- pnet0
|-- r1 [iosxe/CSR1000v]
|   |-- GigabitEthernet1 ----------> r1-r2
|   |-- GigabitEthernet2 ----------> r1-r3
|   `-- Loopback0 ----------> r1_Loopback0
|-- r2 [iosxe/CSR1000v]
|   |-- GigabitEthernet1 ----------> r1-r2
|   |-- GigabitEthernet2 ----------> r2-r4
|   `-- Loopback0 ----------> r2_Loopback0
|-- r3 [iosxe/CSR1000v]
|   |-- GigabitEthernet1 ----------> r3-r4
|   |-- GigabitEthernet2 ----------> r1-r3
|   `-- Loopback0 ----------> r3_Loopback0
|-- r4 [iosxe/CSR1000v]
|   |-- GigabitEthernet1 ----------> r3-r4
|   |-- GigabitEthernet2 ----------> r2-r4
|   `-- Loopback0 ----------> r4_Loopback0
|-- sw1 [ios/IOL]
|   |-- Ethernet0/0 ----------> sw1-sw2
|   |-- Ethernet0/1 ----------> sw1-sw3
|   `-- Ethernet0/2 ----------> sw2-sw4
|-- sw2 [ios/IOL]
|   |-- Ethernet0/0 ----------> sw1-sw2
|   |-- Ethernet0/1 ----------> sw2-sw4
|   `-- Ethernet0/2 ----------> sw2-sw3
|-- sw3 [ios/IOL]
|   |-- Ethernet0/0 ----------> sw3-sw4
|   |-- Ethernet0/1 ----------> sw1-sw3
|   `-- Ethernet0/2 ----------> sw2-sw3
`-- sw4 [ios/IOL]
    |-- Ethernet0/0 ----------> sw3-sw4
    |-- Ethernet0/1 ----------> sw2-sw4
    `-- Ethernet0/2 ----------> sw1-sw4
```

利用しているラボのtestbedはこの通り。

```yml
---

#
# testbed file for lab
#

#
# NOTE
# 1) The device name must match the hostname of the device, otherwise, the connection will hang.
# 2) At least one device need to have the alias ‘uut’ in the testbed yaml file.
#

# to validate the testbed file
# pyats validate testbed [file]

testbed:
  name: iida-pyats on eve-ng

  # common credentials
  credentials:
    default:
      username: ''
      password: ''
    enable:
      password: ''

devices:

  # this host does NOT exist now
  fumidai:
    os: linux
    type: linux
    credentials:
      # ~/.ssh/configは読まないのでユーザ名はここで指定する
      default:
        username: bastion
    connections:
      vty:
        protocol: ssh
        ip: 10.38.220.46


  # must be hostname, same as prompt
  r1:
    alias: 'uut'

    # 機種に対応したプラグインを読み込む優先順位、osは必須でその他は任意
    #  chassis_type > os > platform > model

    # os
    # ios, iosxe, iosxr, nxos, junos
    # https://pubhub.devnetcloud.com/media/unicon/docs/user_guide/supported_platforms.html#
    os: iosxe

    # 任意
    platform: CSR1000v
    type: iosxe

    # スタックしている場合はchassis_typeを指定
    # chassis_type: stack

    connections:
      console:
        protocol: telnet
        ip: feve.nsc.css.fujitsu.com
        port: 38905
        timeout: 10
        arguments:
          # osがiosxeの場合、接続と同時に以下のコマンドが投入される
          #  - term length 0
          #  - term width 0
          #  - show version
          # init_exec_commandsに空っぽのリストを渡せば何も実行されなくなる
          # init_exec_commands: []

          # osがiosxeの場合、接続と同時に以下の設定変更を行う
          # - no logging console
          # - line console 0
          # - exec-timeout 0
          # - end
          # init_config_commandsに空のリストを渡せば設定変更を抑止できる
          init_config_commands: []

      # SSHで踏み台を経由する場合
      vty:
        proxy: fumidai
        protocol: ssh -oKexAlgorithms=+diffie-hellman-group14-sha1,diffie-hellman-group-exchange-sha1
        ip: 192.168.0.11
        port: -p 22


  r2:
    os: iosxe
    platform: CSR1000v
    type: iosxe
    connections:
      console:
        protocol: telnet
        ip: feve.nsc.css.fujitsu.com
        port: 42503
        arguments:
          init_exec_commands:
            - term len 0
            - term wid 0
          init_config_commands: []

  r3:
    os: iosxe
    platform: CSR1000v
    type: iosxe
    connections:
      console:
        protocol: telnet
        ip: feve.nsc.css.fujitsu.com
        port: 48927
        arguments:
          init_exec_commands:
            - term len 0
            - term wid 0
          init_config_commands: []

  r4:
    os: iosxe
    platform: CSR1000v
    type: iosxe
    connections:
      console:
        protocol: telnet
        ip: feve.nsc.css.fujitsu.com
        port: 41539
        arguments:
          init_exec_commands:
            - term len 0
            - term wid 0
          init_config_commands: []

topology:

  fumidai:
    interfaces:
      pnet0:
        type: ethernet

  r1:
    interfaces:
      GigabitEthernet1:
        ipv4: 192.168.12.1/24
        link: r1-r2
        type: ethernet
      GigabitEthernet2:
        ipv4: 192.168.13.1/24
        link: r1-r3
        type: ethernet
      Loopback0:
        ipv4: 192.168.255.1/32
        link: r1_Loopback0
        type: loopback

  r2:
    interfaces:
      GigabitEthernet1:
        ipv4: 192.168.12.2/24
        link: r1-r2
        type: ethernet
      GigabitEthernet2:
        ipv4: 192.168.24.2/24
        link: r2-r4
        type: ethernet
      Loopback0:
        ipv4: 192.168.255.2/32
        link: r2_Loopback0
        type: loopback

  r3:
    interfaces:
      GigabitEthernet1:
        ipv4: 192.168.34.3/24
        link: r3-r4
        type: ethernet
      GigabitEthernet2:
        ipv4: 192.168.13.3/24
        link: r1-r3
        type: ethernet
      Loopback0:
        ipv4: 192.168.255.3/32
        link: r3_Loopback0
        type: loopback

  r4:
    interfaces:
      GigabitEthernet1:
        ipv4: 192.168.34.4/24
        link: r3-r4
        type: ethernet
      GigabitEthernet2:
        ipv4: 192.168.24.4/24
        link: r2-r4
        type: ethernet
      Loopback0:
        ipv4: 192.168.255.4/32
        link: r4_Loopback0
        type: loopback
```

<br><br>

## job

```bash
pyats run job job.py --testbed-file lab-testbed.yml --html-logs
```
