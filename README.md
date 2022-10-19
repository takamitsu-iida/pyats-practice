# pyats-practice

DevNetのサイトにあるIntroduction to pyATSが秀逸です。

ブラウザの中に説明文とターミナルとエディタがあり、コマンドを実行して動作結果を確認できます。
ドキュメントを読む前にまずこれを試してみるべきです。

https://developer.cisco.com/pyats/


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

上記を実行するだけでもpyATSを使う価値があると思わせる内容になっています。

<br><br>

## ドキュメント

DevNetのサイトからたどれます。

- DevNet pyATS https://developer.cisco.com/pyats/

- pyATS Documentation https://pubhub.devnetcloud.com/media/pyats/docs/index.html

- Genie https://developer.cisco.com/docs/genie-docs/

- Genieでparseできるコマンド検索 https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/parsers

- Genieでlearnできる機能検索 https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/models

- aetest https://pubhub.devnetcloud.com/media/pyats/docs/aetest/index.html

- job file https://pubhub.devnetcloud.com/media/pyats/docs/easypy/jobfile.html

- examples(github) https://github.com/CiscoTestAutomation/examples

- solution example(github) https://github.com/CiscoTestAutomation/solutions_examples

<br><br>

## deck

- 説明会向けに作成 https://takamitsu-iida.github.io/decks/pyats-practice/

<br><br>

## install

venvでPython環境を作ります。

```bash
$ python3 -m venv .venv
```

direnvと組み合わせるのがオススメです。ディレクトリに入ったら自動でactivateしてくれます。

```bash
echo 'source .venv/bin/activate' > .envrc
echo 'unset PS1' >> .envrc
direnv allow
```

Python環境が整ったら、pipでpyatsに関連したモジュールを全てインストールします。

```bash
pip install pyats[full]
pip install rest.connector
pip install yang.connector
```

パスワードの類を暗号化して記述するためのモジュールをインストールします。

```bash
pip install cryptography
```

<br><br>

## testbed

インベントリのことをテストベッド(testbed)と呼びます。
testbedはYAML形式で記述します。

接続に関連したパラメータはtestbedにも記述できるので、マニュアルに目を通しておくとよいと思います。

https://pubhub.devnetcloud.com/media/unicon/docs/user_guide/connection.html

利用しているラボのtestbedは概ねこのような感じにしています。

eve-ng上の仮想環境ですのでルータ・スイッチにパスワードは設定されていません。
その場合は設定を省略するのではなく、空文字列のパスワードを指定します。

proxyという項目を指定することで、踏み台を経由することができます。
SSHに組み込まれたプロキシ機能ではなく、踏み台になる装置に実際に接続して、改めてコマンドを発行して乗り込んでいくスタイルです。
何段でも経由できますし、最初はSSH、次はtelnet、のようにプロトコルが変わっても大丈夫です。

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
        ip: feve
        port: 38905
        #
        # dev.connect()に渡される引数よりもtestbedで指定した値の方が優先される
        #
        settings:
          GRACEFUL_DISCONNECT_WAIT_SEC: 1     # default 10
          POST_DISCONNECT_WAIT_SEC: 1         # default 10
          EXEC_TIMEOUT: 20                    # default 60
          CONFIG_TIMEOUT: 20                  # default 60
        arguments:
          connection_timeout: 10
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
        settings:
          GRACEFUL_DISCONNECT_WAIT_SEC: 1
          POST_DISCONNECT_WAIT_SEC: 1

  r2:
    os: iosxe
    platform: CSR1000v
    type: iosxe
    connections:
      console:
        protocol: telnet
        ip: feve
        port: 42503
        settings:
          GRACEFUL_DISCONNECT_WAIT_SEC: 1
          POST_DISCONNECT_WAIT_SEC: 1
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
        ip: feve
        port: 48927
        settings:
          GRACEFUL_DISCONNECT_WAIT_SEC: 1
          POST_DISCONNECT_WAIT_SEC: 1
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
        ip: feve
        port: 41539
        settings:
          GRACEFUL_DISCONNECT_WAIT_SEC: 1
          POST_DISCONNECT_WAIT_SEC: 1
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

> testbedファイルのなかでtopologyを記述した場合、PythonでのAPI利用に支障がでることがあります。
> 明確に使い道が想定される場合をのぞいて、testbedファイルの中にtopologyセクションは記載しないほうが良さそうです。

<br><br>

## 秘匿化

testbedファイルにパスワードをそのまま書くのはよくないので暗号化します。

参照 https://pubhub.devnetcloud.com/media/pyats/docs/utilities/secret_strings.html

```bash
pip install cryptography
```

`~/.pyats/pyats.conf`を作成して設定を記述します。

```INI
[secrets]
string.representer = pyats.utils.secret_strings.FernetSecretStringRepresenter
```

```bash
chmod 600 ~/.pyats/pyats.conf
```

```bash
pyats secret keygen
```

生成されたキーをコピーして、`~/.pyats/pyats.conf`の[secrets]セクションに追記します。

```INI
[secrets]
string.representer = pyats.utils.secret_strings.FernetSecretStringRepresenter
string.key = ....
```

文字列を暗号化します。

```bash
pyats secret encode
```

testbedファイルでは生成された文字列を使ってこのように書きます。

```
password: "%ENC{ ... }"
```

<br><br>

## job

テストを実行する形式の一つがjobです。

jobファイルを作成して実行すると、実行結果をブラウザで確認できます。

```bash
pyats run job job.py --testbed-file lab.yml
```

ログを確認するには、次のコマンドを実行します。HTTPサーバが立ち上がり、自動でブラウザが開きます。

```bash
pyats logs view
```

<br><br>

## jobのログ置き場

過去に実行したジョブはすべて記録として残っています。この記録は `~/.pyats/` に保管されています。

アーカイブされたログもここに保管されていますので、知らぬ間に膨れ上がっているかもしれません。
ときどき確認して要らないものは削除しましょう。

<br><br>

## pyatsの設定

pyATSの環境設定を変更するには `pyats.conf` ファイルを用意します。INI形式で記載します。

ファイルはこの順番で読み込まれれ、同じ設定項目はあとに読まれた方で上書きされます。

- /etc/pyats.conf
- $VIRTUAL_ENV/pyats.conf
- $HOME/.pyats/pyats.conf
- PYATS_CONFIGURATION=path/to/pyats.conf
- cli argument --pyats-configuration can be used to specify a configuration file

jobのログ置き場はデフォルトで~/.pyatsですが、この部分を変更すれば違う場所に保存できます。

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

pyATSが利用している接続ライブラリです。便利です。

プラグイン形式で多くのサービスが組み込まれていて、スタックや冗長化したルートプロセッサにも対応しています。

<br><br>

### デフォルトのプロンプト処理

Cisco以外の機器で挙動がおかしいときや、
新しい装置のプラグインを作成するときはここに記載の正規表現を確認するとよいでしょう。

https://pubhub.devnetcloud.com/media/unicon/docs/user_guide/services/service_dialogs.html

<br><br>

### disconnect

コネクションを切断するにはdisconnect()を呼びます。

接続・切断を短期間に行うことで生じる問題を避けるためにdisconnect()はデフォルトで約10秒待機します。
このデフォルト値は長過ぎるので、単一コネクションであれば短くした方が良いでしょう。

複数のコネクションをfor文で回しながらdisconnect()するのであれば、この設定は慎重に判断したほうがいいでしょう。

参照 https://pubhub.devnetcloud.com/media/unicon/docs/user_guide/connection.html

```python
dev.settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0
dev.settings.POST_DISCONNECT_WAIT_SEC = 0
dev.disconnect()
```

testbedファイルに設定しておくこともできますが、優先度はtestbedの方が高いので、プログラムのなかで動作を変えることはできなくなります。

```yml
  r1:
    os: iosxe
    platform: CSR1000v
    type: iosxe
    connections:
      console:
        protocol: telnet
        ip: feve
        port: 38905
        timeout: 20
        settings:
          GRACEFUL_DISCONNECT_WAIT_SEC: 1
          POST_DISCONNECT_WAIT_SEC: 1
```

### execute

コマンドの打ち込みであればsend()やsendline()ではなくexecute()を使います。

デフォルトのタイムアウトは60秒です。それを超えるとunicon.core.errors.TimeoutErrorがraiseします。
show techのように長大な応答が来ると予期されるときはtimeoutを指定したほうがよいでしょう。

config termのようにモード変更が発生するコマンドを投げ込むとunicon.core.errors.StateMachineErrorが出てスクリプトが停止します。

```python
dev.execute('config term')
```

モードの変更が伴うコマンドを投入するときはallow_state_changeをTrueにします。

```python
dev.execute('config term', allow_state_change=True)
```

実行時にYes/Noの確認が生じる場合はDialogを指定します。

```python
from unicon.eal.dialogs import Statement, Dialog
dialog = Dialog([
    Statement(pattern=r'.*Do you wish to proceed anyway\? \(y/n\)\s*\[n\]',
                        action='sendline(y)',
                        loop_continue=True,
                        continue_timer=False)
])
dev.execute("write erase", reply=dialog)
```

参照 https://pubhub.devnetcloud.com/media/unicon/docs/user_guide/services/generic_services.html#execute

### send

文字列を送信します。改行コード'\r'が必要です。

```python
dev.send("show clock\r")
dev.send("show clock\r", target='standby')
```

### sendline

文字列を送信します。改行コードは不要です。

```python
dev.sendline("show clock")
```

### expect

正規表現で応答を待ち合わせます。

応答バッファのデフォルトは8Kバイトです。show techのように長大なレスポンスだとバッファはが足りないかもしれません。

タイムアウトのデフォルトは10秒です。タイムアウトすると例外がraiseします。

```python
dev.sendline("show interfaces")
dev.expect([r'^pat1', r'pat2'], timeout=10)
```

### receive

受信バッファを検索して真偽値を返します。見つからなくても例外はraiseされません。

`r'nopattern^`を渡すと、`timeout`になるまでバッファを探し続けます。

応答のテキストは`receive_buffer()`で取得します。

```python
dev.transmit("show interfaces")
dev.receive(r'^pat1', timeout=10, target='standby')
output = dev.receive_buffer()
```

### log_user

接続中のコマンド応答を画面に表示するかどうかを指定します。

```python
dev.log_user(enable=True)
dev.log_user(enable=False)
```

### log_file

ログのファイルハンドラ変更します。引数を渡さなければ現在設定されているファイル名が返ります。

```python
dev.log_file(filename='/some/path/uut.log')
dev.log_file() # Returns current FileHandler filename
```

### enable disable

特権モードを変更する。

引数に管理者モードになるためのコマンドを渡せます。

```python
dev.enable()
dev.enable(command='enable 7')
dev.disable()
```

### ping

その装置からpingを打ちます。

Cisco機器のpingコマンドですのでオプションがたくさんあります。

拡張pingを指定するextd_pingは真偽値ではなくyes/noで指定します。

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

到達できないところにpingすると、unicon.core.errors.SubCommandFailureがraiseしてスクリプトが停止してしまいます。

```bash
r1#
Traceback (most recent call last):
  File "./ex60.diff.py", line 18, in <module>
    output = uut.ping(addr="192.168.255.100")
  File "src/unicon/bases/routers/services.py", line 270, in unicon.bases.routers.services.BaseService.__call__
  File "src/unicon/bases/routers/services.py", line 244, in unicon.bases.routers.services.BaseService.get_service_result
unicon.core.errors.SubCommandFailure: ('sub_command failure, patterns matched in the output:', ['Success rate is 0 percent'], 'service result', 'ping 192.168.255.100\r\nType escape sequence to abort.\r\nSending 5, 100-byte ICMP Echos to 192.168.255.100, timeout is 2 seconds:\r\n.....\r\nSuccess rate is 0 percent (0/5)\r\n')
```

ping()を使う場合は例外処理が必須です。

### copy

IOSでのcopyコマンドに相当します。乗り込んだ装置での設定の保存に使います。

成功した場合はcopyコマンドの応答、失敗した場合は例外がraiseします。

```python
out = dev.copy(source='running-conf', dest='startup-config')

out = dev.copy(source = 'tftp:',
                dest = 'bootflash:',
                source_file  = 'copy-test',
                dest_file = 'copy-test',
                server='10.105.33.158')
```

### reload

（実際に試したことはありません）

装置を再起動します。再起動に使うコマンドを細かく指定できます。

再起動で接続は切れるが、再接続してくれるようです。

再起動したことによりプロンプトの処理がうまく継続できないケースは`prompt_recover`をTrueにします。

再起動時の応答が欲しいときには`return_output`をTrueにします。

```python
dev.reload()

# If reload command is other than 'reload'
dev.reload(reload_command="reload location all", timeout=400)

# using prompt_recovery option
dev.reload(prompt_recovery=True)

# using return_output
result, output = dev.reload(return_output=True)
```

### bash_console guestshell

これら機能を搭載した機種でコマンドの打ち込みに使います。

bash

```python
with device.bash_console() as bash:
    output1 = bash.execute('ls')
    output2 = bash.execute('pwd')
```

guestshell

```python
with device.guestshell(enable_guestshell=True, retries=30) as gs:
    output = gs.execute("ifconfig")
```

<br><br>

# telnet接続時の不具合対処

> testbedへの接続プロトコルがtelnetの場合のみ、この対処が必要です。

uniconはPython標準のtelnetlibを利用します。

telnetlibは一度に長大な応答がくることを想定していませんので、
show running-configやshow tech等を投げこむと、期待しているデータを受信できずにスクリプトが停止することがあります。

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

新しい装置に対応させるにはプラグインの開発が必要です。

https://pubhub.devnetcloud.com/media/unicon/docs/developer_guide/plugins.html

実装済みプラグインのソースコードを見たほうが早いです。
ほとんどの処理はgenericで対応済みなので、装置固有の差分になるところだけ実装すれば良さそうです。

https://github.com/CiscoTestAutomation/unicon.plugins/tree/master/src/unicon/plugins

プラグインの例があるので、それを拡張していくのが早道。

https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example


＜つづく＞

<br><br>

# 動作例

Pythonスクリプトで動作させた例をいくつか。

<br><br>

## 構成図

![構成図](https://takamitsu-iida.github.io/pyats-practice/img/fig1.PNG "構成図")

<br>

### ex10.execute.py

<p>
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/ex10.execute.py" target="_blank">source</a>]　
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/output/ex10.log" target="_blank">log</a>]
</p>

接続後にコマンドを打ち込む例です。

```python
output = uut.execute('show version')

from pprint import pprint
pprint(output)
```

実行結果。

```bash
r1#
('Cisco IOS XE Software, Version 17.03.04a\r\n'
 'Cisco IOS Software [Amsterdam], Virtual XE Software '
 '(X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 17.3.4a, RELEASE SOFTWARE '
 '(fc3)\r\n'
 'Technical Support: http://www.cisco.com/techsupport\r\n'
 'Copyright (c) 1986-2021 by Cisco Systems, Inc.\r\n'
 'Compiled Tue 20-Jul-21 04:59 by mcpre\r\n'
 '\r\n'
 '\r\n'
```

<br><br>

### ex11.execute.py

<p>
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/ex11.execute.py" target="_blank">source</a>]　
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/output/ex11.log" target="_blank">log</a>]
</p>

ex10.execute.pyと同一ですが、各処理に例外のハンドリングを加えたものです。

<br><br>

### ex12.execute.py

<p>
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/ex12.execute.py" target="_blank">source</a>]　
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/output/ex12.log" target="_blank">log</a>]
</p>

show running-configを打ち込むだけですが、
telnetで接続しているときに長大な出力を受け取ると不具合がでることがありますので、その対処を加えた例です。

<br><br>

### ex13.execute.py

<p>
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/ex13.execute.py" target="_blank">source</a>]　
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/output/ex13.log" target="_blank">log</a>]
</p>

ログを採取する例です。

テストベッド内の全てのルータに接続して、複数のコマンドを打ち込んで、装置ごとにその結果をファイルに保存する例です。

```python
for name, dev in testbed.devices.items():
    if dev.platform == 'CSR1000v':

        log_path = os.path.join(log_dir, f'ex13_{name}.log')
        with open(log_path, 'w') as f:
            # connect
            try:
                dev.connect(via='console')
            except (TimeoutError, ConnectionError, SubCommandFailure) as e:
                f.write(str(e))
                continue

            # execute
            for cmd in command_list:
                try:
                    f.write('\n===\n')
                    f.write(cmd)
                    f.write('\n===\n')
                    f.write(dev.execute(cmd))
                    f.write('\n\n')
                except SubCommandFailure:
                    f.write(f'`{cmd}` invalid. Skipping.')

            # disconnect
            if dev.is_connected():
                dev.disconnect()
```

これを実行するとlogディレクトリにファイルが保存されます。

```bash
log
├── ex13_r1.log
├── ex13_r2.log
├── ex13_r3.log
└── ex13_r4.log
```

<br><br>

### ex20.parse.py

<p>
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/ex20.parse.py" target="_blank">source</a>]　
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/output/ex20.log" target="_blank">log</a>]
</p>

show versionを打ち込んで、その応答を辞書型に変換する例です。

Genieで対応済みのコマンドはここで検索できます。

https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/parsers


実行例。

```bash
r1#
{'version': {'chassis': 'CSR1000V',
             'chassis_sn': '934T7HPFN7R',
             'compiled_by': 'mcpre',
             'compiled_date': 'Tue 20-Jul-21 04:59',
             'copyright_years': '1986-2021',
             'curr_config_register': '0x2102',
             'disks': {'bootflash:.': {'disk_size': '6188032',
                                       'type_of_disk': 'virtual hard disk'}},
             'hostname': 'r1',
```

<br><br>

### ex30.learn.py

<p>
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/ex30.learn.py" target="_blank">source</a>]　
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/output/ex30.log" target="_blank">log</a>]
</p>

抽象的な機能名を指定して包括的に学習させることもできます。

サポートしている機能名はここから探します。

https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/models

たとえば`routing` を指定して実行するとルーティングテーブルを取得できます。
画面に出力すると横に長くて見づらいですが、階層の深い辞書型になっていることがわかります。

```bash
{'vrf': {'default': {'address_family': {'ipv4': {'routes': {'192.168.12.0/24': {'active': True,
                                                                                'next_hop': {'outgoing_interface': {'GigabitEthernet1': {'outgoing_interface': 'GigabitEthernet1'}}},
                                                                                'route': '192.168.12.0/24',
                                                                                'source_protocol': 'connected',
                                                                                'source_protocol_codes': 'C'},
                                                            '192.168.12.1/32': {'active': True,
                                                                                'next_hop': {'outgoing_interface': {'GigabitEthernet1': {'outgoing_interface': 'GigabitEthernet1'}}},
                                                                                'route': '192.168.12.1/32',
                                                                                'source_protocol': 'local',
                                                                                'source_protocol_codes': 'L'},
```

<br><br>

### ex31.learn.py

<p>
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/ex31.learn.py" target="_blank">source</a>]　
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/output/ex31.log" target="_blank">log</a>]
</p>

インタフェース情報を学習させる例です。

実行例。

```bash
learnt interfaces
dict_keys(['GigabitEthernet4', 'GigabitEthernet3', 'GigabitEthernet2', 'GigabitEthernet1', 'Loopback0'])
{'accounting': {'arp': {'chars_in': 1020,
                        'chars_out': 1080,
                        'pkts_in': 17,
                        'pkts_out': 18},
                'cdp': {'chars_in': 1667889,
                        'chars_out': 1644294,
                        'pkts_in': 3943,
                        'pkts_out': 3943},
                'ip': {'chars_in': 2648174,
                       'chars_out': 2650232,
                       'pkts_in': 23233,
                       'pkts_out': 23234},
                'other': {'chars_in': 1683291,
                          'chars_out': 1645374,
                          'pkts_in': 3994,
                          'pkts_out': 3961}},
 'auto_negotiate': True,
 'bandwidth': 1000000,
 'counters': {'in_broadcast_pkts': 0,
              'in_crc_errors': 0,
              'in_errors': 0,
              'in_mac_pause_frames': 0,
              'in_multicast_pkts': 0,
              'in_octets': 8128590,
              'in_pkts': 51162,
              'last_clear': 'never',
              'out_broadcast_pkts': 0,
              'out_errors': 0,
              'out_mac_pause_frames': 0,
              'out_multicast_pkts': 0,
              'out_octets': 7943936,
              'out_pkts': 50153,
              'rate': {'in_rate': 0,
                       'in_rate_pkts': 0,
                       'load_interval': 300,
                       'out_rate': 0,
                       'out_rate_pkts': 0}},
 'delay': 10,
 'description': 'to r2',
 'duplex_mode': 'full',
 'enabled': True,
 'encapsulation': {'encapsulation': 'arpa'},
 'flow_control': {'receive': False, 'send': False},
 'ipv4': {'192.168.12.1/24': {'ip': '192.168.12.1',
                              'prefix_length': '24',
                              'secondary': False}},
 'mac_address': '5002.0001.0000',
 'mtu': 9000,
 'oper_status': 'up',
 'phys_address': '5002.0001.0000',
 'port_channel': {'port_channel_member': False},
 'port_speed': '1000mbps',
 'switchport_enable': False,
 'type': 'CSR vNIC'}
```

<br><br>

### ex32.learn.py

<p>
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/ex32.learn.py" target="_blank">source</a>]　
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/output/ex32.log" target="_blank">log</a>]
</p>

`stp`を指定して学習させる例です。

実行例。

```bash
sw4
{'global': {'bpdu_filter': False,
            'bpdu_guard': False,
            'bpduguard_timeout_recovery': 300,
            'etherchannel_misconfig_guard': True,
            'loop_guard': False},
 'mstp': {'default': {'domain': 'default', 'name': '', 'revision': 0}},
 'pvst': {'default': {'forwarding_delay': 15,
                      'hello_time': 2,
                      'max_age': 20,
                      'pvst_id': 'default',
                      'vlans': {1: {'bridge_address': 'aabb.cc00.0600',
                                    'bridge_priority': 32768,
                                    'configured_bridge_priority': 32768,
                                    'designated_root_address': 'aabb.cc00.0300',
                                    'designated_root_priority': 32769,
                                    'forwarding_delay': 15,
                                    'hello_time': 2,
                                    'hold_time': 1,
                                    'interfaces': {'Ethernet0/0': {'cost': 100,
                                                                   'counters': {'bpdu_received': 92713,
                                                                                'bpdu_sent': 1},
                                                                   'designated_bridge_address': 'aabb.cc00.0500',
                                                                   'designated_bridge_priority': 32769,
                                                                   'designated_cost': 100,
                                                                   'designated_port_num': 1,
                                                                   'designated_port_priority': 128,
                                                                   'designated_root_address': 'aabb.cc00.0300',
                                                                   'designated_root_priority': 32769,
                                                                   'forward_transitions': 0,
                                                                   'name': 'Ethernet0/0',
                                                                   'port_num': 1,
                                                                   'port_priority': 128,
                                                                   'port_state': 'blocking',
                                                                   'role': 'alternate'},
                                                   'Ethernet0/1': {'cost': 100,
                                                                   'counters': {'bpdu_received': 92722,
                                                                                'bpdu_sent': 0},
                                                                   'designated_bridge_address': 'aabb.cc00.0400',
                                                                   'designated_bridge_priority': 32769,
                                                                   'designated_cost': 100,
                                                                   'designated_port_num': 2,
                                                                   'designated_port_priority': 128,
                                                                   'designated_root_address': 'aabb.cc00.0300',
                                                                   'designated_root_priority': 32769,
                                                                   'forward_transitions': 1,
                                                                   'name': 'Ethernet0/1',
                                                                   'port_num': 2,
                                                                   'port_priority': 128,
                                                                   'port_state': 'blocking',
                                                                   'role': 'alternate'},
                                                   'Ethernet0/2': {'cost': 100,
                                                                   'counters': {'bpdu_received': 92674,
                                                                                'bpdu_sent': 1},
                                                                   'designated_bridge_address': 'aabb.cc00.0300',
                                                                   'designated_bridge_priority': 32769,
                                                                   'designated_cost': 0,
                                                                   'designated_port_num': 3,
                                                                   'designated_port_priority': 128,
                                                                   'designated_root_address': 'aabb.cc00.0300',
                                                                   'designated_root_priority': 32769,
                                                                   'forward_transitions': 1,
                                                                   'name': 'Ethernet0/2',
                                                                   'port_num': 3,
                                                                   'port_priority': 128,
                                                                   'port_state': 'forwarding',
                                                                   'role': 'root'}},
                                    'max_age': 20,
                                    'root_cost': 100,
                                    'root_port': 3,
                                    'sys_id_ext': 1,
                                    'time_since_topology_change': '2d03h',
                                    'topology_changes': 2,
                                    'vlan_id': 1}}}}}
```

<br><br>

### ex33.learn.py

<p>
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/ex33.learn.py" target="_blank">source</a>]　
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/output/ex33.log" target="_blank">log</a>]
</p>

`config`を指定して学習させる例です。

深い意味合いまで解釈しているわけではありません。
ブロック化されている設定を、親となる行をキーとした辞書型に格納しているだけです。

実行例。

```bash
r1#
{'Building configuration...': {},
 'Current configuration : 6519 bytes': {},
 'boot-end-marker': {},
 'boot-start-marker': {},
 'call-home': {'contact-email-addr sch-smart-licensing@cisco.com': {},
               'profile "CiscoTAC-1"': {'active': {},
                                        'destination transport-method http': {}}},
 'cdp run': {},
 'control-plane': {},

```

<br><br>

### ex40.parse_find.py

<p>
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/ex40.parse_find.py" target="_blank">source</a>]　
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/output/ex40.log" target="_blank">log</a>]
</p>

`show interfaces`コマンドをパースして辞書型のオブジェクトを取得したあと、欲しい情報を探しに行く例です。

単純に辞書型の中をループさせて、`out_pkts`が0になっているインタフェースを見つけることもできますが、ソースコードは読みづらいです。

深い辞書型を探索するときには、Rとfindをインポートすると簡単です。

https://pubhub.devnetcloud.com/media/pyats/docs/utilities/helper_functions.html


```python
req = R(['(.*)', 'counters', 'out_pkts', 0])
found = find(parsed, req, filter_=False)
pprint(found)
```

Rに渡しているリストは辞書型の階層のキーです。
最後の要素に値を指定するとで、その値に一致するものを取得します。
上記の例ではこのような階層のエントリを探しています。

```python
{
    '(.*)': {
        'counters': {
            'out_pkts': 0
        }
    }
}
```

実行例。

```bash
[(0, ['GigabitEthernet3', 'counters', 'out_pkts']),
 (0, ['GigabitEthernet4', 'counters', 'out_pkts']),
 (0, ['Loopback0', 'counters', 'out_pkts'])]
```

Gig3とGig4とLo0が送信パケット数ゼロ(out_pkts==0)ということがわかります。

<br><br>

### ex41.learn_find.py

<p>
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/ex41.learn_find.py" target="_blank">source</a>]　
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/output/ex41.log" target="_blank">log</a>]
</p>

もう少し実践的な例です。

oper_statusがupのインタフェースを探す場合はこうします。

```python
req = R(['info', '(.*)', 'oper_status', 'up'])
intf_up = find(intf, req, filter_=False)
print('up interfaces')
pprint(intf_up)
```

duplexがfullのインタフェースを探す場合はこうします。

```python
req2 = R(['info', '(.*)', 'duplex_mode', 'full'])
intf_full = find(intf, req2, filter_=False)
print('full duplex interfaces')
pprint(intf_full)
```

oper_statusがupで、かつ、duplexがfullのインタフェースを探すにはこうします。
`(.*)`という指定で既に使っていましたが、キーには正規表現が使えます。

```python
req3 = [
    R(['info', '(?P<interface>.*)', 'oper_status', 'up']),
    R(['info', '(?P<interface>.*)', 'duplex_mode', 'full'])
]
intf_up_full = find(intf, *req3, filter_=False)
print("up and full duplex interfaces")
pprint(intf_up_full)
```

<br><br>

### ex42.learn_find.py

<p>
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/ex42.learn_find.py" target="_blank">source</a>]　
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/output/ex42.log" target="_blank">log</a>]
</p>


stpでブロックポートがどこにあるのかを見つける例です。

全てのスイッチを順番に接続して、`stp`を指定して学習させます。

学習結果を一つの辞書型に格納しておきます。
その辞書型に対してこのような探索をかけると全てのブロックポートを見つけることができます。

```python
from pyats.utils.objects import R, find
req = R(['(.*)', 'info', 'pvst', 'default', 'vlans', '(.*)', 'interfaces', '(.*)', 'port_state', 'blocking'])
found = find(learnt, req, filter_=False)
```

実行結果。

sw3のe0/2とsw4のe0/1、sw4のe0/0がブロックポートになっていることがわかります。
手作業で探すと大変ですが、いとも簡単に見つけることができます。

```bash
found blocking port
sw3 Ethernet0/2
sw4 Ethernet0/1
sw4 Ethernet0/0
```

<br><br>

### ex43.learn_poll.py

<p>
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/ex43.learn_poll.py" target="_blank">source</a>]　
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/output/ex43.log" target="_blank">log</a>]
</p>

学習した状態が特定の条件を満たすまで、定期的に学習を続ける例です。

ここでは「upしているインタフェースが少なくとも１つある」という条件を満たすまで、5秒間隔で3回、繰り返し学習します。

```python
# verify at least one interface is up, or raise Exception
def verify_interface_status(obj):
    # make sure interface has learnt
    assert obj.info
    for name in obj.info.keys():
        oper_status = obj.info[name].get('oper_status', None)
        if oper_status == 'up':
            print("verified successfully")
            return

    raise Exception("Could not find any up interface")


intf = Interface(device=uut)
try:
    intf.learn_poll(verify=verify_interface_status, sleep=5, attempt=3)
except StopIteration as e:
    print(e)
```

verify=で渡す関数において例外をraiseすれば条件を満たしていないと判断され、繰り返し学習を継続します。

<br><br>

### ex50.configure.py

<p>
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/ex50.configure.py" target="_blank">source</a>]　
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/output/ex50.log" target="_blank">log</a>]
</p>

装置に設定を投げ込む例です。

コピー＆ペーストでターミナルに貼り付ける感覚で使えます。

```python
output = uut.configure('''
interface Gig1
description "configured by pyats"
exit
interface Gig2
description "configured by pyats"
exit
''')
```

実行例。config termは自動で打ち込まれます。最後のendも自動で打ち込まれます。

```bash
r1#

2022-10-17 18:48:16,073: %UNICON-INFO: +++ r1 with via 'console': configure +++
config term
Enter configuration commands, one per line.  End with CNTL/Z.
r1(config)#
r1(config)#interface Gig1
r1(config-if)#description "configured by pyats"
r1(config-if)#exit
r1(config)#interface Gig2
r1(config-if)#description "configured by pyats"
r1(config-if)#exit
r1(config)#end
r1#
('\r\n'
 'interface Gig1\r\n'
 'description "configured by pyats"\r\n'
 'exit\r\n'
 'interface Gig2\r\n'
 'description "configured by pyats"\r\n'
 'exit\r\n')
```

<br><br>

### ex51.configure.py

<p>
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/ex51.configure.py" target="_blank">source</a>]　
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/output/ex51.log" target="_blank">log</a>]
</p>

Genieが備えているオブジェクトに設定を行い、投入すべきコマンドを機械的に生成させる例です。

設定用のInterfaceオブジェクトを作成して、そのオブジェクトに設定を仕込んでいきます。
build_config()でその装置に投入すべきコンフィグが作成されます。

```python
from genie.conf.base import Interface

gig1 = Interface(device=uut, name='GigabitEthernet1')
gig2 = Interface(device=uut, name='GigabitEthernet2')
gig3 = Interface(device=uut, name='GigabitEthernet3')
gig4 = Interface(device=uut, name='GigabitEthernet4')
gig1.description = "configured by Genie Conf Object"
gig2.description = "configured by Genie Conf Object"
gig3.description = "configured by Genie Conf Object"
gig4.description = "configured by Genie Conf Object"

# verify config
print(gig1.build_config(apply=False))
print(gig2.build_config(apply=False))
print(gig3.build_config(apply=False))
print(gig4.build_config(apply=False))

# apply config
gig1.build_config(apply=True)
gig2.build_config(apply=True)
gig3.build_config(apply=True)
gig4.build_config(apply=True)
```

実行例。

build_config()するたびに設定を投入していることがわかります。
投入すべきコマンドをひとまとめにして、一気に投入した方がよいかもしれません。

```bash
r1#
interface GigabitEthernet1
 description configured by Genie Conf Object
 exit
interface GigabitEthernet2
 description configured by Genie Conf Object
 exit
interface GigabitEthernet3
 description configured by Genie Conf Object
 exit
interface GigabitEthernet4
 description configured by Genie Conf Object
 exit

2022-10-17 18:52:51,428: %UNICON-INFO: +++ r1 with via 'console': configure +++
config term
Enter configuration commands, one per line.  End with CNTL/Z.
r1(config)#interface GigabitEthernet1
r1(config-if)# description configured by Genie Conf Object
r1(config-if)# exit
r1(config)#end
r1#

2022-10-17 18:52:52,143: %UNICON-INFO: +++ r1 with via 'console': configure +++
config term
Enter configuration commands, one per line.  End with CNTL/Z.
r1(config)#interface GigabitEthernet2
r1(config-if)# description configured by Genie Conf Object
r1(config-if)# exit
r1(config)#end
r1#

2022-10-17 18:52:52,857: %UNICON-INFO: +++ r1 with via 'console': configure +++
config term
Enter configuration commands, one per line.  End with CNTL/Z.
r1(config)#interface GigabitEthernet3
r1(config-if)# description configured by Genie Conf Object
r1(config-if)# exit
r1(config)#end
r1#

2022-10-17 18:52:53,553: %UNICON-INFO: +++ r1 with via 'console': configure +++
config term
Enter configuration commands, one per line.  End with CNTL/Z.
r1(config)#interface GigabitEthernet4
r1(config-if)# description configured by Genie Conf Object
r1(config-if)# exit
r1(config)#end
r1#

2022-10-17 18:52:54,270: %UNICON-INFO: +++ r1 with via 'console': configure +++
config term
Enter configuration commands, one per line.  End with CNTL/Z.
r1(config)#interface GigabitEthernet1
r1(config-if)# no description configured by Genie Conf Object
r1(config-if)# exit
r1(config)#end
```

<br><br>

### ex52.configure.py

<p>
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/ex52.configure.py" target="_blank">source</a>]　
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/output/ex52.log" target="_blank">log</a>]
</p>

スタティックルーティングを設定する例です。

```python
from genie.libs.conf.static_routing.static_routing import StaticRouting

static_routing = StaticRouting()

static_routing.device_attr[uut].vrf_attr['default'].address_family_attr['ipv4'].route_attr['10.10.10.0/24'].interface_attr['GigabitEthernet1'].if_nexthop = '192.168.12.2'
```

<br><br>

### ex53.configure.py

<p>
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/ex53.configure.py" target="_blank">source</a>]　
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/output/ex53.log" target="_blank">log</a>]
</p>

OSPFを設定する例です。

```python
# create Ospf object
ospf1 = Ospf()

# add configurations to vrf default
ospf1.device_attr[uut].vrf_attr[vrf0].instance = '1'
ospf1.device_attr[uut].vrf_attr[vrf0].router_id = '192.168.255.1'
ospf1.device_attr[uut].vrf_attr[vrf0].area_attr['0'].interface_attr[gig1].if_cost = 10
ospf1.device_attr[uut].vrf_attr[vrf0].area_attr['0'].interface_attr[gig1].if_type = 'point-to-point'
```

<br><br>

### ex54.configure.py

<p>
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/ex54.configure.py" target="_blank">source</a>]　
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/output/ex54.log" target="_blank">log</a>]
</p>

いろいろ実験しているうちにr1の設定が消えてしまったので、pyATSで投入する例を作りました。
CDPを設定して、インタフェースを設定して、OSPFを設定します。

実行例。

```bash
2022-10-17 18:59:39,820: %UNICON-INFO: +++ r1 with via 'console': configure +++
config term
Enter configuration commands, one per line.  End with CNTL/Z.
r1(config)#
r1(config)#cdp run
r1(config)#interface Gig1
r1(config-if)#cdp enable
r1(config-if)#exit
r1(config)#interface Gig2
r1(config-if)#cdp enable
r1(config-if)#exit
r1(config)#end
r1#
('\r\n'
 'cdp run\r\n'
 'interface Gig1\r\n'
 'cdp enable\r\n'
 'exit\r\n'
 'interface Gig2\r\n'
 'cdp enable\r\n'
 'exit\r\n')

2022-10-17 18:59:41,134: %UNICON-INFO: +++ r1 with via 'console': configure +++
config term
Enter configuration commands, one per line.  End with CNTL/Z.
r1(config)#interface Loopback0
r1(config-if)# ip address 192.168.255.1 255.255.255.255
r1(config-if)# no shutdown
r1(config-if)# exit
r1(config)#end
r1#

2022-10-17 18:59:41,935: %UNICON-INFO: +++ r1 with via 'console': configure +++
config term
Enter configuration commands, one per line.  End with CNTL/Z.
r1(config)#interface GigabitEthernet1
r1(config-if)# description to r2
r1(config-if)# ip address 192.168.12.1 255.255.255.0
r1(config-if)# mtu 9000
r1(config-if)# no shutdown
r1(config-if)# exit
r1(config)#end
r1#

2022-10-17 18:59:42,906: %UNICON-INFO: +++ r1 with via 'console': configure +++
config term
Enter configuration commands, one per line.  End with CNTL/Z.
r1(config)#interface GigabitEthernet2
r1(config-if)# description to r3
r1(config-if)# ip address 192.168.13.1 255.255.255.0
r1(config-if)# mtu 9000
r1(config-if)# no shutdown
r1(config-if)# exit
r1(config)#end
r1#
('router ospf 1\n'
 ' router-id 192.168.255.1\n'
 ' network 192.168.12.1 0.0.0.0 area 0\n'
 ' network 192.168.13.1 0.0.0.0 area 0\n'
 ' network 192.168.255.1 0.0.0.0 area 0\n'
 ' exit\n'
 'interface GigabitEthernet1\n'
 ' ip ospf cost 100\n'
 ' ip ospf network point-to-point\n'
 ' exit\n'
 'interface GigabitEthernet2\n'
 ' ip ospf cost 100\n'
 ' ip ospf network point-to-point\n'
 ' exit')

2022-10-17 18:59:44,312: %UNICON-INFO: +++ r1 with via 'console': configure +++
config term
Enter configuration commands, one per line.  End with CNTL/Z.
r1(config)#router ospf 1
r1(config-router)# router-id 192.168.255.1
r1(config-router)# network 192.168.12.1 0.0.0.0 area 0
r1(config-router)# network 192.168.13.1 0.0.0.0 area 0
r1(config-router)# network 192.168.255.1 0.0.0.0 area 0
r1(config-router)# exit
r1(config)#interface GigabitEthernet1
r1(config-if)# ip ospf cost 100
r1(config-if)# ip ospf network point-to-point
r1(config-if)# exit
r1(config)#interface GigabitEthernet2
r1(config-if)# ip ospf cost 100
r1(config-if)# ip ospf network point-to-point
r1(config-if)# exit
r1(config)#end
r1#
```

<br><br>

### ex60.diff.py

<p>
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/ex60.diff.py" target="_blank">source</a>]　
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/output/ex60.log" target="_blank">log</a>]
</p>

作業前後のコンフィグで差分を表示する例です。

ここではGig1のOSPFコストを10に変更する作業を実施しています。

実行例。

+記号は増えた行、-記号は削除された行です。

Gig1のコストは、元々100だったのが10に変更されていることがわかります。

```bash
r1#
+Current configuration : 6519 bytes:
-Current configuration : 6520 bytes:
 interface GigabitEthernet1:
+ ip ospf cost 10:
- ip ospf cost 100:
```

<br><br>

### ex61.diff.py

<p>
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/ex61.diff.py" target="_blank">source</a>]　
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/output/ex61.log" target="_blank">log</a>]
</p>

OSPFの全情報を学習させて、作業前後で比較する例です。

実行例を見れば分かると思いますが、そのままではちょっと使えない感じです。
チェックサムとかシーケンス番号は変わって当然なので、そういうのを排除しないと実用できなそうです。

実行例。

```bash
r1#
 info:
  vrf:
   default:
    address_family:
     ipv4:
      instance:
       1:
        areas:
         0.0.0.0:
          database:
           lsa_types:
            1:
             lsas:
              192.168.255.1 192.168.255.1:
               ospfv2:
                body:
                 router:
                  links:
                   192.168.12.0:
                    topologies:
                     0:
-                     metric: 100
+                     metric: 10
                   192.168.255.2:
                    topologies:
                     0:
-                     metric: 100
+                     metric: 10
                header:
-                age: 218
+                age: 2
-                checksum: 0xB20
+                checksum: 0xAE30
-                seq_num: 80000049
+                seq_num: 8000004A
              192.168.255.2 192.168.255.2:
               ospfv2:
                header:
-                age: 1734
+                age: 1743
              192.168.255.3 192.168.255.3:
               ospfv2:
                header:
-                age: 1868
+                age: 1877
              192.168.255.4 192.168.255.4:
               ospfv2:
                header:
-                age: 1787
+                age: 1796
          interfaces:
           GigabitEthernet1:
-           cost: 100
+           cost: 10
-           hello_timer: 00:00:07
+           hello_timer: 00:00:08
           GigabitEthernet2:
-           hello_timer: 00:00:06
+           hello_timer: 00:00:07
          statistics:
-          area_scope_lsa_cksum_sum: 0x012C67
+          area_scope_lsa_cksum_sum: 0x01CF77
-          spf_runs_count: 35
+          spf_runs_count: 36
```

<br><br>

### ex70.save.py

<p>
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/ex70.save.py" target="_blank">source</a>]　
[<a href="https://github.com/takamitsu-iida/pyats-practice/blob/main/output/ex70.log" target="_blank">log</a>]
</p>

学習させた情報をファイルに保管する例です。

保存はこうします。

```python
# learn all interface
intf.learn()

with open(log_file, 'wb') as f:
    f.write(intf.pickle(intf))
```

ファイルから復元するにはこうします。

```python

# load saved data
import pickle
with open(log_file, 'rb') as f:
    loaded = pickle.load(f)
```

<br><br>

# testとjob

検証作業では、OKなのかNGなのか、判定する場面が多々あります。

ルーティングの検証であればPingできることが期待値かもしれませんし、
アクセスリストの検証であればPingに失敗するのが期待値かもしれません。

どういう条件ならOKなのか、をプログラムで記述して、実行結果をわかりやすくまとめてくれるのがaetestです。


aetestを単体で実行してもよいのですが、job形式にしておくと後からブラウザで結果を参照できて便利です。
