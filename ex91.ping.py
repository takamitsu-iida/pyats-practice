#!/usr/bin/env python

#
# 連続pingを実行し、一定時間経過したらCtrl-Shift-6で停止します
#

import pprint
import re

#
# pyATS
#

from genie.testbed import load
from unicon.core.errors import TimeoutError, StateMachineError, ConnectionError
from unicon.core.errors import SubCommandFailure


def ping(dev, destination, source='', repeat=10000, duration=10):
    """
    IOSデバイスの連続pingを実行します。

    Parameters
    ----------
    dev : genie.libs.conf.device.iosxe.device.Device
        テストベッドのデバイスです
    destination : str
        宛先アドレス 例 192.168.255.4
    source : str, default ''
        送信元アドレスもしくはインタフェース
    repeat : int, default 10000
        連続pingに指定する送信回数
    duration : int, default 10
        receive()に渡すタイムアウト値で、タイムアウトしたらCtrl-Shift-6を送信して停止

    Returns
    -------
    output : str or None
        失敗時はNoneを、成功時はreceive()で一致した部分を返却します
    """
    if not dev.is_connected():
        return None

    if dev.os not in ['ios', 'iosxe', 'iosxr', 'nxos']:
        return None

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
    # 出力される応答は別途取得する
    try:
        dev.sendline(cmd)
    except SubCommandFailure:
        return None

    # 最後まで実施してSuccess rate...が出力されるか、もしくはtimeoutになるまで待機する
    # receive() はタイムアウトしても例外を出さないので戻り値の真偽値で結果を判断する
    finished = dev.receive(pattern, timeout=duration) #, search_size=0)
    if finished:
        output = dev.receive_buffer()
        return output

    # まだ連続pingは継続して実行中なのでCtrl-Shift-6を送信して停止する
    dev.transmit("\036")

    # 連続pingが停止するので、プロンプトの受信を待つ
    finished = dev.receive(pattern, timeout=5) #, search_size=0)
    if finished:
        output = dev.receive_buffer()
        return output

    return None


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

    #
    # script args
    #
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed', help='testbed YAML file', type=str, default='lab.yml')
    args, _ = parser.parse_known_args()


    # テストベッドをロード
    testbed = load(args.testbed)

    # 出力結果を格納する辞書型
    outputs = {}

    # 対象装置
    target_routers = ['r1', 'r2']

    for name in target_routers:
        dev = testbed.devices[name]

        # 接続
        try:
            dev.connect(via='console', log_stdout=False)
        except (TimeoutError, StateMachineError, ConnectionError) as e:
            print(e)
            continue

        # 連続pingを10実行して完了
        output = ping(dev, '192.168.255.4', source='loopback0', repeat=10, duration=5)

        # 結果を保存
        outputs[name + '-repeat-10'] = output

        # 連続pingを実行して5秒後に強制停止
        output = ping(dev, '192.168.255.4', source='loopback0', repeat=100000, duration=5)

        # 結果を保存
        outputs[name + '-ctrl-shift-6'] = output

        # 切断
        dev.disconnect()

    # 結果を表示
    for name, output in outputs.items():
        if output is not None:
            print(name)
            print(output)
            parsed = parse_ping_output(output)
            pprint.pprint(parsed)
        print('\n')