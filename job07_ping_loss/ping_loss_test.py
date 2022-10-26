#!/usr/bin/env python

#
# このテストで想定している構成図
# https://github.com/takamitsu-iida/pyats-practice/blob/main/img/fig1.PNG
#
# r1-+-(gig1)-r2-(gig2)-+-r4
#    +-(gig2)-r3-(gig2)-+
#
# r1からr4に連続pingを打つ
# r2のgig1をダウンさせてpingのロスを計測
# r2のgig1をアップさせてpingのロスを計測
# r3のgig1をダウンさせてpingのロスを計測
# r3のgig2をアップさせてpingのロスを計測

import logging
import os
import time

from pyats import aetest
from pyats.async_ import pcall
from genie.testbed import load
from genie.utils.timeout import Timeout
from unicon.core.errors import TimeoutError, StateMachineError, ConnectionError

logger = logging.getLogger(__name__)

def here(path=''):
  return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

# pickle directory
pkl_dir = os.path.join(here('.'), 'pkl')

###################################################################
###                  COMMON SETUP SECTION                       ###
###################################################################

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def load_testbed(self, testbed):
        """
        testbedの形式を変換
        """
        assert testbed, 'Testbed is not provided!'
        logger.info('Converting pyATS testbed to Genie Testbed to support pyATS Library features')
        testbed = load(testbed)

        # 親クラスにtestbedを格納（上書き）
        self.parent.parameters.update(testbed=testbed)

    @aetest.subsection
    def create_directory(self):
        # create pkl_dir
        os.makedirs(pkl_dir, exist_ok=True)

    @aetest.subsection
    def connect(self, testbed):
        """
        r1, r2, r3, r4に接続する
        """
        routers = ['r1', 'r2', 'r3', 'r4']
        devices = []

        for router in routers:
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

def ping(dev, source, destination, repeat):
    """
    連続pingを実行して欠けたping数を返却する
    """
    # pingが全部欠損したとすると、repeat * 2秒必要になってしまうが、そんなに待てないので180秒にしておく
    # pingを実行
    parsed = dev.parse(f'ping {destination} source {source} repeat {repeat}', timeout=180)

    # pingパーサーのスキーマはここにある通り
    # https://github.com/CiscoTestAutomation/genieparser/blob/master/src/genie/libs/parser/iosxe/ping.py#L48
    #
    # ping 192.168.255.4 source loopback0 repeat 100
    #
    # {'ping': {'address': '192.168.255.4',
    #         'data_bytes': 100,
    #         'repeat': 100,
    #         'result_per_line': ['!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!',
    #                             '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'],
    #         'source': '192.168.255.1',
    #         'statistics': {'received': 100,
    #                         'round_trip': {'avg_ms': 1, 'max_ms': 3, 'min_ms': 1},
    #                         'send': 100,
    #                         'success_rate_percent': 100.0},
    #         'timeout_secs': 2}}
    send = parsed.q.raw('[ping][statistics][send]')
    received = parsed.q.raw('[ping][statistics][received]')
    loss = send - received
    return loss


def shut(dev, intf_name):
    return shutdown_interface(dev, intf_name, no=False)


def no_shut(dev, intf_name):
    return shutdown_interface(dev, intf_name, no=True)


def shutdown_interface(dev, intf_name, no=False):
    if no:
        cmd = f'interface {intf_name}\nno shutdown'
    else:
        cmd = f'interface {intf_name}\nshutdown'

    dev.configure(cmd)


def run_shut(shut_dev, shut_intf_name, ping_dev, ping_source, ping_destination, ping_repeat):
    time.sleep(1)
    (_, ping_loss) = pcall([shut, ping], iargs=[[shut_dev, shut_intf_name], [ping_dev, ping_source, ping_destination, ping_repeat]])
    return ping_loss


def run_no_shut(shut_dev, shut_intf_name, ping_dev, ping_source, ping_destination, ping_repeat):
    time.sleep(1)
    (_, ping_loss) = pcall([no_shut, ping], iargs=[[shut_dev, shut_intf_name], [ping_dev, ping_source, ping_destination, ping_repeat]])
    return ping_loss


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


# @aetest.loop(device_name=('r2', 'r3'))

@aetest.loop(device_name=('r2',))
class ping_loss_test_class(aetest.Testcase):

    @aetest.test
    def test(self, steps, testbed, device_name):
        """
        途中経路をダウンさせてpingの欠けを数える
        """

        dev = testbed.devices[device_name]
        ping_dev = testbed.devices['r1']

        # devに関して
        with steps.start(dev.name, continue_=True) as dev_step:

            for intf_name in ['GigabitEthernet1', 'GigabitEthernet2']:

                # intf_nameを閉塞する
                with dev_step.start(f'{intf_name} down', continue_=True) as intf_down_step:
                    loss = run_shut(dev, intf_name, ping_dev, 'loopback0', '192.168.255.4', 200)
                    logger.info(loss)
                    print(loss)

                time.sleep(10)

                # intf_nameの閉塞を解除する
                with dev_step.start(f'{intf_name} up', continue_=True) as intf_up_step:
                    run_no_shut(dev, intf_name, ping_dev, 'loopback0', '192.168.255.4', 200)

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

    aetest.main(testbed=args.testbed)
