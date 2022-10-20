# ループの例

# マニュアルから抜粋。
# https://pubhub.devnetcloud.com/media/pyats/docs/aetest/examples.html

# でも、マニュアルに誤記があって、そのままだと動かない。

"""
#
# スタンドアロンで実行する場合
#
python mega_looping.py --testbed ../lab.yml --interfaces="Gig1,Gig2"


#
# ジョブファイルで実行する場合
#
=== mega_looping_job.py
from pyats.easypy import run
def main():
   run('mega_looping.py', interfaces=['Ethernet1/1', 'Ethernet1/2'])
===

pyats run job mega_looping_job.py --testbed-file tb.yaml
"""

import logging
from pyats import aetest

logger = logging.getLogger(__name__)

# static variable
# VLANS = list(range(1, 4096))
VLANS = list(range(1, 10))

class CommonSetup(aetest.CommonSetup):

    #
    # このサブセクションは最初に一度だけ実行
    #

    @aetest.subsection
    def check_testbed(self, testbed):
        '''
        checking testbed information
        '''

        logger.info('Testbed = %s' % testbed)
        # do some testbed checking
        # ...

    #
    # ループを指定しているのでVLANSの数だけ、このセットアップが走る
    #

    @aetest.subsection.loop(vlan=VLANS)
    def configure_vlan(self, vlan):
        '''
        configure every vlan, each being a subsection
        '''

        logger.info("configuring vlan: %s" % vlan)
        # do the configuration
        # ...

    #
    # このサブセクションでは、loop.mark()を使ってインタフェースの数だけ別のクラスをループさせる
    #

    @aetest.subsection
    def mark_testcase_for_looping(self, interfaces):
        '''
        marking testcase for looping based on script argument interfaces
        '''

        aetest.loop.mark(InterfaceFlapping, interface=interfaces)


class InterfaceFlapping(aetest.Testcase):
    '''
    tests interface flapping, requires parameter 'interface'
    '''

    @aetest.setup
    def setup(self, interface):
        # ここで渡されてくるinterfaceは["gig1", "gig2"]ではない
        # 最初の実行時は"gig1"、次の実行時は"gig2"になる
        logger.info('testing interface: %s' % interface)


    #
    # upとdownで2回実行する
    #
    @aetest.test.loop(status=['up', 'down'])
    def test_status(self, status):
        '''
        check that intf status can be flapped
        '''
        logger.info('configure interface status to: %s' % status)
        # do testing
        # ...


#
# VLANSの要素の数だけ実行される
# いまどの要素なのかを知りたければ、関数の引数でvlanを受け取ればよい
# 実行時に渡した引数もほしければ受け取れる

@aetest.loop(vlan = VLANS)
class Traffic(aetest.Testcase):
    '''
    send traffic on all vlans on all interfaces
    '''

    @aetest.setup
    def setup(self, interfaces):
        '''
        mark traffic test with looping through interfaces
        '''
        logger.info(' '.join(interfaces))

        # ここで関数をループさせているはずなのに、なぜか実行されない
        # aetest.loop.mark(self.test2, interface=interfaces)

        aetest.loop.mark(self.test, interface=interfaces)

    @aetest.test
    def test(self, vlan, interface, interfaces):
        '''
        send traffic to vlan + interface
        '''
        logger.info('interfaces: %s' % ' '.join(interfaces))
        logger.info('interface: %s' % interface)
        logger.info('vlan: %s' % vlan)

        # send traffic
        # ...


class CommonCleanup(aetest.CommonCleanup):

    @aetest.subsection.loop(vlan=VLANS)
    def unconfigure_vlan(self, vlan):
        '''
        unconfigure every vlan, each being a subsection
        '''

        logger.info("unconfiguring vlan: %s" % vlan)
        # do the configuration
        # ...

# main()
if __name__ == '__main__':

    # set logger level
    logger.setLevel(logging.INFO)

    # local imports
    import sys
    import argparse
    from pyats.topology import loader

    parser = argparse.ArgumentParser(description = "standalone parser")
    parser.add_argument('--testbed', dest = 'testbed')
    parser.add_argument('--interfaces', dest = 'interfaces')

    # parse args
    args, sys.argv[1:] = parser.parse_known_args(sys.argv[1:])

    # post-parsing processing
    testbed = loader.load(args.testbed)
    interfaces = args.interfaces.split(',')

    # and pass all arguments to aetest.main() as kwargs
    aetest.main(testbed = testbed, interfaces = interfaces)
