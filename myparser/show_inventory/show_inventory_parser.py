#
# HOW TO USE THIS LIBRARY
#
# from show_inventory_parser import ShowInventory
#
# show_inv = ShowInventory(device=dev)
# parsed = show_inv.parse()
# print(parsed)

# see pyATS Development Guid
# https://pubhub.devnetcloud.com/media/pyats-development-guide/docs/writeparser/writeparser.html

# see pyATS built in parser source code
# https://github.com/CiscoTestAutomation/genieparser/blob/master/src/genie/libs/parser/iosxe/show_platform.py


import re

from genie.metaparser import MetaParser
from genie.metaparser.util.schemaengine import Optional, Any

# ====================================================
#  Schema for show inventory
# ====================================================
class MyShowInventorySchema(MetaParser):
    """
    Schema for:
        show inventory
    """

    schema = {
        'inventory': {
            Any(): {
                Optional('name'): str,
                Optional('description'): str,
                Optional('pid'): str,
                Optional('vid'): str,
                Optional('serial'): str,
            },
        },
    }


# ================================
# Parser for 'show inventory'
# ================================
class MyShowInventory(MyShowInventorySchema):

    cli_command = 'show inventory'

    def cli(self, output=None):

        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output


        # NAME: "Chassis", DESCR: "Cisco CSR1000V Chassis"
        # PID: CSR1000V          , VID: V00  , SN: 9ZSGNIG46EE

        # NAME: "module R0", DESCR: "Cisco CSR1000V Route Processor"
        # PID: CSR1000V          , VID: V00  , SN: JAB1303001C

        # NAME: "module F0", DESCR: "Cisco CSR1000V Embedded Services Processor"
        # PID: CSR1000V          , VID:      , SN:

        # pattern to capture name and description
        p1 = re.compile(r'\s*NAME\s*:\s*"(?P<name>.*)"\s*,\s*DESCR\s*:\s*"(?P<description>.*)"')

        # pattern to capture product ID, version ID, and serial number.
        p2 = re.compile(r'\s*PID\s*:\s*(?P<pid>\S+)\s*,\s*VID\s*:\s*(?P<vid>.*)\s*,\s*SN\s*:\s*(?P<serial>.*)\s*')

        parsed_dict = {}
        inventory_index = 0

        for line in out.splitlines():
            line = line.strip()

            result = p1.match(line)

            if result:
                # setdefault allows assigned var to set value of key (first arg) in dict
                inventory_dict = parsed_dict.setdefault('inventory',{}) \
                    .setdefault(inventory_index,{})
                group = result.groupdict()

                inventory_dict['name'] = group['name']
                inventory_dict['description'] = group['description']

                continue

            result = p2.match(line)

            if result:
                inventory_dict = parsed_dict.setdefault('inventory',{}) \
                    .setdefault(inventory_index,{})
                group = result.groupdict()

                inventory_dict['pid'] = group['pid']
                inventory_dict['vid'] = group['vid']
                inventory_dict['serial'] = group['serial']

                inventory_index = inventory_index + 1 # move onto next entry

                continue

        return parsed_dict
