# 
# this connects to the specified node via IP, then prints every NeighborInfo and PaxCount packet that it hears
# 
import meshtastic.tcp_interface # type: ignore
from meshtastic.serial_interface import SerialInterface # type: ignore
from meshtastic import mesh_pb2, paxcount_pb2, BROADCAST_NUM # type: ignore
from pubsub import pub # type: ignore
from datetime import datetime
import pytz # type: ignore
import time
import csv
# test
#
# replace with your nodes IP
#
nodeip = "10.10.1.205"

def idToHex(nodeId): 
    return '!' + hex(nodeId)[2:]

def GetCurrentTime():
    utcmoment_naive = datetime.utcnow()
    utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
#
# replace with your nodes timezone city
#
    timezones = ['America/Chicago']
    for tz in timezones:
        localDatetime = utcmoment.astimezone(pytz.timezone(tz))
    return localDatetime

def GetNodeName(node_id):
    node_name = hex(node_id)
    hex_id = '!' + hex(node_id)[2:]
    for node in interface.nodes.values():
        if hex_id == node["user"]["id"]:
            node_name = node["user"]["longName"]
    return node_name
    
def onConnection(interface, topic=pub.AUTO_TOPIC):
    print ()
    print ("*          PaxWatcher beta",)
    print ("*          Connected to " + GetNodeName(interface.myInfo.my_node_num))
    print ("*")
    print ("* ", GetCurrentTime(),"*")
    print ("*")
    
def onReceive(packet, interface): 
    if 'decoded' in packet:
        if packet['decoded'].get('portnum') == 'PAXCOUNTER_APP':
            message = paxcount_pb2.Paxcount()
            payload_bytes = packet['decoded'].get('payload', b'')
            message.ParseFromString(payload_bytes)
            paxtotal = message.wifi + message.ble
            print(f"*          {packet['decoded'].get('portnum', 'N/A')} packet")
            print("*          Time:", GetCurrentTime())
            print("*          From:", GetNodeName(packet['from']), "uptime:", message.uptime)
            print(f"*          SNR: {packet['rxSnr']} RSSI: {packet['rxRssi']}")
            print("*          Device count")
            print(f"*          wifi {message.wifi} / BLE: {message.ble} / PAXtotal: {paxtotal}")
            print("*")

interface = meshtastic.tcp_interface.TCPInterface(nodeip)
# interface = SerialInterface()
pub.subscribe(onReceive, 'meshtastic.receive')
pub.subscribe(onConnection, 'meshtastic.connection.established')
while True: time.sleep(10)
interface.close()