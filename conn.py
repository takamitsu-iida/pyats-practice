#!/usr/bin/python3

from pyats.topology import loader

testbed = loader.load('lab.yml')

# access the devices
print(testbed.devices)

r1 = testbed.devices['r1']
r2 = testbed.devices['r2']

# find links from one device to another
for link in r1.find_links(r2):
    print(repr(link))


# establish basic connectivity
r1.connect()

# issue commands
print(r1.execute('show version'))

#r1.configure('''
#    interface GigabitEthernet1
#        ip address 10.10.10.1 255.255.255.0
#''')

# establish multiple, simultaneous connections
r2.connect(via='console')

# issue commands through each connection separately
print(r2.execute('show version'))
