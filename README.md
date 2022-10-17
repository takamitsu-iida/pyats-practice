# pyats-practice

https://developer.cisco.com/pyats/ にあるIntroduction to pyATSが秀逸。

ブラウザの中に説明文とターミナルとエディタがあり、ブラウザのなかでコマンドを実行して結果を確認できる。

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

- devnet pyATS

https://developer.cisco.com/pyats/

- pyATS Documentation

https://pubhub.devnetcloud.com/media/pyats/docs/index.html

- aetest

https://pubhub.devnetcloud.com/media/pyats/docs/aetest/index.html

- job file

https://pubhub.devnetcloud.com/media/pyats/docs/easypy/jobfile.html

- genie

https://developer.cisco.com/docs/genie-docs/

- examples(github)

https://github.com/CiscoTestAutomation/examples

- solution example(github)

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

接続に関連した項目はtestbedに記述できるので、マニュアルに目を通しておくとよい。

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
```

記述したtestbedがおかしくないか検証できる。

```bash
pyats validate testbed [testbed yaml file]
```

:::note warn
> testbedファイルのなかでtopologyを記述した場合、PythonでのAPI利用に支障がでることがあります。
:::

```python
from genie.libs.conf.interface import Interface
gig1 = Interface(device=uut, name='GigabitEthernet1')
```

このように`Interface`オブジェクトを作成しようとすると例外がraiseします。

```text
File "src/pyats/topology/device.py", line 296, in pyats.topology.device.DeviceBase.add_interface
# pyats.topology.exceptions.DuplicateInterfaceError: Interface 'GigabitEthernet1' already exists on this device 'r1'.
```

明確に使い道が想定される場合をのぞいて、testbedファイルの中にtopologyセクションは記載しないほうが良さそうです。


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

## jobのログ置き場

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

jobのログ置き場を変えたいなら、この部分を変更すればよい。

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

拡張pingを指定するextd_pingの指定は真偽値ではなくyes/noなので注意。

応答がないと例外SubCommandFailureがraiseする。

```python
output = ping(addr="9.33.11.41")
output = ping(addr="10.2.1.1", extd_ping='yes')
```

動作例。

到達できるアドレスにpingするときは、

```python
output = uut.ping(addr="192.168.255.1")
pprint(output)
```

こういう出力になる。

```bash
('ping 192.168.255.1\r\n'
 'Type escape sequence to abort.\r\n'
 'Sending 5, 100-byte ICMP Echos to 192.168.255.1, timeout is 2 seconds:\r\n'
 '!!!!!\r\n'
 'Success rate is 100 percent (5/5), round-trip min/avg/max = 1/1/1 ms\r\n')
```

到達できないところにpingすると、SubCommandFailure例外がraiseしてスクリプトが停止してしまう。

```bash
r1#
Traceback (most recent call last):
  File "./ex60.diff.py", line 18, in <module>
    output = uut.ping(addr="192.168.255.100")
  File "src/unicon/bases/routers/services.py", line 270, in unicon.bases.routers.services.BaseService.__call__
  File "src/unicon/bases/routers/services.py", line 244, in unicon.bases.routers.services.BaseService.get_service_result
unicon.core.errors.SubCommandFailure: ('sub_command failure, patterns matched in the output:', ['Success rate is 0 percent'], 'service result', 'ping 192.168.255.100\r\nType escape sequence to abort.\r\nSending 5, 100-byte ICMP Echos to 192.168.255.100, timeout is 2 seconds:\r\n.....\r\nSuccess rate is 0 percent (0/5)\r\n')
```

ping()を使う場合は例外処理を忘れずにやること。

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

<br><br>

# telnet接続時の不具合対処

:::note warn
testbedへの接続プロトコルがtelnetの場合のみ、この対処が必要です。SSHであれば問題ありません。
:::

uniconはPython標準のtelnetlibを利用します。

telnetlibは一度に長大な応答がくることを想定していませんので、
show running-configやshow tech等を投げこむと、期待しているデータを受信できずにスクリプトが停止していまいます。

telnetlibの受信バッファを大きくすればよいだけなのですが、標準ライブラリを直接書き換えるわけにはいきません。
そこでtelnetlib.pyのコピーをローカルのlibフォルダに保存して、それを先に読み込ませるようにします。

下記をスクリプトの先頭に入れておくとよいでしょう。

```python
import sys
import os

#
# overwrite standard telnetlib
#
def here(path=''):
  return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

if not here('./lib') in sys.path:
  sys.path.insert(0, here('./lib'))

import telnetlib
if telnetlib.MODIFIED_BY:
    print('modified telnetlib is loaded.')
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


＜つづく＞

<br><br>

# 動作例

実際に動作させてみた例です。

<br><br>

## 構成図
