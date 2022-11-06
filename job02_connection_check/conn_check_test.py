#!/usr/bin/env python

import logging
import re

from pyats import aetest

logger = logging.getLogger(__name__)

###################################################################
###                  COMMON SETUP SECTION                       ###
###################################################################

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def check_topology(self, testbed, ios1_name='r1', ios2_name='r2'):
        """
        テストベッドのトポロジ情報を確認。

        Args:
            testbed (genie.libs.conf.testbed.Testbed): スクリプト実行時に渡されるテストベッド
            ios1_name (str, optional): １つ目の装置。 Defaults to 'r1'.
            ios2_name (str, optional): ２つ目の装置。 Defaults to 'r2'.
        """

        # testbedが正しくロードされているか確認する
        assert testbed, 'Testbed is not provided!'

        ios1 = testbed.devices[ios1_name]
        ios2 = testbed.devices[ios2_name]

        # テストケースでこの変数にアクセスできるようにパラメータに追加
        # このパラメータは関数の引数で取得するか
        # self.parameters['ios1']のようにして取り出します
        self.parent.parameters.update(ios1=ios1, ios2=ios2)

        # テストベッドで記述されているトポロジ情報で、ios1-ios2間にリンクが定義されているかチェック
        # links = ios1.find_links(ios2)
        # assert len(links) >= 1, 'require one link between ios1 and ios2'


    @aetest.subsection
    def establish_connections(self, steps, ios1, ios2):
        """
        対象装置に接続する

        Args:
            steps (_type_): テストステップ
            ios1 (_type_): check_topology()で取り出した１つ目の装置
            ios2 (_type_): check_topology()で取り出した２つ目の装置
        """
        with steps.start(f'Connecting to {ios1.name}'):
            ios1.connect(via='console')

        with steps.start(f'Connecting to {ios2.name}'):
            ios2.connect(via='console')

###################################################################
###                     TESTCASES SECTION                       ###
###################################################################

#
# このテストケースをios1、ios2の順で実施
#
@aetest.loop(device=('ios1', 'ios2'))
class PingTestcase(aetest.Testcase):

    # pingの宛先を２つ指定して、順番に実施
    @aetest.test.loop(destination=('192.168.255.1', '192.168.255.2'))
    def ping(self, device, destination):
        """
        pingで疎通がとれるか確認する。

        Args:
            device (str): デコレータ@aetest.loopで指定したdevice
            destination (str): デコレータ@aetest.test.loopで指定したpinの宛先
        """
        try:
            # uniconのping()を実行
            # セットアップ時にパラメータに埋め込んだ情報を取り出す
            result = self.parameters[device].ping(destination)

            # 引数でtestbedを受け取ってこうすることもできる
            # result = testbed[device].ping(destination)
        except Exception as e:
            message = 'Ping {} from device {} failed with error: {}'.format(destination, device, str(e))
            self.failed(message, goto=['exit'])
        else:
            match = re.search(r'Success rate is (?P<rate>\d+) percent', result)
            success_rate = match.group('rate')
            message = 'Ping {} with success rate of {}%'.format(destination, success_rate)
            logger.info(message)

#####################################################################
####                       COMMON CLEANUP SECTION                 ###
#####################################################################

class CommonCleanup(aetest.CommonCleanup):

    @aetest.subsection
    def disconnect(self, steps, ios1, ios2):
        """
        装置を切断します。

        Args:
            steps (_type_): ステップ。
            ios1 (genie.libs.conf.device.ios.device.Device): １つ目の装置。
            ios2 (genie.libs.conf.device.ios.device.Device): ２つ目の装置。
        """
        with steps.start(f'Disconnecting from {ios1.name}'):
            ios1.disconnect()

        with steps.start('Disconnecting from {ios2.name}'):
            ios2.disconnect()

#
# スタンドアロンで実行する場合
#
# python conn_check_test.py --testbed ../lab.yml
#
if __name__ == '__main__':

    import argparse

    from pyats import topology

    # set logger level
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--testbed',
        dest='testbed',
        help='testbed YAML file',
        type=topology.loader.load,
        default=None,
    )
    args, _ = parser.parse_known_args()

    aetest.main(testbed=args.testbed)
