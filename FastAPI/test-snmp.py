from pysnmp.hlapi import *

def get_dlink_switch_ports(ip, community):
    ports = {}
    errorIndication, errorStatus, errorIndex, varBinds = next(
        bulkCmd(SnmpEngine(),
                CommunityData(community),
                UdpTransportTarget((ip, 161)),
                ContextData(),
                0, 25,  # starting from OID 0, retrieve 25 variables at a time
                ObjectType(ObjectIdentity('DLink-MIB', 'dlinkPortDescr')),
                ObjectType(ObjectIdentity('DLink-MIB', 'dlinkPortOperStatus')))
    )

    if errorIndication:
        print(errorIndication)
    else:
        if errorStatus:
            print(f'{errorStatus.prettyPrint()} at {errorIndex}')
        else:
            for varBind in varBinds:
                oid, value = varBind
                dlinkPortDescr = value[0]
                dlinkPortOperStatus = value[1]
                ports[oid] = {'dlinkPortDescr': dlinkPortDescr, 'dlinkPortOperStatus': dlinkPortOperStatus}

    return ports

switch_ip = '192.168.2.23'
community_string = 'public'

dlink_switch_ports = get_dlink_switch_ports(switch_ip, community_string)

for oid, port_info in dlink_switch_ports.items():
    dlinkPortDescr = port_info['dlinkPortDescr']
    dlinkPortOperStatus = port_info['dlinkPortOperStatus']
    print(f"Port: {dlinkPortDescr}, Status: {dlinkPortOperStatus}")
