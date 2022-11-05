#!/usr/bin/env python

#
# 事前に採取しておいたログをパースする
#

from pprint import pprint

# import Genie
from genie.conf.base import Device

# 'show version' on iosxe

OUTPUT = '''
Cisco IOS XE Software, Version 17.03.04a
Cisco IOS Software [Amsterdam], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 17.3.4a, RELEASE SOFTWARE (fc3)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2021 by Cisco Systems, Inc.
Compiled Tue 20-Jul-21 04:59 by mcpre

ROM: IOS-XE ROMMON

r1 uptime is 1 week, 5 days, 16 hours, 1 minute
Uptime for this control processor is 1 week, 5 days, 16 hours, 3 minutes
System returned to ROM by reload
System image file is "bootflash:packages.conf"
Last reload reason: reload

A summary of U.S. laws governing Cisco cryptographic products may be found at:
http://www.cisco.com/wwl/export/crypto/tool/stqrg.html

If you require further assistance please contact us by sending email to
export@cisco.com.

License Level: ax
License Type: N/A(Smart License Enabled)
Next reload license Level: ax

The current throughput level is 1000 kbps

Smart Licensing Status: UNREGISTERED/No Licenses in Use

cisco CSR1000V (VXE) processor (revision VXE) with 1105173K/3075K bytes of memory.
Processor board ID 934T7HPFN7R
Router operating mode: Autonomous
4 Gigabit Ethernet interfaces
32768K bytes of non-volatile configuration memory.
3012228K bytes of physical memory.
6188032K bytes of virtual hard disk at bootflash:.

Configuration register is 0x2102
'''

# testbedからではなく、デバイスオブジェクトを直接生成する
# nameの指定は必須（名前は何でもよい）
# osの指定はは必須
dev = Device(name='r1', os='iosxe')

# abstractionを設定しないと例外がraiseする
# raise ValueError('Expected device to have custom.abstraction '
dev.custom.setdefault('abstraction', {'order': ['os']})

# outputにテキストを渡してパースする
parsed = dev.parse('show version', output=OUTPUT)

pprint(parsed)
