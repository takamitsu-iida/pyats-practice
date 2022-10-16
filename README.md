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

- aetest

https://pubhub.devnetcloud.com/media/pyats/docs/aetest/index.html

- job file

https://pubhub.devnetcloud.com/media/pyats/docs/easypy/jobfile.html

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

<br><br>

## job

jobファイルを作成して実行すると、結果をブラウザで確認できる。

```bash
pyats run job job.py --testbed-file lab.yml
```

ログの確認。HTTPサーバが立ち上がってブラウザが起動する。

```bash
pyats logs view
```

<br><br>

## ログ置き場

`~/.pyats/` に保管される。

知らぬ間に膨れ上がっているかもしれないので要注意。

<br><br>

## pyatsの設定

`pyats.conf`ファイルを用意する。INI形式で記載。

ファイルはこの順番で読み込まれる。同じ設定項目はあとに読まれた方で上書きされる。

- /etc/pyats.conf
- $VIRTUAL_ENV/pyats.conf
- $HOME/.pyats/pyats.conf
- PYATS_CONFIGURATION=path/to/pyats.conf
- cli argument --pyats-configuration can be used to specify a configuration file

ログ置き場を変えたいなら、この部分の設定。

```INI
# configuration related to easypy execution
[easypy]

# archive storage directory
# (use this to specify where you want pyATS archive zip file to be saved)
# runinfo.archive = <path>

# runinfo directory
# (specifies the location where the runtime dir is created during execution)
# runinfo.directory = <path to runinfo folder>
```

<br><br>

# unicon

接続ライブラリ。

スタックや冗長化したルートプロセッサに対応している。

プレイバック機能があり、接続したログを使ってモックを作れる。

<br><br>

### デフォルトのプロンプト

Cisco以外の機器で挙動がおかしいときは、正規表現を見直す。

https://pubhub.devnetcloud.com/media/unicon/docs/user_guide/services/service_dialogs.html


### send

送信する。改行コード'\r'が必要。

```python
rtr.send("show clock\r")
rtr.send("show clock\r", target='standby')
```

### sendline

送信する。改行コード不要。

```python
rtr.sendline("show clock")
```

### expect

応答を待ち合わせ。待ち合わせる文字列は正規表現が使える。

応答バッファのデフォルトは8Kバイト。show techのように長大なレスポンスだと恐らくバッファが足りない。

タイムアウトのデフォルトは10秒。タイムアウト時には例外がでる。

```python
rtr.sendline("show interfaces")
rtr.expect([r'^pat1', r'pat2'], timeout=10)
```

### receive

応答バッファを検索する。真偽値を返す。見つからなくても例外は発報されない。

`r'nopattern^`を渡すと、`timeout`になるまでバッファを探し続ける。

`receive_buffer()`でバッファを取得する。

```python
rtr.transmit("show interfaces")
rtr.receive(r'^pat1', timeout=10, target='standby')
output = rtr.receive_buffer()
```

### log_user

接続中のコマンド応答を画面に表示するかどうか。

```python
rtr.log_user(enable=True)
rtr.log_user(enable=False)
```

### log_file

ログのファイルハンドラ変更する。引数を渡さなければ現在設定されているファイル名を返す。

```python
rtr.log_file(filename='/some/path/uut.log')
rtr.log_file() # Returns current FileHandler filename
```

### enable disable

管理者モードを変更する。

引数に管理者モードになるためのコマンドが渡せるので、`enable`以外のコマンドで管理者モードに入るような装置でも使える。

```python
rtr.enable()
rtr.enable(command='enable 7')
rtr.disable()
```

### ping

その装置からpingを打つ。オプションがたくさんある。

拡張pingを指定するextd_pingの指定は真偽値ではなくyes/noになっている。

応答がないと例外SubCommandFailureがraiseする。

```python
output = ping(addr="9.33.11.41")
output = ping(addr="10.2.1.1", extd_ping='yes')
```

### copy

IOSでのcopyコマンドに相当。設定の保存に使う。

成功した場合はcopyコマンドの応答、失敗した場合は例外がraiseする。

```python
out = rtr.copy(source='running-conf', dest='startup-config')

out = rtr.copy(source = 'tftp:',
                dest = 'bootflash:',
                source_file  = 'copy-test',
                dest_file = 'copy-test',
                server='10.105.33.158')
```

### reload

実際に試したことはない。

装置を再起動する。

再起動に使うコマンドを指定できる。

再起動で接続は切れるが、再接続してくれる。
プロンプトの処理がうまくできないケースは`prompt_recover`をTrueにする。

再起動時の応答が欲しいときには、`return_output`をTrueにする。

```python
rtr.reload()

# If reload command is other than 'reload'
rtr.reload(reload_command="reload location all", timeout=400)

# using prompt_recovery option
rtr.reload(prompt_recovery=True)

# using return_output
result, output = rtr.reload(return_output=True)
```

### bash_console guestshell

これら機能を搭載した機種ならコマンドの打ち込みに使える。

```python
with device.bash_console() as bash:
    output1 = bash.execute('ls')
    output2 = bash.execute('pwd')

with device.guestshell(enable_guestshell=True, retries=30) as gs:
    output = gs.execute("ifconfig")
```

### get_config

running-configを取得する。

```python
rtr.get_config()
rtr.get_config(target='standby')
```


<br><br>

# プラグイン開発

新しい装置に対応させるにはプラグインの開発が必要。

https://pubhub.devnetcloud.com/media/unicon/docs/developer_guide/plugins.html

実装済みプラグインのソースコードを見たほうが早い。
ほとんどの処理はgenericで対応できるので、装置固有の差分になるところだけ実装すれば良さそう。

https://github.com/CiscoTestAutomation/unicon.plugins/tree/master/src/unicon/plugins

プラグインの例があるので、それを拡張していくのが早道。

https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example
