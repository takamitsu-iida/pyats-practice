#!/usr/bin/env python

#
# configure static route
#

import argparse

# import Genie
from genie.testbed import load
from genie.libs.conf.static_routing.static_routing import StaticRouting

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        'oper',
        help='add or del static route',
        type=str,
        choices=['add', 'del']
    )

    args, _ = parser.parse_known_args()

    testbed = load('../lab.yml')

    uut = testbed.devices['uut']

    uut.connect(via='console')

    static_routing = StaticRouting()

    ipv4 = static_routing.device_attr[uut].vrf_attr['default'].address_family_attr['ipv4']
    ipv4.route_attr['10.10.10.0/24'].interface_attr['GigabitEthernet1'].if_nexthop = '192.168.12.2'
    ipv4.route_attr['10.10.20.0/24'].interface_attr['GigabitEthernet1'].if_nexthop = '192.168.12.2'
    ipv4.route_attr['10.10.30.0/24'].interface_attr['GigabitEthernet1'].if_nexthop = '192.168.12.2'
    ipv4.route_attr['10.10.40.0/24'].interface_attr['GigabitEthernet1'].if_nexthop = '192.168.12.2'
    ipv4.route_attr['10.10.50.0/24'].interface_attr['GigabitEthernet1'].if_nexthop = '192.168.12.2'

    uut.add_feature(static_routing)

    if args.oper == 'add':
        # add static route
        static_routing.build_config(apply=True)
    else:
        # delete static route
        static_routing.build_unconfig(apply=True)

    # disconnect
    if uut.is_connected():
        uut.disconnect()
