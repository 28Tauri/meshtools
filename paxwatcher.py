# 
# this connects to the specified node via IP, 
#  then prints every PaxCount packet to the screen
#  and logs to a csv file
# 
import meshtastic.tcp_interface # type: ignore
from meshtastic.serial_interface import SerialInterface # type: ignore
from meshtastic import mesh_pb2, paxcount_pb2, BROADCAST_NUM # type: ignore
from pubsub import pub # type: ignore
from datetime import datetime
import pytz # type: ignore
import time
import csv
#
# replace with your nodes IP
#
nodeip = "10.10.1.205"
timestamp = int(time.time())
fileprefix = 'pax'

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
    print ("* ", GetCurrentTime())
    print ("*")
    # create a new csv file, named prefix_timestamp (note that timestamp is from runtime not OnConnect)
    with open(
    f'{fileprefix}_{timestamp}.csv', 'w', encoding='utf-8' 
        ) as f:
        f.write('time,from,uptime,snr,wifi,ble,total' + '\n')
    
def onReceive(packet, interface): 
    if 'decoded' in packet:
        if packet['decoded'].get('portnum') == 'PAXCOUNTER_APP':
            message = paxcount_pb2.Paxcount()
            payload_bytes = packet['decoded'].get('payload', b'')
            message.ParseFromString(payload_bytes)
            paxtotal = message.wifi + message.ble
            now_time = GetCurrentTime()
            who_from = GetNodeName(packet['from'])
            # here we build the array for what gets appended to the csv
            add_data = [now_time, who_from, message.uptime, packet['rxSnr'], message.wifi, message.ble, paxtotal]
            # open the file we saved OnConnect, in append mode, and we want newlines after each new tranche of data
            with open(f'{fileprefix}_{timestamp}.csv', 'a', newline='\n') as file:
                writer = csv.writer(file)
                writer.writerow(add_data)
            # also print all that to the screen in a structured format
            print(f"*          {packet['decoded'].get('portnum', 'N/A')} packet")
            print("*          Time:", now_time)
            print("*          From:", who_from, "uptime:", message.uptime)
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