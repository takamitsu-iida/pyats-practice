#!/usr/bin/env python

import logging

from pyats import aetest

logger = logging.getLogger(__name__)

###################################################################
###                  COMMON SETUP SECTION                       ###
###################################################################

class common_setup(aetest.CommonSetup):
    """
    セットアップセクションです。

    デコレータ@aetest.subsectionを付与した関数を作成します。
    関数名は任意で構いません。

    関数は何個作成しても構いません。書いた順番に実行されます。

    関数を超えて値を共有したい場合は、クラス変数に値を格納します。
    """

    @aetest.subsection
    def sample_subsection_1(self):
        """ Common Setup subsection """
        logger.info('aetest common setup 1')

    @aetest.subsection
    def sample_subsection_2(self):
        """ Common Setup subsection """
        logger.info('aetest common setup 2')


###################################################################
###                     TESTCASES SECTION                       ###
###################################################################

#
# テストケース１．
#
class tc_one(aetest.Testcase):
    """テストケース１．

    aetest.Testcaseを継承したクラスであることが重要です。
    クラス名は任意です。

    テストケースは3つのセクションで構成されます。
    1. Setup
    2. Test
    3. Cleanup

    デコレータを付与することで関数の役割が決まります。
    """

    @aetest.setup
    def prepare_testcase(self, section):
        """
        テストケース１．セットアップセクション
        """
        # 引数sectionでセクション名を受け取ります。
        logger.info('TestCase1-Setup')

        # 共通的に使う値はクラス変数に格納しておく
        self.value = 1


    @aetest.test
    def simple_test_1(self):
        """
        テストケース１．テストセクション１．
        """
        logger.info('TestCase1-Test1')

        # PASSする
        assert 1 + 1 == 2
        assert self.value + 1 == 2


    @aetest.test
    def simple_test_2(self):
        """
        テストケース１．テストセクション２．
        """
        logger.info('TestCase1-Test2')

        # PASSする
        self.value += -1
        assert self.value == 0


    @aetest.cleanup
    def clean_testcase(self):
        """
        テストケース１．クリンナップセクション
        """
        logger.info('TestCase1-Cleanup')
        del self.value


#
# テストケース２．
#
class tc_two(aetest.Testcase):
    """
    テストケース２．
    """

    @aetest.test
    def simple_test_1(self):
        """テストケース２．テストセクション１．
        """
        logger.info('TestCase2-Test1')

        # 意図的に失敗させる
        self.failed('This is an intentional failure')


#
# テストケース３．
#
@aetest.loop(a=[2, 3])
class tc_three(aetest.Testcase):
    """
    テストケース３．
    """
    @aetest.test
    @aetest.test.loop(b=[4, 5])
    def simple_test_1(self, a, b):
        """テストケース３．テストセクション１．
        """
        logger.info('TestCase3-Test2')
        logger.info("%s ^ %s = %s" % (a, b, a**b))


#
# テストケース４．
#
class tc_four(aetest.Testcase):

    @aetest.setup
    def prepare_testcase(self):
        # 共通的に使う値はクラス変数に格納しておく
        self.a = [1, 2, 3, 4, 5]
        self.b = [4, 5, 6, 7, 8]

    @aetest.test
    def simple_test_1(self, steps):
        logger.info('TestCase4-Test1')
        for i in self.a:
            with steps.start(f'step for a={i}', continue_=True) as a_step:
                logger.info(f'Current step index: {a_step.index}')
                for j in self.b:
                    with a_step.start(f'step for b={j}', continue_=True) as b_step:
                        logger.info(f'Current step index: {b_step.index}')
                        if i >= j:
                            a_step.failed(f'{i} >= {j}')


#####################################################################
####                       COMMON CLEANUP SECTION                 ###
#####################################################################

class common_cleanup(aetest.CommonCleanup):
    """
    クリンナップセクション
    """

    @aetest.subsection
    def clean_everything(self):
        """
        クリンナップセクション
        """
        logger.info('aetest Common Cleanup')


if __name__ == '__main__':

    result = aetest.main()
    aetest.exit_cli_code(result)
