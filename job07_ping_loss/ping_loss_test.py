#!/usr/bin/env python

#
# このテストで想定している構成図
# https://github.com/takamitsu-iida/pyats-practice/blob/main/img/fig1.PNG
#
# r1-+-(gig1)-r2-(gig2)-+-r4
#    +-(gig2)-r3-(gig2)-+
#
# r1からr4に連続pingを打つ
# r2のgig1をダウンさせてpingのロスを計測 (r1->r3->r4に迂回)
# r2のgig1をアップさせてpingのロスを計測 (r1->r2->r4に戻る)
# r2のgig2をダウンさせてpingのロスを計測 (r1->r3->r4に迂回)
# r2のgig2をアップさせてpingのロスを計測 (r1->r2->r4に戻る)

import logging
import os
from pprint import pformat
import re
import time

from unicon.core.errors import SubCommandFailure
from unicon.core.errors import TimeoutError, StateMachineError, ConnectionError
from pyats import aetest
from pyats.async_ import pcall
from genie.testbed import load
from genie.utils.timeout import Timeout

logger = logging.getLogger(__name__)

def here(path=''):
  return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

###################################################################
###                  COMMON SETUP SECTION                       ###
###################################################################

#
# これらモジュールレベルの値は実行時にtestenv.ymlからセットされる
#
pinger: None
targets: None

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def load_testbed(self, testbed):
        """
        testbedの形式を変換する
        """
        assert testbed, 'Testbed is not provided!'
        logger.info('Converting pyATS testbed to Genie Testbed to support pyATS Library features')
        testbed = load(testbed)

        # 親クラスにtestbedを格納（上書き）
        self.parent.parameters.update(testbed=testbed)


    @aetest.subsection
    def assert_datafile(self):
        """
        testenv.ymlが正しくロードされているか確認する
        """
        assert pinger, 'pinger not found'
        logger.info(pformat(pinger))

        assert targets, 'targets not found'
        logger.info(pformat(targets))


    @aetest.subsection
    def connect(self, testbed):
        """
        testenvで指定されたデバイスに接続する
        """
        devices = []
        for router in targets.keys():
            r = testbed.devices[router]
            try:
                r.connect(via='console')
                devices.append(r)
            except (TimeoutError, StateMachineError, ConnectionError):
                logger.error(f'Unable to connect to {router}')

        # 親クラスにdevicesを格納して後続のテストで利用できるようにする
        self.parent.parameters.update(devices=devices)


###################################################################
###                     TESTCASES SECTION                       ###
###################################################################

#
# pingを実行する関数
# ここから流用
# https://github.com/takamitsu-iida/pyats-practice/blob/main/ex91.ping.py
#
def ping(dev, destination, repeat=10000, duration=10):
    """
    IOSデバイスの連続pingを実行します。

    Parameters
    ----------
    dev : genie.libs.conf.device.iosxe.device.Device
        テストベッドのデバイスです
    destination : str
        宛先アドレス 例 192.168.255.4
    repeat : int, default 10000
        連続pingに指定する送信回数
    duration : int, default 10
        指定した秒数が経過したらCtrl-Shift-6で停止します

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

    # pingコマンドを送信する
    # 出力される応答は別途取得する
    try:
        dev.sendline(f'ping {destination} repeat {repeat}')
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


def get_ping_loss(output):
    """
    連続pingを実施した結果のテキスト出力から、ロスした個数を調べて返却します
    """
    parsed = parse_ping_output(output=output)
    send = parsed['send']
    received = parsed['received']
    return send - received


def get_oper_status(parsed):
    """
    parse('show interface Gigabitethernet1')の結果から'oper_statu'を抽出して返却する
    """
    # show interface {interface name}パーサーのスキーマはここにある通り
    # https://github.com/CiscoTestAutomation/genieparser/blob/master/src/genie/libs/parser/iosxe/show_interface.py#L222
    #
    # {'GigabitEthernet1': {'arp_timeout': '04:00:00',
    #                     'bandwidth': 1000000,
    #                     'oper_status': 'up', ★これだけを抽出
    oper_status = parsed.q.get_values('oper_status', 0)
    return oper_status


def check_ospf_neighbor(dev, intf_name):
    """
    intf_nameのインタフェース上にOSPFネイバーがいればTrueを返す
    """
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

    # intf_nameが存在するかどうかを返却する
    filtered = parsed.q.contains(intf_name).reconstruct()
    return any(filtered)


def shut(dev, intf_name):
    time.sleep(1)
    return shutdown_interface(dev, intf_name, no=False)


def no_shut(dev, intf_name):
    time.sleep(1)
    return shutdown_interface(dev, intf_name, no=True)


def shutdown_interface(dev, intf_name, no=False):
    if no:
        cmd = f'interface {intf_name}\nno shutdown'
    else:
        cmd = f'interface {intf_name}\nshutdown'
    dev.configure(cmd)


@aetest.loop(device_name=('r2',))
class ping_loss_test_class(aetest.Testcase):

    @aetest.test
    def test(self, steps, testbed, device_name):
        """
        途中経路をダウンさせてpingの欠けを数える
        """

        # device_nameはデコレータでループ指定した値
        dev = testbed.devices[device_name]

        # pingを実施するために乗り込む装置
        # ここではr1
        ping_dev = testbed.devices['r1']

        # devに関してのステップ
        with steps.start(dev.name, continue_=True) as dev_step:

            # ダウン・アップさせる対象インタフェース
            for intf_name in ['GigabitEthernet1', 'GigabitEthernet2']:

                # intf_nameを閉塞するステップ
                with dev_step.start(f'{intf_name} down', continue_=True) as intf_down_step:
                    # pcallの使い方はここを参照
                    # https://pubhub.devnetcloud.com/media/pyats/docs/async/pcall.html
                    #
                    # この２つの関数を同時に実行する
                    #   def shut(dev, intf_name):
                    #   def ping(dev, destination, repeat=10000, duration=10):
                    (_, loss) = pcall(
                                    [shut, ping],
                                    iargs=( (dev, intf_name), (ping_dev, '192.168.255.4') ),
                                    ikwargs=( {}, {'duration': 30}) )
                    logger.info(loss)

                time.sleep(10)

                # intf_nameの閉塞を解除するステップ
                with dev_step.start(f'{intf_name} up', continue_=True) as intf_up_step:
                    #
                    # この２つの関数を同時に実行する
                    #   def no_shut(dev, intf_name):
                    #   def ping(dev, destination, repeat=10000, duration=10):
                    (_, loss) = pcall(
                                    [no_shut, ping],
                                    cargs=(dev),
                                    iargs=( (dev, intf_name), (ping_dev, '192.168.255.4') ),
                                    ikwargs=( {}, {'duration': 30}))

                time.sleep(10)

#####################################################################
####                       COMMON CLEANUP SECTION                 ###
#####################################################################

class CommonCleanup(aetest.CommonCleanup):
    """CommonCleanup Section"""

    @aetest.subsection
    def disconnect(self, testbed):
        # testbedそのものから切断
        testbed.disconnect()

#
# stand-alone test
#
if __name__ == "__main__":

    # python ping_loss_test.py --testbed ../lab.yml

    import argparse
    from pyats import topology

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--testbed',
        dest='testbed',
        help='testbed YAML file',
        type=topology.loader.load,
        default=None,
    )

    # parse command line arguments only we know
    args, _ = parser.parse_known_args()

    testenv_path = os.path.join(here('.'), 'testenv.yml')

    aetest.main(testbed=args.testbed, datafile=testenv_path)
