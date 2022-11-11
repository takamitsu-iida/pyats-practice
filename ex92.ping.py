#!/usr/bin/env python

#
# multiprocessingを使ってpingを別プロセスで実行します。
#   pingプロセスは、連続pingを実行します
#   receive()で連続pingが終了するか、タイムアウトを待ちます
#     タイムアウトした場合は、キューをチェックして停止命令が来ていればCtrl-Shift-6を送信して連続pingを止めます
#   並行して動作するメインプロセスでは、別のデバイスに対して何か作業をして、終了したらキューに停止命令を発行します
#

import multiprocessing
import pprint
import re

from multiprocessing import Process, Pipe

# Genieライブラリからテストベッドをロードする関数をインポートします
from genie.testbed import load

# 例外クラスをインポートします
from unicon.core.errors import TimeoutError, StateMachineError, ConnectionError
from unicon.core.errors import SubCommandFailure


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



if __name__ == '__main__':

    import argparse
    import time

    # このスクリプトを実行するときに --testbed を指定することで読み込むテストベッドファイルを切り替えます
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed', help='testbed YAML file', type=str, default='lab.yml')
    args, _ = parser.parse_known_args()


    # テストベッドをロード
    testbed = load(args.testbed)

    # 出力結果を格納する辞書型
    outputs = {}

    # pingを打ち込む装置
    pinger = 'r1'
    pinger = testbed.devices[pinger]

    # 操作対象装置
    target = 'r2'
    target = testbed.devices[target]

    # pingを打ち込む装置に接続
    pinger.connect(log_stdout=False) # pingの応答を画面に表示しない
    target.connect()

    # pingの宛先
    ping_dest = '192.168.255.4'

    # プロセス間通信用のコネクションを作成
    parent_conn, child_conn = Pipe()

    # pingを別プロセスで実行
    p = multiprocessing.Process(name='ping', target=ping, args=(child_conn, pinger, ping_dest))
    p.start()

    # 時間のかかる作業を模擬するために待機
    time.sleep(5)

    # 同時並行してターゲット装置で作業する
    target.execute('show version')

    # 作業が完了したらpingプロセスに停止命令を出す
    # 中身は読まないので、送信する内容はなんでもよい
    parent_conn.send('CTRL-SHIFT-6')

    # pingプロセスの終了を待つ
    p.join()

    # 切断
    pinger.disconnect()
    target.disconnect()

    # pingの出力を取り出す
    if parent_conn.poll():
        output = parent_conn.recv()
        parsed = parse_ping_output(output)
        pprint.pprint(parsed)
