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

# テスト環境に関する情報はdatafile.ymlから読み込みます
# 参考
# https://pubhub.devnetcloud.com/media/pyats/docs/aetest/datafile.html


import logging
import os

from datetime import datetime
from pprint import pformat

# 必要な関数をping_loss_util.pyから取り出す
from ping_loss_util import ping, get_ping_loss, shut, no_shut, verify_ospf_neighbor

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

from unicon.core.errors import TimeoutError, StateMachineError, ConnectionError
from pyats import aetest
from pyats.async_ import pcall


logger = logging.getLogger(__name__)

###################################################################
###                  COMMON SETUP SECTION                       ###
###################################################################

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def assert_datafile(self, pinger, targets):
        """
        datafile.ymlが正しくロードされているか確認する

        Args:
            pinger (dict): datafile.ymlを参照
            targets (dict): datafile.ymlを参照
        """
        assert pinger is not None, 'pinger not found in datafile'
        logger.info(pformat(pinger))

        assert targets is not None, 'targets not found in datafile'
        logger.info(pformat(targets))

        # pingを打ち込むデバイスと、インタフェースを閉塞するデバイスが同じ場合は、違うコネクションを使うような工夫が必要
        assert pinger['from'] not in targets.keys(), 'pinger and target is same host'


    @aetest.subsection
    def connect(self, testbed, pinger, targets):
        """
        datafile.ymlで指定されたデバイスに接続する

        Args:
            testbed (genie.libs.conf.testbed.Testbed): スクリプト実行時に渡されるテストベッド
            pinger (dict): datafile.ymlを参照
            targets (dict): datafile.ymlを参照
        """

        # testbedが正しくロードされているか確認する
        assert testbed, 'Testbed is not provided!'

        # pingデバイスに接続
        ping_dev = testbed.devices[pinger['from']]
        try:
            ping_dev.connect(via='console', log_stdout=False) # 画面に表示しない
        except (TimeoutError, StateMachineError, ConnectionError):
            logger.error(f'Unable to connect to {router}')

        for router in targets.keys():
            r = testbed.devices[router]
            if r.is_connected():
                continue
            try:
                r.connect(via='console')
            except (TimeoutError, StateMachineError, ConnectionError):
                logger.error(f'Unable to connect to {router}')


###################################################################
###                     TESTCASES SECTION                       ###
###################################################################

class ping_loss_test_class(aetest.Testcase):

    @aetest.test
    def test(self, steps, testbed, pinger, targets):
        """途中経路をダウンさせてpingの欠けを数える

        Args:
            steps (_type_): aetestのステップ
            testbed (genie.libs.conf.testbed.Testbed): スクリプト実行時に渡されるテストベッド
            pinger (dict): datafile.ymlで指定したping実行装置
            targets (dict): datafile.ymlで指定した操作対象装置
        """

        # 連続pingの欠損値を保存する入れ物を作成
        self.ping_loss_result = {}

        # 連続pingを実行する装置名、パラメータを取り出す
        ping_from = pinger['from']

        # 連続pingを実行する装置をテストベッドから取り出す
        ping_dev = testbed.devices[ping_from]

        # datafile.ymlで指定した操作対象装置を順番に取り出す
        for target in targets.keys():
            # テストベッドからこの装置を取り出す
            dev = testbed.devices[target]
            with steps.start(dev.name, continue_=False) as dev_step:

                # 連続pingの欠損値を保存する入れ物にこの装置のエントリを作成
                self.ping_loss_result[target] = {}

                # この装置のインタフェースのリストを取り出す
                interfaces = targets[target]['interfaces']
                for intf in interfaces:
                    with dev_step.start(intf, continue_=False) as intf_step:

                        # 連続pingの欠損値を保存する入れ物にこのインタフェースのエントリを作成
                        self.ping_loss_result[target][intf] = {}

                        # 閉塞するステップ
                        with intf_step.start(f'{intf} down', continue_=False) as intf_down_step:

                            # pcallの使い方はここを参照
                            # https://pubhub.devnetcloud.com/media/pyats/docs/async/pcall.html
                            #
                            # この２つの関数を同時に実行する
                            #   def shut(dev, intf_name):
                            #   def ping(dev, destination, repeat=10000, duration=10):
                            # 位置引数はiargs、キーワード引数はikwargsに渡す
                            #
                            # 連続pingをrepeat回数実行、duration秒後にCtrl-Shift-6で停止する
                            (_, ping_result) = pcall(
                                            [shut, ping],
                                            iargs=( (dev, intf), (ping_dev, pinger['to']) ),
                                            ikwargs=( {}, { 'repeat': pinger['repeat'], 'duration': pinger['duration']}) )

                            if ping_result is None:
                                logger.error('ping failed')
                                loss = -1
                            else:
                                logger.info(ping_result)
                                loss = get_ping_loss(ping_result)
                            self.ping_loss_result[target][intf]['down'] = loss

                            if not verify_ospf_neighbor(dev, intf, False):
                                intf_down_step.failed('OSPF neighbor verification failed.')

                        # 閉塞を解除するステップ
                        with intf_step.start(f'{intf} up', continue_=False) as intf_up_step:
                            (_, loss) = pcall(
                                            [no_shut, ping],
                                            iargs=( (dev, intf), (ping_dev, pinger['to']) ),
                                            ikwargs=( {}, { 'repeat': pinger['repeat'], 'duration': pinger['duration']}))

                            if ping_result is None:
                                logger.error('ping failed')
                                loss = -1
                            else:
                                logger.info(ping_result)
                                loss = get_ping_loss(ping_result)
                            self.ping_loss_result[target][intf]['up'] = loss

                            if not verify_ospf_neighbor(dev, intf, True):
                                intf_up_step.failed('OSPF neighbor verification failed.')


    @aetest.test
    def dump_result(self):
        """
        結果を表に変換して保存

        Args:
            ping_loss_result (dict): ping_loss_test_classのテストケースで作成したオブジェクト
        """
        # ping_loss_resultはこんな形をしている
        # {'r2': {'GigabitEthernet1': {'down': 0, 'up': 0},
        #         'GigabitEthernet2': {'down': 0, 'up': 0}},
        #  'r4': {'GigabitEthernet1': {'down': 0, 'up': 0}}}
        output = ''
        if HAS_TABULATE:
            result = []
            for device_name, device_data in self.ping_loss_result.items():
                for intf_name, intf_data in device_data.items():
                    for k, v in intf_data.items():
                        result.append([device_name, intf_name, k, v])
            output = tabulate(result)
        else:
            output = pformat(self.ping_loss_result)

        if __name__ == '__main__':
            print(output)
        logger.info(output)

        log_path = os.path.join(os.path.dirname(__file__), 'result.txt')
        with open(log_path, 'w') as f:
            f.write(datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'))
            f.write('\n')
            f.write(output)


#####################################################################
####                       COMMON CLEANUP SECTION                 ###
#####################################################################

class CommonCleanup(aetest.CommonCleanup):
    """CommonCleanup Section"""

    @aetest.subsection
    def disconnect(self, testbed):
        """
        testbedから全て切断します。

        Args:
            testbed (genie.libs.conf.testbed.Testbed): スクリプト実行時に渡されるテストベッド
        """
        testbed.disconnect()


#
# スタンドアロンでの実行
#
# python ping_loss_test.py --testbed ../lab.yml
#
if __name__ == '__main__':

    import argparse
    import os

    from pyats import topology

    DATAFILE = 'datafile.yml'
    SCRIPT_DIR = os.path.dirname(__file__)
    DATAFILE_PATH = os.path.join(SCRIPT_DIR, DATAFILE)

    # スクリプト実行時に受け取る引数
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--testbed',
        dest='testbed',
        help='testbed YAML file',
        type=topology.loader.load,
        default=None,
    )
    args, _ = parser.parse_known_args()

    # main()に渡す引数
    main_args = {
        'testbed': args.testbed,
    }

    # もしdatafile.ymlがあれば、それも渡す
    if os.path.exists(DATAFILE_PATH):
        main_args.update({'datafile': DATAFILE_PATH})

    aetest.main(**main_args)
