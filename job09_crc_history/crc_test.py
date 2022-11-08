#!/usr/bin/env python

import logging
import os

from datetime import datetime
from pprint import pformat

# db_util.pyから関数を取り出す
from db_util import insert_intf_info, get_intf_info_by_name

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

#
# このテストを実行した時点の共通のタイムスタンプ
#
TIMESTAMP = datetime.now().timestamp()

###################################################################
###                  COMMON SETUP SECTION                       ###
###################################################################

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def create_result_list(self):
        """
        結果を格納する**辞書型**を作成する
        """
        results = {}

        # 親クラスに格納
        self.parent.parameters.update(results=results)


    @aetest.subsection
    def assert_datafile(self, max_history, crc_threshold, targets):
        """
        datafile.ymlが正しくロードされているか確認する

        Args:
            max_history (int): datafile.ymlを参照
            crc_threshold (int): datafile.ymlを参照
            targets (dict): datafile.ymlを参照
        """
        assert max_history is not None, 'max_history not found in datafile'
        logger.info(f'max_history is {max_history}')

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
            targets (dict): 対象装置、datafile.yml参照
        """

        # testbedが正しくロードされているか確認する
        assert testbed, 'Testbed is not provided!'

        for name in targets.keys():
            dev = testbed.devices[name]
            if dev.os not in ('ios', 'iosxe', 'iosxr', 'nxos'):
                continue
            try:
                testbed.devices[name].connect()
            except (TimeoutError, StateMachineError, ConnectionError):
                logger.error(f'Unable to connect to {name}')

        # 接続できた装置の **名前** を取り出す
        connected = [d.name for d in testbed if d.is_connected()]

        # 接続できた装置に関して、テストケースをループ
        aetest.loop.mark(crc_test_class, device_name=connected)


###################################################################
###                     TESTCASES SECTION                       ###
###################################################################

class crc_test_class(aetest.Testcase):

    @aetest.setup
    def setup(self, testbed, device_name, max_history):
        """
        インタフェース情報を学習します。

        Args:
            testbed (genie.libs.conf.testbed.Testbed): スクリプト実行時に渡されるテストベッド
            device_name (str): ループ指定で渡された装置の**名前**
        """

        logger.info(banner(f'Learning Interface Information from {device_name}'))

        # テストベッドから装置を取り出す
        device = testbed.devices[device_name]

        # このdeviceの機種にあったInterfaceクラスをロードする
        Interface = get_ops('interface', device)
        intf = Interface(device=device)

        # 学習
        intf.learn()

        # 学習できたことを確認
        assert intf.info

        # データベースにタイムスタンプとともに保存
        insert_intf_info(device_name, intf.info, TIMESTAMP, max_history=max_history)


    @aetest.test
    def count_crc(self, steps, device_name, crc_threshold, results):
        """
        データベースに保存されている情報からCRCエラーの数を集計します。

        Args:
            steps: ステップ
            device_name (str): ループ指定で渡された装置の**名前**
            crc_threshold (int, optional): いくつまで許容するかの指定、datafile.yml参照
            results (dict): 結果を保存する辞書型、セットアップで作成したスクリプトレベルのパラメータ
        """

        # 集計結果
        table_data = []

        # device_nameのデータをデータベースから取得
        # これは古い順に並んでいる
        hist_list = get_intf_info_by_name(device_name)

        # 取り出したデータのタイムスタンプのリスト
        ts_list = [d['timestamp'] for d in hist_list]

        # datetimeのリスト
        datetime_list = [datetime.fromtimestamp(ts) for ts in ts_list]

        # 分かりやすく日付の文字列に変換
        date_list = [dt.strftime("%Y-%m-%d %H:%M:%S") for dt in datetime_list]

        # 一番古いデータのintf_infoを取り出して、インタフェース名でループを回す
        for intf in hist_list[0]['intf_info'].keys():

            # 各インタフェースのステップ
            with steps.start(intf, continue_=True) as intf_step:

                # 集計結果の行を作成して追加
                table_row = []
                table_data.append(table_row)

                # 装置名を追加
                table_row.append(device_name)

                # インタフェース名を追加
                table_row.append(intf)

                # countersを過去情報から取得
                crc_errors = []
                for hist_data in hist_list:
                    # 'intf_info'キーを取り出す
                    intf_info = hist_data['intf_info']

                    # 'counters'キーを取り出す
                    counters = intf_info[intf].get('counters', None)
                    if counters is None:
                        crc_errors.append('-')
                        continue

                    # countersから'in_crc_errors'を取り出す
                    in_crc_errors = counters.get('in_crc_errors', None)
                    if in_crc_errors is None:
                        crc_errors.append('-')
                        continue

                    crc_errors.append(in_crc_errors)

                table_row.extend(crc_errors)

                if '-' in crc_errors:
                    intf_step.skipped(f'{intf} does not have in_crc_errors counter')
                    table_row.append('Skipped')
                else:
                    min_crc = min(crc_errors)
                    max_crc = max(crc_errors)
                    if max_crc - min_crc > crc_threshold:
                        intf_step.failed(f'{intf} in_crc_errors {in_crc_errors} > {crc_threshold}')
                        table_row.append('Failed')
                    else:
                        table_row.append('Passed')

        # table_dataのインタフェースの並びがバラバラなのでソートする
        # インタフェースは2列目、つまりインデックスは1
        table_data = sorted(table_data, reverse=False, key=lambda col: col[1])

        # ヘッダ
        # | device | intf | 日付 | 日付 |... | test |
        headers = ['device', 'intf']
        headers.extend(date_list)
        headers.append('test')

        # resultsに格納する
        results[device_name] = {'headers': headers, 'table': table_data}

        # 表示して確認
        if HAS_TABULATE:
            output = tabulate(table_data, tablefmt='orgtbl', headers=headers)
        else:
            output = pformat(table_data)

        logger.info(output)


class result_class(aetest.Testcase):

    @aetest.test
    def show_results(self, results):
        """
        まとめて結果を表示します。
        """

        output = ''
        for value in results.values():
            output += '\n'
            if HAS_TABULATE:
                output += tabulate(value['table'], tablefmt='orgtbl', headers=value['headers'])
            else:
                output += pformat(value['table'])
            output += '\n'

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


#
# スタンドアロンでの実行
#
# python crc_test.py --testbed ../lab.yml
#
if __name__ == '__main__':

    import argparse
    import os

    from pyats import topology

    # set logger level
    logger.setLevel(logging.INFO)

    DATAFILE = 'datafile.yml'
    SCRIPT_DIR = os.path.dirname(__file__)
    DATAFILE_PATH = os.path.join(SCRIPT_DIR, DATAFILE)

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
