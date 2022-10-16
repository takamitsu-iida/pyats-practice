#!/usr/bin/env python

from pyats import aetest
from genie.testbed import load

"""
class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def connect_to_device(self, testbed):
        # 渡されたtestbedをGenieのtestbedに変換する
        # testbed = load(testbed)
        # self.parent.parameters.update(testbed=testbed)
        pass
"""

class Testcase1(aetest.Testcase):
    @aetest.test
    def trivial_test(self):
        assert 1 + 1 == 2


class Testcase2(aetest.Testcase):

    @aetest.setup
    def setup(self):
        self.value = 1

    @aetest.test
    def another_trivial_test(self):
        self.value += -1
        assert self.value == 0

    @aetest.cleanup
    def cleanup(self):
        del self.value

@aetest.loop(a=[2, 3])
class Testcase3(aetest.Testcase):

    @aetest.test.loop(b=[8, 9])
    def test(self, a, b):
        print("%s ^ %s = %s" % (a, b, a**b))


class NeilArmstrong(aetest.Testcase):

    # stepsは予約後
    # この関数内でステップを刻む場合に使う
    @aetest.test
    def says(self, steps):

        with steps.start('first step', description = 'this is the first step') as step:
            print('Currnet step index: ', step.index)

        with steps.start('second step', description = 'this is the second step') as step:
            print('Currnet step index: ', step.index)


"""
class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect_from_devices(self, testbed):
        # デバイスから切断する
        pass
"""


# for running as its own executable
if __name__ == '__main__':

    TEST_ARG = False

    if TEST_ARG:
        # 引数あり
        import sys
        import argparse
        from pyats import topology

        # creating our own parser to parse script arguments
        parser = argparse.ArgumentParser(description = "standalone parser")
        parser.add_argument('--testbed', dest = 'testbed', type = topology.loader.load)
        parser.add_argument('--vlan', dest = 'vlan', type = int)

        # do the parsing
        # always use parse_known_args, as aetest needs to parse any
        # remainder arguments that this parser does not understand
        args, sys.argv[1:] = parser.parse_known_args(sys.argv[1:])

        # and pass all arguments to aetest.main() as kwargs
        aetest.main(testbed = args.testbed, vlan=args.vlan)

    else:
        # 引数なし
        aetest.main()
