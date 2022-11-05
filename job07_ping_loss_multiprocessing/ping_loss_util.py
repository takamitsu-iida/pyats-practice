#!/usr/bin/env python

#
# multiprocessingを使ってpingを別プロセスで実行します。
#   pingプロセスは、連続pingを実行します
#   receive()で連続pingが終了するか、タイムアウトを待ちます
#     タイムアウトした場合は、キューをチェックして停止命令が来ていればCtrl-Shift-6を送信して連続pingを止めます
#   並行して動作するメインプロセスでは、別のデバイスに対して何か作業をして、終了したらキューに停止命令を発行します
#

import re
import time

from unicon.core.errors import SubCommandFailure
from genie.utils.timeout import Timeout

#
# pingを実行する関数
# ここから流用
# https://github.com/takamitsu-iida/pyats-practice/blob/main/ex92.ping.py
#
def ping(conn, dev, destination, source='', repeat=10000, duration=2):
    """
    IOSデバイスの連続pingを実行します。pingが終了するまでブロッキングします。

    Parameters
    ----------
    conn : multiprocessing.connection.Connection
        Pipe()で作成したプロセス間通信用コネクション
    dev : genie.libs.conf.device.iosxe.device.Device
        テストベッドのデバイスです
    destination : str
        宛先アドレス 例 192.168.255.4
    source : str, default ''
        送信元アドレスもしくはインタフェース
    repeat : int, default 10000
        連続pingに指定する送信回数
    duration : int, default 2
        pingの停止命令をチェックする間隔（秒）
    """
    if not dev.is_connected():
        return

    if dev.os not in ['ios', 'iosxe', 'iosxr', 'nxos']:
        return

    # 最後の1行とプロンプトを捕捉する場合
    pattern = r'Success +rate +is +(.*)(\r\n|\n|\r)({}#)$'.format(dev.hostname)

    # 連続pingの!!!!の部分も含めて全部捕捉する場合
    # pattern = r'(.*)Success +rate +is +(.*)(\r\n|\n|\r)({}#)$'.format(dev.hostname)

    # 送り込むコマンド
    if source:
        cmd = f'ping {destination} source {source} repeat {repeat}'
    else:
        cmd = f'ping {destination} repeat {repeat}'

    # pingコマンドを送信する
    # sendline()は送信するだけのノンブロッキング処理
    # 出力される応答は別途receive()で取得する
    try:
        dev.sendline(cmd)
    except SubCommandFailure:
        return

    # Success rate...が出力されるまで繰り返しreceive()を発行する
    while True:
        try:
            finished = dev.receive(pattern, timeout=duration) #, search_size=0)
        except SubCommandFailure:
            break
        if finished:
            output = dev.receive_buffer()
            conn.send(output)
            break
        if conn.poll():
            # Ctrl-Shift-6を送信して実行中の処理を停止する
            dev.transmit("\036")


def parse_ping_output(output):
    """
    IOSデバイスの連続pingの結果をパースします。を実行します。

    Parameters
    ----------
    output : str
        出力されたSuccess rate...を含む文字列です。

    Returns
    -------
    parsed : dict
        パースした結果を辞書型で返します。
    """

    pattern = re.compile(
        r'Success +rate +is +(?P<success_percent>\d+) +percent +\((?P<received>\d+)\/(?P<send>\d+)\)(, +round-trip +min/avg/max *= *(?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+) +(?P<unit>\w+))?'
    )

    parsed = {}

    for line in output.splitlines():
        line = line.strip()

        match = pattern.match(line)
        if match:
            group = match.groupdict()

            parsed['success_rate_percent'] = float(group['success_percent'])
            parsed['received'] = int(group['received'])
            parsed['send'] = int(group['send'])

            if group.get('min', None) is not None:
                parsed['min'] = int(group['min'])
                parsed['max'] = int(group['max'])
                parsed['avg'] = int(group['avg'])

                if group['unit'] == 's':
                    parsed['min'] = parsed['min'] * 1000
                    parsed['max'] = parsed['max'] * 1000
                    parsed['avg'] = parsed['avg'] * 1000

    return parsed


def get_ping_loss(output):
    """
    連続pingを実施した結果のテキスト出力から、ロスした個数を調べて返却します

    Args:
        output (str): 連続pingを実行した結果のテキスト出力

    Returns:
        int: 送信数と受信数の差分
    """
    parsed = parse_ping_output(output=output)
    send = parsed['send']
    received = parsed['received']
    return send - received


def get_oper_status(parsed):
    """
    parse('show interface Gigabitethernet1')の辞書型から'oper_status'を抽出して返却する

    Args:
        parsed (dict): parse('show iterface <intf_name>')の結果

    Returns:
        str: 'up'や'down'などの文字列
    """
    # show interface {interface name}パーサーのスキーマはここにある通り
    # https://github.com/CiscoTestAutomation/genieparser/blob/master/src/genie/libs/parser/iosxe/show_interface.py#L222
    #
    # {'GigabitEthernet1': {'arp_timeout': '04:00:00',
    #                     'bandwidth': 1000000,
    #                     'oper_status': 'up', ★これだけを抽出
    oper_status = parsed.q.get_values('oper_status', 0)
    return oper_status


def verify_ospf_neighbor(dev, intf_name, is_exist):
    """
    intf_nameのインタフェース上にOSPFネイバーがis_existの状態になるまで待機する

    Args:
        dev (_type_): テストベッドデバイス
        intf_name (str): インタフェース名
        is_exist (bool): そのインタフェース上にOSPFネイバーがいることを期待するならTrue、いないことを期待するならFalse

    Returns:
        bool: 確認できた場合はTrue、確認できなかったらFalseを返す
    """
    # 上限120秒、10秒待機、タイムアウトを画面表示
    timeout = Timeout(max_time = 120, interval = 10, disable_log = False)
    try:
        while timeout.iterate():
            parsed = dev.parse('show ip ospf neighbor')
            # parsedはこういう形をしている
            #
            # {'interfaces': {'GigabitEthernet1': {'neighbors': {'192.168.255.2': {'address': '192.168.12.2',
            #                                                                      'dead_time': '00:00:37',
            #                                                                      'priority': 0,
            #                                                                      'state': 'FULL/  '
            #                                                                               '-'}}},
            #                 'GigabitEthernet2': {'neighbors': {'192.168.255.3': {'address': '192.168.13.3',
            #                                                                      'dead_time': '00:00:33',
            #                                                                      'priority': 0,
            #                                                                      'state': 'FULL/  '
            #                                                                               '-'}}}}}

            # intf_nameのエントリを取り出す
            filtered = parsed.q.contains(intf_name).reconstruct()

            if is_exist and any(filtered):
                # 存在することを期待していて、エントリが存在する
                break
            if (not is_exist) and (not any(filtered)):
                # 存在しないことを期待していて、エントリが存在しない
                break

            timeout.sleep()

    except TimeoutError:
        return False

    return True

def shut(dev, intf_name):
    """
    指定の名前のインタフェースを閉塞する

    Args:
        dev (_type_): テストベッドデバイス
        intf_name (str): インタフェース名
    """
    time.sleep(1)
    shutdown_interface(dev, intf_name, no=False)


def no_shut(dev, intf_name):
    """
    指定の名前のインタフェースの閉塞を解除する

    Args:
        dev (_type_): テストベッドデバイス
        intf_name (str): インタフェース名
    """
    time.sleep(1)
    shutdown_interface(dev, intf_name, no=True)


def shutdown_interface(dev, intf_name, no=False):
    """_summary_

    Args:
        dev (_type_): テストベッドデバイス
        intf_name (str): インタフェース名
        no (bool, optional): noがTrueの場合、no shutdownを打ち込む。デフォルトはFalse
    """
    if no:
        cmd = f'interface {intf_name}\nno shutdown'
    else:
        cmd = f'interface {intf_name}\nshutdown'
    dev.configure(cmd)
