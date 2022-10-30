#!/usr/bin/env python

import datetime
import logging
import os
import shutil

from pprint import pformat, pprint

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

from unicon.core.errors import TimeoutError, StateMachineError, ConnectionError
from pyats import aetest
from pyats.log.utils import banner
from genie.ops.utils import get_ops  # 機種にあったopsクラスを取得する

logger = logging.getLogger(__name__)

# 状態データを保存するディレクトリ
# pickle形式で保存するので、ここでは'pkl'という名前にする
pkl_dir = os.path.join(os.path.dirname(__file__), 'pkl')

# pkl_dirの中に日付のディレクトリを作る
log_dir_name = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
log_dir = os.path.join(pkl_dir, datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))

###################################################################
###                  COMMON SETUP SECTION                       ###
###################################################################

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def create_directory(self):
        """
        保存先のディレクトリ pkl_dir log_dirを作る
        """
        os.makedirs(pkl_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)


    @aetest.subsection
    def create_result_list(self):
        """
        結果を格納するリストを作成する
        """
        results = []

        # 親クラスに格納
        self.parent.parameters.update(results=results)


    @aetest.subsection
    def assert_datafile(self, crc_threshold, targets):
        """
        datafile.ymlが正しくロードされているか確認する

        Args:
            crc_threshold (int): datafile.ymlを参照
            targets (dict): datafile.ymlを参照
        """
        assert crc_threshold is not None, 'crc_threshold not found in datafile'
        logger.info(f'crc_threshold is {crc_threshold}')

        assert targets is not None, 'targets not found in datafile'
        logger.info(pformat(targets))


    @aetest.subsection
    def connect(self, testbed, targets):
        """
        datafile.ymlで指定されたtargets装置に接続します。

        Args:
            testbed (genie.libs.conf.testbed.Testbed): スクリプト実行時に渡されるテストベッド
            targets (dict): 対象とする装置、datafile.yml参照
        """

        # testbedが正しくロードされているか確認する
        assert testbed, 'Testbed is not provided!'

        for name in targets.keys():
            dev = testbed.devices[name]
            if dev.os not in ('ios', 'iosxe', 'iosxr', 'nxos'):
                continue
            try:
                testbed.devices[name].connect(via='console')
            except (TimeoutError, StateMachineError, ConnectionError):
                logger.error(f'Unable to connect to {name}')

        # 接続できた装置の **名前** を取り出す
        connected = [d.name for d in testbed if d.is_connected()]

        # 接続できた装置に関して、テストケースをループ
        aetest.loop.mark(crc_test_class, device_name = connected)


###################################################################
###                     TESTCASES SECTION                       ###
###################################################################

def save(learnt, path):
    """
    dev.learn()の結果をpathで示すファイルに保存する
    """
    if os.path.exists(path):
        os.remove(path)
    with open(path, 'wb') as f:
        f.write(learnt.pickle(learnt))

class crc_test_class(aetest.Testcase):

    @aetest.setup
    def setup(self, testbed, device_name):
        """
        インタフェース情報を学習します。

        Args:
            testbed (genie.libs.conf.testbed.Testbed): スクリプト実行時に渡されるテストベッド
            device_name (str): ループ指定で渡された装置の**名前**
            # device (genie.libs.conf.device.ios.device.Device): ループ指定で渡された装置
        """

        logger.info(banner(f'Learning Interface Information from {device_name}'))

        # テストベッドから装置を取り出す
        device = testbed.devices[device_name]

        # このdeviceの機種にあったInterfaceクラスをロードする
        Interface = get_ops('interface', device)
        intf = Interface(device=device)

        if device.is_connected():
            # 学習
            intf.learn()

            # 学習できたか確認
            assert intf.info

            # クラス変数に保存
            self.interface_info = intf

            # ファイルに保存
            log_path = os.path.join(log_dir, f'{device_name}.pickle')
            save(self.interface_info, log_path)
        else:
            self.failed(f'{device.name} is not connected')


    @aetest.test
    def count_crc(self, steps, device_name, crc_threshold, results):
        """
        学習した情報からCRCエラーの数を集計します。

        Args:
            device_name (str): ループ指定で渡された装置の**名前**
            # device (genie.libs.conf.device.ios.device.Device): ループ指定で渡された装置
            crc_threshold (int, optional): いくつまで許容するかの指定。 Defaults to 0.
            result_list (list): 結果を保存するリスト
        """

        # 集計結果
        table_data = []

        # 学習した情報をループ
        for intf, data in self.interface_info.info.items():

            # 各インタフェースのステップ
            with steps.start(intf, continue_=True) as intf_step:

                # 集計結果の行
                table_row = []
                table_data.append(table_row)

                # countersを取得
                counters = data.get('counters', None)

                # countersがなければテストはSkipped
                if counters is None:
                    table_row.append(device_name)
                    table_row.append(intf)
                    table_row.append('-')
                    table_row.append('Skipped')
                    intf_step.skipped(f'{intf} does not have counters')
                    continue

                # countersから'in_crc_errors'を取り出す
                in_crc_errors = counters.get('in_crc_errors', None)

                if in_crc_errors is None:
                    table_row.append(device_name)
                    table_row.append(intf)
                    table_row.append('-')
                    table_row.append('Skipped')
                    intf_step.skipped(f'{intf} does not have in_crc_errors')
                    continue

                table_row.append(device_name)
                table_row.append(intf)
                table_row.append(str(in_crc_errors))

                if in_crc_errors > crc_threshold:
                    table_row.append('Failed')
                    intf_step.failed(f'{intf} in_crc_errors {in_crc_errors} > {crc_threshold}')
                else:
                    table_row.append('Passed')
                    # passed

        # table_dataのインタフェースの並びがバラバラなのでソートする
        # インタフェースは2列目、つまりインデックスは1
        table_data = sorted(table_data, reverse=False, key=lambda col: col[1])

        # table_dataを格納する
        results.extend(table_data)

        # 表示して確認
        if HAS_TABULATE:
            output = tabulate(table_data, headers=['Device', 'Interface', 'IN_CRC_ERRORS', 'Test'], tablefmt='orgtbl')
        else:
            output = pformat(table_data)

        if __name__ == '__main__':
            print(output)
        logger.info(output)


class result_class(aetest.Testcase):

    @aetest.test
    def show_results(self, results):
        """
        結果を表示します。
        """

        if HAS_TABULATE:
            output = tabulate(results, headers=['Device', 'Interface', 'IN_CRC_ERRORS', 'Test'], tablefmt='orgtbl')
        else:
            output = pformat(results)

        if __name__ == '__main__':
            print(output)
        logger.info(output)


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


    @aetest.subsection
    def archive(self):
        """
        ログファイルをzipで圧縮します。
        """
        # zipファイルアーカイブして
        shutil.make_archive(os.path.join(pkl_dir, log_dir_name), format='zip', root_dir=log_dir)

        # ディレクトリは削除
        shutil.rmtree(log_dir)











#
# スタンドアロンでの実行
#
# python crc_test.py --testbed ../lab.yml
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
